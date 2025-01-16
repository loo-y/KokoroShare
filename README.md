# KokoroShare
本项目旨在将强大的 [Kokoro-TTS](https://huggingface.co/hexgrad/Kokoro-82M) 以易于使用的 Web UI 形式呈现，用户可以自由输入文本，并选择不同的声音进行语音合成。
> Kokoro is a frontier TTS model for its size of 82 million parameters (text in/audio out).

https://github.com/user-attachments/assets/c6dd56ac-2553-4471-a634-72770a96dad1


## 快速上手
项目提供了两种方式来运行 KokoroShare，您可以选择最适合您的方式：
### 方式一：Docker (推荐)
我们已为您准备好 Dockerfile，您可以根据需要进行自定义。以下是如何构建和运行 Docker 镜像的步骤：
#### 1. 构建 Docker 镜像
```bash
docker build -t kokoroshare .
```

#### 2. 运行 Docker 容器
CPU 模式：
```bash
docker run -dp 7860:7860 --name kokoroTTS kokoroshare
```
GPU 模式 (如果您有 NVIDIA 显卡):
```bash
docker run --gpus=all -dp 7860:7860 --name kokoroTTS kokoroshare
```

#### 3. 进入 Docker 容器 (可选)
```bash
docker exec -it kokoroTTS /bin/bash
```


### 方式二：Google Colab
如果您希望快速体验，或者没有本地环境，可以使用 Google Colab：
* 访问 [Google Colab](https://colab.research.google.com/)
* 点击"文件" - "上传Notebook"
* 选择项目中的 ```KokoroShare.ipynb``` 进行上传
* 运行 Notebook 中的代码块
* 当 Gradio 应用启动后，您将获得一个公共链接，用于访问 Web UI。

    <img src="https://github.com/user-attachments/assets/8f3dc7ee-4651-44db-8b8c-3a5a8f2bf839" width=400 />