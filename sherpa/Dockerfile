FROM python:3.12-slim

# 设置非交互式环境（避免安装过程中询问时区等问题）
# export DEBIAN_FRONTEND=noninteractive
ENV DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /workspace

# 安装基础编译工具链
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    wget \
    portaudio19-dev \
    git-lfs \
    build-essential \
    vim \
    python3-pip \
    cmake \
    ca-certificates && \
    # 清理缓存以减小镜像体积
    apt-get clean && \
    # pip3 install onnxruntime setuptools gradio sounddevice && \
    rm -rf /var/lib/apt/lists/*

# Clone the repository
RUN git lfs install
RUN git clone https://github.com/k2-fsa/sherpa-onnx

# 设置默认工作目录
WORKDIR /workspace/sherpa-onnx

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Download and extract the model
ARG MODEL_URL="https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20.tar.bz2"
ARG MODEL_DIR="sherpa-onnx-streaming-zipformer-model"
RUN wget ${MODEL_URL} -O model.tar.bz2 && \
    tar -xvf model.tar.bz2 -C ./ && \
    rm model.tar.bz2
RUN mv sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20 ${MODEL_DIR}


RUN export SHERPA_ONNX_CMAKE_ARGS="-DSHERPA_ONNX_ENABLE_GPU=ON" 

RUN python3 setup.py install

EXPOSE 8989

# 指定默认命令（按需修改）
CMD ["/bin/bash"]
