import gradio as gr
import sounddevice as sd
import sherpa_onnx
import numpy as np
from queue import Queue
import threading

# -------------------- 模型初始化 --------------------
# MODEL_DIR = "sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20"
MODEL_DIR = "sherpa-onnx-streaming-zipformer-model"

def create_recognizer():
    # 模型文件路径
    tokens = f"{MODEL_DIR}/tokens.txt"
    encoder = f"{MODEL_DIR}/encoder-epoch-99-avg-1.onnx"
    decoder = f"{MODEL_DIR}/decoder-epoch-99-avg-1.onnx"
    joiner = f"{MODEL_DIR}/joiner-epoch-99-avg-1.onnx"

    # 创建识别器
    recognizer = sherpa_onnx.OnlineRecognizer.from_transducer(
        tokens=tokens,
        encoder=encoder,
        decoder=decoder,
        joiner=joiner,
        num_threads=1,
        sample_rate=16000,
        feature_dim=80,
        enable_endpoint_detection=True,
        rule1_min_trailing_silence=2.4,
        rule2_min_trailing_silence=1.2,
        rule3_min_utterance_length=300,
        decoding_method="greedy_search",
        provider="cpu",
    )
    return recognizer

# -------------------- 全局变量 --------------------
recognizer = create_recognizer()  # 初始化模型
result_queue = Queue()            # 结果队列
audio_stream = None               # 音频流对象
stream = None                     # sherpa-onnx流

# -------------------- 音频处理逻辑 --------------------
def audio_callback(indata, frames, time, status):
    """实时音频流回调函数"""
    global stream
    if status:
        print(f"音频流错误: {status}")
    
    # 将numpy数组转换为list[float]
    samples = indata.reshape(-1).astype(np.float32).tolist()
    
    # 流式处理音频数据
    stream.accept_waveform(16000, samples)  # 注意采样率需与模型一致
    while recognizer.is_ready(stream):
        recognizer.decode_stream(stream)
    
    # 获取识别结果
    result = recognizer.get_result(stream)
    if result:
        result_queue.put(result)  # 将结果推送到队列

# -------------------- Gradio交互逻辑 --------------------
def start_recording():
    """开始录音"""
    global audio_stream, stream
    stream = recognizer.create_stream()  # 创建新的识别流
    try:
        audio_stream = sd.InputStream(
            samplerate=16000,       # 必须与模型采样率一致
            channels=1,
            callback=audio_callback,
            dtype='float32'
        )
        audio_stream.start()
        return "录音已开始，请说话..."
    except Exception as e:
        return f"启动失败: {str(e)}"

def stop_recording():
    """停止录音"""
    global audio_stream
    if audio_stream:
        audio_stream.stop()
        audio_stream.close()
        audio_stream = None
    return "录音已停止"

def update_result():
    """实时更新识别结果到界面"""
    while True:
        if not result_queue.empty():
            yield result_queue.get()
        else:
            yield "等待语音输入..."
        time.sleep(0.1)  # 控制更新频率

# -------------------- 构建Gradio界面 --------------------
with gr.Blocks(title="实时语音识别") as demo:
    gr.Markdown("# 基于Sherpa-onnx的实时语音识别")
    
    # 控件
    result_box = gr.Textbox(label="识别结果", interactive=False, streaming=True)
    start_btn = gr.Button("🎤 开始录音", variant="primary")
    stop_btn = gr.Button("⏹ 停止录音", variant="secondary")
    
    # 事件绑定
    start_btn.click(
        fn=start_recording,
        outputs=result_box,
        api_name="start_recording"
    )
    stop_btn.click(
        fn=stop_recording,
        outputs=result_box,
        api_name="stop_recording"
    )
    
    # 实时更新
    demo.load(
        fn=update_result,
        outputs=result_box,
        every=0.1,  # 每0.1秒更新一次
    )

# -------------------- 启动应用 --------------------
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
