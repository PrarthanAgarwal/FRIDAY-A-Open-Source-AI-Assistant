import io
import wave
from pathlib import Path
import keyboard
from threading import Event
import pyaudio
from rhasspysilence import WebRtcVadRecorder, VoiceCommand, VoiceCommandResult
from loguru import logger

class InterruptibleRecorder:
    def __init__(self, whisper_handler):
        """
        Initialize recorder with WhisperHandler for transcription
        """
        self.stop_recording = Event()
        self.vad_mode = 3  # More aggressive voice detection
        self.silence_seconds = 0.5
        self.whisper_handler = whisper_handler
        self.pa = pyaudio.PyAudio()
        self.temp_dir = Path("temp/audio")
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def check_interrupt(self):
        return keyboard.is_pressed('esc')

    async def record(self) -> str:
        """
        Records audio until silence is detected or interrupted.
        Returns transcribed text using faster-whisper.
        """
        recorder = WebRtcVadRecorder(
            vad_mode=self.vad_mode,
            silence_seconds=self.silence_seconds,
        )
        recorder.start()
        
        audio_source = self.pa.open(
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
                    logger.info("Recording interrupted by user")
                    return "interrupted"

                chunk = audio_source.read(960)
                voice_command = recorder.process_chunk(chunk)
                frames.append(chunk)

                if voice_command and voice_command.result == VoiceCommandResult.SUCCESS:
                    logger.info("Voice command complete")
                    break

            wav_path = self.temp_dir / "recording.wav"
            with wave.open(str(wav_path), "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(self.pa.get_sample_size(pyaudio.paInt16))
                wf.setframerate(16000)
                wf.writeframes(b''.join(frames))

            # Transcribe using faster-whisper
            return await self.whisper_handler.transcribe(wav_path)

        finally:
            audio_source.stop_stream()
            audio_source.close()
            recorder.stop() 