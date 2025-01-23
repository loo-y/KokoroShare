#!/bin/bash

# 检查并安装 git
if ! command -v git &> /dev/null
then
    echo "git is not installed. Attempting to install..."
    apt-get update
    apt-get install -y git
    if [ $? -ne 0 ]; then
        echo "Failed to install git. Please install it manually and run this script again."
        exit 1
    fi
    echo "git installed successfully."
fi

# 检查并安装 pip
if ! command -v pip &> /dev/null
then
    echo "pip is not installed. Attempting to install..."
    apt-get update
    apt-get install -y python3-pip
    if [ $? -ne 0 ]; then
        echo "Failed to install pip. Please install it manually and run this script again."
        exit 1
    fi
    echo "pip installed successfully."
fi

# 检查 Python 版本是否大于等于 3.10
if ! python3 -c "import sys; assert sys.version_info >= (3, 10)" 2>/dev/null; then
    echo "Python 3.10 or higher is not installed. Attempting to install Python 3.12..."
    apt-get update
    apt-get install -y python3.12 python3.12-dev
    if [ $? -ne 0 ]; then
        echo "Failed to install Python 3.12. Please install it manually and run this script again."
        exit 1
    fi
    
    # 检查是否已经有 pip3.12
    if ! command -v pip3.12 &> /dev/null
    then
        echo "pip3.12 is not installed. Attempting to install..."
        apt-get update
        apt-get install -y python3.12-venv
        python3.12 -m ensurepip
        if [ $? -ne 0 ]; then
            echo "Failed to install pip3.12. Please install it manually and run this script again."
            exit 1
        fi
    fi
    echo "Python 3.12 installed successfully."
     # 使用 pip3.12
    PIP_CMD="pip3.12"
else
    echo "Python 3.10 or higher is installed."
    PIP_CMD="pip3"
fi


# 安装
echo "正在安装装基础编译工具链"
apt-get update
apt-get -qq -y install git wget ortaudio19-dev git-lfs build-essential vim cmake ca-certificates > /dev/null 2>&1
echo "安装完成."

echo "清理缓存以减小镜像体积"
apt-get clean 
rm -rf /var/lib/apt/lists/*


# 克隆仓库
echo "正在克隆 sherpa-onnx 仓库..."
git lfs install
git clone https://github.com/k2-fsa/sherpa-onnx sherpa-onnx
echo "sherpa-onnx 仓库克隆完成."

# 进入仓库目录
cd sherpa-onnx

# 复制 requirements.txt
echo "正在复制 requirements.txt..."
cp ../../requirements.txt .
echo "requirements.txt 复制完成."

# 安装 Python 依赖
echo "正在安装 Python 依赖..."
$PIP_CMD install -v --no-cache-dir -r requirements.txt
echo "Python 依赖安装完成."

# 获取 gradion 的安装路径
GRADIO_PATH=$(python3 -c "import gradio; import os; print(os.path.dirname(gradio.__file__))")

# 下载 frpc
echo "正在下载 frpc..."
wget -O frpc_linux_amd64 "https://cdn-media.hf-mirror.com/frpc-gradio-0.3/frpc_linux_amd64"
if [ $? -ne 0 ]; then
    echo "Failed to download frpc. Please check your internet connection."
    exit 1
fi

# 重命名 frpc
echo "正在重命名 frpc..."
mv frpc_linux_amd64 frpc_linux_amd64_v0.3

# 移动 frpc
echo "正在移动 frpc 到 ${GRADIO_PATH}..."
mv frpc_linux_amd64_v0.3 "$GRADIO_PATH"
if [ $? -ne 0 ]; then
    echo "Failed to move frpc. Please make sure you have permission."
    exit 1
fi

echo "frpc 下载完成并放置正确位置."


# 添加执行权限
echo "正在添加 frpc 执行权限..."
chmod +x "$GRADIO_PATH/frpc_linux_amd64_v0.3"
if [ $? -ne 0 ]; then
    echo "Failed to add execution permission for frpc. Please check your permission."
    exit 1
fi


# 定义变量（可按需修改）
MODEL_URL="https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20.tar.bz2"
MODEL_DIR="sherpa-onnx-streaming-zipformer-model"

# 创建目录并下载模型
mkdir -p "${MODEL_DIR}" && \
wget "${MODEL_URL}" -O model.tar.bz2 && \
tar -xvf model.tar.bz2 -C ./ && \
rm model.tar.bz2

# 重命名解压后的目录
mv sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20/ "${MODEL_DIR}/"

echo "模型已成功安装到目录: ${MODEL_DIR}"

# 复制其他应用代码（假设当前脚本在项目根目录下）
echo "正在复制启动代码..."
cp -r ../../streamingaudio.py .
echo "启动代码复制完成."

