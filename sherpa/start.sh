#!/bin/bash

# 切换到脚本所在的目录，防止相对路径问题
cd "$(dirname "$0")sherpa-onnx"

# 启动应用程序
python streamingaudio.py

# 可以添加其他启动相关的命令，例如启动日志输出
# python run.py > app.log 2>&1 &  # 后台运行并输出日志到 app.log

# 可选：在启动完成后输出提示信息
# echo "应用程序已启动！"
