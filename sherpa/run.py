import argparse
import os
import sys
import tarfile
import time
from pathlib import Path
import urllib.request
import numpy as np
import gradio as gr
import sounddevice as sd
import sherpa_onnx

# MODEL_DIR = "sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20"
MODEL_DIR = "sherpa-onnx-streaming-zipformer-model"

def assert_file_exists(filename: str):
    assert Path(filename).is_file(), (
        f"{filename} does not exist!\n"
        "Please refer to "
        "https://k2-fsa.github.io/sherpa/onnx/pretrained_models/index.html to download it"
    )


def create_recognizer(args):
    assert_file_exists(args.encoder)
    assert_file_exists(args.decoder)
    assert_file_exists(args.joiner)
    assert_file_exists(args.tokens)

    recognizer = sherpa_onnx.OnlineRecognizer.from_transducer(
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
        rule3_min_utterance_length=300,  # it essentially disables this rule
        decoding_method=args.decoding_method,
        provider=args.provider,
        hotwords_file=args.hotwords_file,
        hotwords_score=args.hotwords_score,
        blank_penalty=args.blank_penalty,
    )
    return recognizer


def recognize_from_microphone(audio, args):
    if audio is None:
        return "请先录音"
    
    recognizer = create_recognizer(args)
    sample_rate = 16000 # Gradio 默认采样率是 16000
    # 提取 numpy 数组并转换为 list[float]
    audio_sample_rate, audio_data = audio
    audio_float = audio_data.astype(np.float32).tolist()

    stream = recognizer.create_stream()
    stream.accept_waveform(sample_rate, audio_float)
    
    while recognizer.is_ready(stream):
        recognizer.decode_stream(stream)

    result = recognizer.get_result(stream)
    recognizer.reset(stream)
    
    if result and result != "": # 添加非空判断
        return result
    else:
      return "未识别到语音"

def get_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "--tokens",
        type=str,
        default=f"{MODEL_DIR}/tokens.txt",
        help="Path to tokens.txt",
    )

    parser.add_argument(
        "--encoder",
        type=str,
        default=f"{MODEL_DIR}/encoder-epoch-99-avg-1.onnx",
        help="Path to the encoder model",
    )

    parser.add_argument(
        "--decoder",
        type=str,
        default=f"{MODEL_DIR}/decoder-epoch-99-avg-1.onnx",
        help="Path to the decoder model",
    )

    parser.add_argument(
        "--joiner",
        type=str,
        default=f"{MODEL_DIR}/joiner-epoch-99-avg-1.onnx",
        help="Path to the joiner model",
    )

    parser.add_argument(
        "--decoding-method",
        type=str,
        default="greedy_search",
        help="Valid values are greedy_search and modified_beam_search",
    )

    parser.add_argument(
        "--provider",
        type=str,
        default="cpu",
        help="Valid values: cpu, cuda, coreml",
    )

    parser.add_argument(
        "--hotwords-file",
        type=str,
        default="",
        help="""
        The file containing hotwords, one words/phrases per line, and for each
        phrase the bpe/cjkchar are separated by a space. For example:

         HE LL O  WORLD
        你 好 世 界
        """,
    )

    parser.add_argument(
        "--hotwords-score",
        type=float,
        default=1.5,
        help="""
        The hotword score of each token for biasing word/phrase. Used only if
        --hotwords-file is given.
        """,
    )

    parser.add_argument(
        "--blank-penalty",
        type=float,
        default=0.0,
        help="""
        The penalty applied on blank symbol during decoding.
        Note: It is a positive value that would be applied to logits like
        this `logits[:, 0] -= blank_penalty` (suppose logits.shape is
        [batch_size, vocab] and blank id is 0).
        """,
    )

    return parser.parse_args()

if __name__ == "__main__":
    args = get_args()

    iface = gr.Interface(
        fn=lambda audio: recognize_from_microphone(audio, args),
        inputs=gr.Audio(sources=["microphone"], label="Record your voice"),
        outputs="text",
        title="Sherpa-ONNX Speech Recognition",
        description="Real-time speech recognition using Sherpa-ONNX.",
    )

    iface.launch(share=True, server_name="0.0.0.0", server_port=8989)
