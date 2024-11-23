import os
import yaml
import torch
import soundfile as sf
from pathlib import Path
from munch import Munch
from typing import Optional
from nltk.tokenize import word_tokenize
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from models.StyleTTS2.models import (
    load_ASR_models,
    load_F0_models,
    build_model
)
from models.StyleTTS2.Utils.PLBERT.util import load_plbert
from models.StyleTTS2.Modules.diffusion.sampler import (
    DiffusionSampler, 
    ADPM2Sampler, 
    KarrasSchedule
)
from models.StyleTTS2.text_utils import TextCleaner
from models.StyleTTS2.testen import CustomEspeakBackend
from models.StyleTTS2.utils import recursive_munch

class TTSHandler:
    def __init__(self, config):
        self.config = config
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.s_prev = None  # Store previous style vector
        
        # Load StyleTTS2 config
        styletts_config_path = os.path.join(config.models.STYLETTS2_PATH, "config.yml")
        self.model_config = yaml.safe_load(open(styletts_config_path))
        
        # Initialize models
        self._initialize_models()
        
        self.textcleaner = TextCleaner()
        self.phonemizer = CustomEspeakBackend(language='en-us')
        
    def _initialize_models(self):
        """Initialize all required StyleTTS2 models"""
        # Load individual components
        self.text_aligner = load_ASR_models(
            self.model_config['ASR_path'],
            self.model_config['ASR_config']
        )
        self.pitch_extractor = load_F0_models(self.model_config['F0_path'])
        self.plbert = load_plbert(self.model_config['PLBERT_dir'])
        
        # Build main model using recursive_munch
        self.model = build_model(
            recursive_munch(self.model_config['model_params']),
            self.text_aligner,
            self.pitch_extractor,
            self.plbert
        )
        
        # Load weights
        weights_path = os.path.join(self.config.models.STYLETTS2_PATH, "epoch_2nd_00100.pth")
        params_whole = torch.load(weights_path, map_location='cpu')
        params = params_whole['net']
        
        for key in self.model:
            if key in params:
                try:
                    self.model[key].load_state_dict(params[key])
                except:
                    from collections import OrderedDict
                    state_dict = params[key]
                    new_state_dict = OrderedDict()
                    for k, v in state_dict.items():
                        name = k[7:]  # remove `module.`
                        new_state_dict[name] = v
                    self.model[key].load_state_dict(new_state_dict, strict=False)
        
        # Move models to device and set to eval mode
        _ = [self.model[key].eval() for key in self.model]
        _ = [self.model[key].to(self.device) for key in self.model]
        
        # Initialize sampler
        self.sampler = DiffusionSampler(
            self.model.diffusion.diffusion,
            sampler=ADPM2Sampler(),
            sigma_schedule=KarrasSchedule(
                sigma_min=0.0001, 
                sigma_max=3.0, 
                rho=9.0
            ),
            clamp=False
        )

    @torch.inference_mode()
    async def generate_speech(self, text: str) -> str:
        """Generate speech from text using StyleTTS2"""
        BATCH_SIZE = 4  # Process 4 sentences at a time
        
        # Split text into sentences
        sentences = [s.strip() + '.' for s in text.split('.') if s.strip()]
        wavs = []
        
        # Process sentences in batches
        for i in range(0, len(sentences), BATCH_SIZE):
            batch = sentences[i:i + BATCH_SIZE]
            batch_wavs = []
            
            with torch.amp.autocast(self.device, dtype=torch.float16):
                noise = torch.randn(
                    len(batch), 1, 256,
                    device=self.device,
                    dtype=torch.float16
                )
                
                for j, (text, noise_j) in enumerate(zip(batch, noise)):
                    wav, self.s_prev = self._inference(
                        text,
                        self.s_prev,
                        noise_j.unsqueeze(0),
                        alpha=0.7,
                        diffusion_steps=5,
                        embedding_scale=1.2
                    )
                    # Add small padding between sentences
                    padding = torch.zeros(int(24000 * 0.05))
                    wav = torch.cat([wav, padding])
                    batch_wavs.append(wav)
            
            wavs.extend(batch_wavs)
        
        combined_wav = torch.cat(wavs)
        
        # Add fade out
        fade_length = int(24000 * 0.3)  # 300ms fade
        fade_out = torch.linspace(1.0, 0.0, fade_length)
        combined_wav[-fade_length:] *= fade_out
        
        # Add final padding
        final_padding = torch.zeros(int(24000 * 0.1))
        combined_wav = torch.cat([combined_wav, final_padding])
        
        # Save to temporary file
        output_path = Path("temp_speech.wav")
        sf.write(output_path, combined_wav.cpu().numpy(), 24000)
        
        return str(output_path)

    def _inference(
        self,
        text: str,
        s_prev: Optional[torch.Tensor],
        noise: torch.Tensor,
        alpha: float = 0.7,
        diffusion_steps: int = 5,
        embedding_scale: float = 1.0
    ):
        """Internal inference method"""
        text = text.strip()
        text = text.replace('"', '')
        ps = self.phonemizer.phonemize([text])
        ps = word_tokenize(ps[0])
        ps = ' '.join(ps)

        tokens = self.textcleaner(ps)
        tokens.insert(0, 0)
        tokens = torch.LongTensor(tokens).to(self.device).unsqueeze(0)
        
        with torch.no_grad():
            input_lengths = torch.LongTensor([tokens.shape[-1]]).to(tokens.device)
            text_mask = self.length_to_mask(input_lengths).to(tokens.device)

            t_en = self.model.text_encoder(tokens, input_lengths, text_mask)
            bert_dur = self.model.bert(tokens, attention_mask=(~text_mask).int())
            d_en = self.model.bert_encoder(bert_dur).transpose(-1, -2) 

            s_pred = self.sampler(noise, 
                  embedding=bert_dur[0].unsqueeze(0), 
                  num_steps=diffusion_steps,
                  embedding_scale=embedding_scale).squeeze(0)
            
            if s_prev is not None:
                # convex combination of previous and current style
                s_pred = alpha * s_prev + (1 - alpha) * s_pred
            
            s = s_pred[:, 128:]
            ref = s_pred[:, :128]

            d = self.model.predictor.text_encoder(d_en, s, input_lengths, text_mask)

            x, _ = self.model.predictor.lstm(d)
            duration = self.model.predictor.duration_proj(x)
            duration = torch.sigmoid(duration).sum(axis=-1)
            pred_dur = torch.round(duration.squeeze()).clamp(min=1)

            pred_aln_trg = torch.zeros(input_lengths, int(pred_dur.sum().data))
            c_frame = 0
            for i in range(pred_aln_trg.size(0)):
                pred_aln_trg[i, c_frame:c_frame + int(pred_dur[i].data)] = 1
                c_frame += int(pred_dur[i].data)

            # encode prosody
            en = (d.transpose(-1, -2) @ pred_aln_trg.unsqueeze(0).to(self.device))
            F0_pred, N_pred = self.model.predictor.F0Ntrain(en, s)
            out = self.model.decoder(
                (t_en @ pred_aln_trg.unsqueeze(0).to(self.device)), 
                F0_pred, N_pred, ref.squeeze().unsqueeze(0)
            )
            
        return out.squeeze().cpu().numpy(), s_pred

    def length_to_mask(self, lengths):
        """Convert lengths to mask"""
        mask = torch.arange(lengths.max()).unsqueeze(0).expand(lengths.shape[0], -1).type_as(lengths)
        mask = torch.gt(mask+1, lengths.unsqueeze(1))
        return mask

    async def close(self):
        """Cleanup resources"""
        # Clear CUDA cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache() 

    @classmethod
    async def create(cls, config):
        """Create a new TTSHandler instance"""
        instance = cls(config)
        return instance