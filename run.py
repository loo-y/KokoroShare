import os
import torch
from models import build_model
from kokoro import generate
from IPython.display import Audio, display
import numpy as np


device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f'loaded device: {device}')
MODEL = build_model('kokoro-v0_19.pth', device)

VOICE_NAMES = [
    'af',  # Default voice is a 50-50 mix of Bella & Sarah
    'af_bella', 'af_sarah', 'am_adam', 'am_michael',
    'bf_emma', 'bf_isabella', 'bm_george', 'bm_lewis',
    'af_nicole', 'af_sky',
]
VOICEPACKS = {name: torch.load(f'voices/{name}.pt', weights_only=True).to(device) for name in VOICE_NAMES}


def generate_audio(text, voice_name):
    if not text:
        return None, None, "Please enter some text."
    if voice_name not in VOICEPACKS:
        return None, None, "Invalid voice selected."
    voicepack = VOICEPACKS[voice_name]
    try:
        audio, out_ps = generate(MODEL, text, voicepack, lang=voice_name[0])
        return (24000, audio), out_ps, None
    except Exception as e:
      return None, None, str(e)

def display_audio(audio_tuple):
  if audio_tuple:
    rate, data = audio_tuple
    return (rate, np.array(data))
    #return display(Audio(data=data, autoplay=True))
    #return Audio(data=data, rate=rate, autoplay=True)、

  else:
    return None


# --- Gradio Interface ---
with gr.Blocks() as demo:
  gr.Markdown("## Kokoro Text-to-Speech")
  with gr.Row():
    with gr.Column():
      text_input = gr.Textbox(label="Enter text to synthesize:", lines=5, placeholder="Enter text here...")
      voice_dropdown = gr.Dropdown(choices=VOICE_NAMES, label="Select Voice", value=VOICE_NAMES[0])
      generate_button = gr.Button("Generate Audio")
      error_output = gr.Textbox(label="Error Message", interactive=False)
    with gr.Column():
      audio_output = gr.Audio(label="Generated Audio", interactive=False)
      phoneme_output = gr.Textbox(label="Phonemes", interactive=False)

  generate_button.click(
      generate_audio,
      inputs=[text_input, voice_dropdown],
      outputs=[audio_output, phoneme_output, error_output],
  ).then(
      display_audio,
      inputs=audio_output,
      outputs=audio_output
  )

# --- Launch the Web UI ---
if __name__ == "__main__":
  demo.launch(share=False, server_name="0.0.0.0", server_port=7860)
