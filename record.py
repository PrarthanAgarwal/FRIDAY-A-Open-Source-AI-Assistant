import io
import typing
import time
import wave
from pathlib import Path
import whisper
from threading import Event
import keyboard #type: ignore

from rhasspysilence import WebRtcVadRecorder, VoiceCommand, VoiceCommandResult
import pyaudio
import os

pa = pyaudio.PyAudio()

class InterruptibleRecorder:
    def __init__(self):
        self.stop_recording = Event()
        self.vad_mode = 3  # Increase sensitivity
        self.silence_seconds = 0.5  # Reduce silence threshold

    def check_interrupt(self):
        return keyboard.is_pressed('esc')  # or any other key you prefer

    def speech_to_text(self) -> str:
        """
        Records audio until silence is detected or interrupted.
        Saves audio to audio/recording.wav and returns the transcribed text using Whisper.
        """
        recorder = WebRtcVadRecorder(
            vad_mode=self.vad_mode,
            silence_seconds=self.silence_seconds,
        )
        recorder.start()
        
        # file directory
        wav_sink = "tempaudio/"
        # file name
        wav_filename = "recording"
        
        if wav_sink:
            wav_sink_path = Path(wav_sink)
            if wav_sink_path.is_dir():
                # Directory to write WAV files
                wav_dir = wav_sink_path
            else:
                # Create the directory if it doesn't exist
                wav_sink_path.mkdir(parents=True, exist_ok=True)
                wav_dir = wav_sink_path
        else:
            raise ValueError("The WAV sink path must not be empty.")
        
        voice_command: typing.Optional[VoiceCommand] = None
        audio_source = pa.open(
            rate=16000,
            format=pyaudio.paInt16,
            channels=1,
            input=True,
            frames_per_buffer=960,
        )
        audio_source.start_stream()

        frames = []
        
        try:
            while True:
                if self.check_interrupt():
                    print("\nRecording interrupted by user")
                    return "interrupted"

                chunk = audio_source.read(960)
                voice_command = recorder.process_chunk(chunk)
                frames.append(chunk)

                if voice_command and voice_command.result == VoiceCommandResult.SUCCESS:
                    print("Finished recording.")
                    break

            # Save the audio data as a .wav file
            wav_file_path = wav_dir / f"{wav_filename}.wav"
            wav_file_str = str(wav_file_path)  # Convert Path object to string
            with wave.open(wav_file_str, "wb") as wf:  # Pass string path to wave.open
                wf.setnchannels(1)
                wf.setsampwidth(pa.get_sample_size(pyaudio.paInt16))
                wf.setframerate(16000)
                wf.writeframes(b''.join(frames))

            # Transcribe the saved audio file using Whisper
            #print("Transcribing audio with Whisper...")
            user_transcription = transcribe_with_whisper(wav_file_str)
            #print("Transcription complete.")
            return user_transcription

        finally:
            audio_source.stop_stream()
            audio_source.close()
            recorder.stop()

def transcribe_with_whisper(audio_file_path: str) -> str:
    # Load the model
    model = whisper.load_model("base.en")  # You can choose different model sizes like 'tiny', 'base', 'small', 'medium', 'large'

    # Transcribe the audio
    result = model.transcribe(audio_file_path)
    return result["text"]        
