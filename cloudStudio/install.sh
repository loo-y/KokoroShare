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

# 检查并安装 git-lfs
if ! command -v git-lfs &> /dev/null
then
  echo "git-lfs is not installed. Attempting to install..."
  apt-get update
  apt-get install -y git-lfs
  if [ $? -ne 0 ]; then
        echo "Failed to install git-lfs. Please install it manually and run this script again."
        exit 1
  fi
  echo "git-lfs installed successfully."
fi

# 安装 espeak-ng
echo "正在安装 espeak-ng..."
apt-get update
apt-get -qq -y install espeak-ng > /dev/null 2>&1
echo "espeak-ng 安装完成."

# 克隆仓库
echo "正在克隆 Kokoro-82M 仓库..."
git lfs install
git clone https://hf-mirror.com/hexgrad/Kokoro-82M Kokoro-82M
echo "Kokoro-82M 仓库克隆完成."

# 进入仓库目录
cd Kokoro-82M

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

# 复制其他应用代码（假设当前脚本在项目根目录下）
echo "正在复制启动代码..."
cp -r ../../run.py .
echo "启动代码复制完成."

# 修改 run.py 中的启动代码
echo "正在修改启动代码，支持公网分享..."
sed -i 's/demo.launch(share=False/demo.launch(share=True/g' run.py
echo "启动代码修改完成."

echo "安装完成！请进入 Kokoro-82M 目录并执行 python run.py 来运行应用程序。"
