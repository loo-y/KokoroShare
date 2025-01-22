import argparse
import numpy as np
import gradio as gr
import sherpa_onnx

# MODEL_DIR = "sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20"
MODEL_DIR = "sherpa-onnx-streaming-zipformer-model"

def assert_file_exists(filename: str):
    assert Path(filename).is_file(), f"{filename} does not exist!"

def create_recognizer(args):
    return sherpa_onnx.OnlineRecognizer.from_transducer(
        tokens=args.tokens,
        encoder=args.encoder,
        decoder=args.decoder,
        joiner=args.joiner,
        num_threads=1,
        sample_rate=16000,
        feature_dim=80,
        enable_endpoint_detection=True,
        rule1_min_trailing_silence=2.4,
        rule2_min_trailing_silence=1.2,
        rule3_min_utterance_length=300,
        decoding_method=args.decoding_method,
        provider=args.provider,
        hotwords_file=args.hotwords_file,
        hotwords_score=args.hotwords_score,
        blank_penalty=args.blank_penalty,
    )

def recognize_from_microphone(audio, args):
    if audio is None:
        return "请先录音"

    # Gradio返回的音频格式处理
    sample_rate, audio_data = audio
    audio_data = audio_data.astype(np.float32) / 32768.0  # int16转float32归一化

    recognizer = create_recognizer(args)
    stream = recognizer.create_stream()

    # 模拟流式处理：将完整音频分成小块
    chunk_size = int(0.1 * sample_rate)  # 每次处理0.1秒的音频
    pointer = 0
    result = ""

    while pointer < len(audio_data):
        # 提取当前块数据
        chunk = audio_data[pointer:pointer + chunk_size]
        pointer += chunk_size

        # 传入流式接口
        stream.accept_waveform(sample_rate, chunk.tolist())
        while recognizer.is_ready(stream):
            recognizer.decode_stream(stream)

        # 检测端点并获取结果
        is_endpoint = recognizer.is_endpoint(stream)
        current_result = recognizer.get_result(stream)

        if current_result:
            result = current_result
            if is_endpoint:
                break  # 检测到端点，提前结束

    # 最终结果处理
    recognizer.reset(stream)
    return result if result else "未识别到语音"

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tokens", default=f"{MODEL_DIR}/tokens.txt")
    parser.add_argument("--encoder", default=f"{MODEL_DIR}/encoder-epoch-99-avg-1.onnx")
    parser.add_argument("--decoder", default=f"{MODEL_DIR}/decoder-epoch-99-avg-1.onnx")
    parser.add_argument("--joiner", default=f"{MODEL_DIR}/joiner-epoch-99-avg-1.onnx")
    parser.add_argument("--decoding-method", default="greedy_search")
    parser.add_argument("--provider", default="cpu")
    parser.add_argument("--hotwords-file", default="")
    parser.add_argument("--hotwords-score", type=float, default=1.5)
    parser.add_argument("--blank-penalty", type=float, default=0.0)
    return parser.parse_args()

if __name__ == "__main__":
    args = get_args()
    iface = gr.Interface(
        fn=lambda audio: recognize_from_microphone(audio, args),
        inputs=gr.Audio(sources="microphone", type="numpy", label="录音"),
        outputs="text",
        title="Sherpa-ONNX 实时语音识别",
        description="点击下方录音按钮开始说话",
    )
    iface.launch(share=True, server_name="0.0.0.0", server_port=8989)
