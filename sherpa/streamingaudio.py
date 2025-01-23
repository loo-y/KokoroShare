import gradio as gr
import numpy as np
from sherpa_onnx import OnlineRecognizer, OnlineStream

# -------------------- 模型初始化 --------------------
# MODEL_DIR = "sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20"
MODEL_DIR = "sherpa-onnx-streaming-zipformer-model"
def create_recognizer():
    # 模型文件路径
    tokens = f"{MODEL_DIR}/tokens.txt"
    encoder = f"{MODEL_DIR}/encoder-epoch-99-avg-1.onnx"
    decoder = f"{MODEL_DIR}/decoder-epoch-99-avg-1.onnx"
    joiner = f"{MODEL_DIR}/joiner-epoch-99-avg-1.onnx"
    # 替换为你的模型路径（需与sherpa-onnx兼容）
    recognizer = OnlineRecognizer.from_transducer(
        tokens=tokens,
        encoder=encoder,
        decoder=decoder,
        joiner=joiner,
        num_threads=1,
        sample_rate=48000,
        feature_dim=80,
    )
    return recognizer

recognizer = create_recognizer()

# -------------------- 流式处理逻辑 --------------------
def transcribe(stream_state, new_chunk):
    sr, audio_data = new_chunk
    # stream = recognizer.create_stream()
    # 初始化或获取当前识别流
    if stream_state is None:
        stream = recognizer.create_stream()
    else:
        stream = stream_state

    # 处理音频块（转换为模型需要的格式）
    audio_data = audio_data.astype(np.float32)
    if audio_data.ndim > 1:  # 转单声道
        audio_data = np.mean(audio_data, axis=1)
    audio_data /= np.max(np.abs(audio_data))  # 归一化
    
    # 流式识别
    stream.accept_waveform(sr, audio_data.tolist())
    while recognizer.is_ready(stream):
        recognizer.decode_stream(stream)
    result = recognizer.get_result(stream)
    print("语音识别结果：" + result)
    # 返回更新后的流状态和识别结果
    return stream, result or ""

# -------------------- Gradio 界面 --------------------
demo = gr.Interface(
    fn=transcribe,
    inputs=[
        gr.State(),  # 用于保存识别流状态
        gr.Audio(
            sources=["microphone"],
            streaming=True,  # 启用流式模式
            type="numpy"
        )
    ],
    outputs=[
        gr.State(),  # 更新后的流状态
        gr.Textbox(label="实时识别结果")
    ],
    live=True,  # 实时处理输入
    title="流式语音识别 (Sherpa-onnx)",
    description="点击麦克风并说话，实时显示识别结果"
)

# with gr.Blocks(title="流式语音识别") as demo:
#     gr.Markdown("## 🎤 流式语音识别 (Sherpa-onnx)")
#     gr.Markdown("点击麦克风按钮开始说话，识别结果将实时显示下方")

#     stream_state = gr.State()
#     # 输入区域（上方）
#     with gr.Row():
#         state_input = gr.State()  # 隐藏状态组件
#         audio_input = gr.Audio(
#             sources=["microphone"],
#             # streaming=True,
#             type="numpy"
#         )
        
    
#     # 输出区域（下方）
#     with gr.Row():
#         state_output = gr.State()  # 隐藏状态组件
#         result_output = gr.Textbox(
#             label="实时识别结果"
#         )
    


#     # 事件绑定（保持实时流式处理）
#     audio_input.stream(
#         fn=transcribe,
#         inputs=[state_input, audio_input],
#         outputs=[state_output, result_output]
#     )

demo.launch(share=True, server_name="0.0.0.0", server_port=8989)
