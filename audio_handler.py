import wave
import pyaudio
import keyboard #type: ignore
import torch
from openvoice import se_extractor
from rhasspysilence import WebRtcVadRecorder, VoiceCommand, VoiceCommandResult

class AudioHandler:
    def __init__(self, device='cuda:0' if torch.cuda.is_available() else 'cpu'):
        self.device = device
        self.setup_audio_parameters()
        
    def setup_audio_parameters(self):
        self.playback_buffer = 2048
        self.input_buffer = 512
        self.chunk_size = 1536
        self.vad_mode = 2
        self.silence_seconds = 0.25
    
    def play_audio(self, file_path):
        wf = wave.open(file_path, 'rb')
        p = pyaudio.PyAudio()
        playback_stream = None
        input_stream = None
        
        try:
            playback_stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                                   channels=wf.getnchannels(),
                                   rate=wf.getframerate(),
                                   output=True,
                                   frames_per_buffer=self.playback_buffer)
            
            input_stream = p.open(rate=16000,
                                format=pyaudio.paInt16,
                                channels=1,
                                input=True,
                                frames_per_buffer=self.input_buffer)
            
            recorder = WebRtcVadRecorder(vad_mode=self.vad_mode, 
                                       silence_seconds=self.silence_seconds)
            recorder.start()
            
            data = wf.readframes(self.chunk_size)
            
            while data:
                if keyboard.is_pressed('esc'):
                    break
                    
                try:
                    input_chunk = input_stream.read(self.input_buffer, 
                                                  exception_on_overflow=False)
                    voice_command = recorder.process_chunk(input_chunk)
                    
                    if voice_command and voice_command.result == VoiceCommandResult.SUCCESS:
                        print("\nVoice detected, stopping playback...")
                        break
                except OSError:
                    pass
                    
                playback_stream.write(data)
                data = wf.readframes(self.chunk_size)
                
        finally:
            self.cleanup_streams(playback_stream, input_stream, p, recorder)
    
    def cleanup_streams(self, playback_stream, input_stream, p, recorder):
        if playback_stream:
            playback_stream.stop_stream()
            playback_stream.close()
        if input_stream:
            input_stream.stop_stream()
            input_stream.close()
        p.terminate()
        recorder.stop() 