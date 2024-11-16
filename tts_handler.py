import os
from pathlib import Path
import torch
from api import BaseSpeakerTTS, ToneColorConverter
from openvoice import se_extractor

class TTSHandler:
    def __init__(self, en_ckpt_base, ckpt_converter, device):
        self.device = device
        self.output_dir = 'outputs'
        self.setup_directories()
        self.load_models(en_ckpt_base, ckpt_converter)
        
    def setup_directories(self):
        os.makedirs(self.output_dir, exist_ok=True)
        
    def load_models(self, en_ckpt_base, ckpt_converter):
        self.en_base_speaker_tts = BaseSpeakerTTS(
            f'{en_ckpt_base}/config.json', 
            device=self.device
        )
        self.en_base_speaker_tts.load_ckpt(f'{en_ckpt_base}/checkpoint.pth')
        
        self.tone_color_converter = ToneColorConverter(
            f'{ckpt_converter}/config.json', 
            device=self.device
        )
        self.tone_color_converter.load_ckpt(f'{ckpt_converter}/checkpoint.pth')
        
        self.en_source_default_se = torch.load(
            f'{en_ckpt_base}/en_default_se.pth'
        ).to(self.device)
        self.en_source_style_se = torch.load(
            f'{en_ckpt_base}/en_style_se.pth'
        ).to(self.device)
    
    def process_and_play(self, prompt, style, audio_file_pth2, audio_handler):
        source_se = (self.en_source_default_se 
                    if style == 'default' 
                    else self.en_source_style_se)
        
        try:
            print("\nGenerating voice response...", end='', flush=True)
            
            target_se, audio_name = se_extractor.get_se(
                audio_file_pth2, 
                self.tone_color_converter, 
                target_dir='processed', 
                vad=True
            )
            
            src_path = f'{self.output_dir}/tmp.wav'
            self.en_base_speaker_tts.tts(
                prompt, 
                src_path, 
                speaker=style, 
                language='English'
            )
            
            save_path = f'{self.output_dir}/output.wav'
            self.tone_color_converter.convert(
                audio_src_path=src_path,
                src_se=source_se,
                tgt_se=target_se,
                output_path=save_path,
                message="@MyShell"
            )
            
            print("Done!")
            print("\nPlaying response:")
            audio_handler.play_audio(save_path)
            
        except Exception as e:
            print(f"Error during audio generation: {e}") 