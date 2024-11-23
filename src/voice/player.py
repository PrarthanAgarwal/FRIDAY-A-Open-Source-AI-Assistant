import wave
import pyaudio
from threading import Event
from pathlib import Path
from loguru import logger
from rhasspysilence import WebRtcVadRecorder, VoiceCommandResult

class AudioPlayer:
    def __init__(self):
        self.playback_buffer = 2048
        self.input_buffer = 512
        self.chunk_size = 1536
        self.vad_mode = 2
        self.silence_seconds = 0.25
        self.stop_event = Event()
        self.pa = pyaudio.PyAudio()

    async def play(self, file_path: Path, interruptible: bool = True) -> bool:
        """
        Plays audio file with optional interrupt capability
        Returns True if played completely, False if interrupted
        """
        try:
            with wave.open(str(file_path), 'rb') as wf:
                playback_stream = self.pa.open(
                    format=self.pa.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True,
                    frames_per_buffer=self.playback_buffer
                )
                
                input_stream = None
                recorder = None
                
                if interruptible:
                    input_stream = self.pa.open(
                        rate=16000,
                        format=pyaudio.paInt16,
                        channels=1,
                        input=True,
                        frames_per_buffer=self.input_buffer
                    )
                    recorder = WebRtcVadRecorder(
                        vad_mode=self.vad_mode,
                        silence_seconds=self.silence_seconds
                    )
                    recorder.start()
                
                data = wf.readframes(self.chunk_size)
                while data and not self.stop_event.is_set():
                    if interruptible and input_stream:
                        try:
                            input_chunk = input_stream.read(
                                self.input_buffer, 
                                exception_on_overflow=False
                            )
                            voice_command = recorder.process_chunk(input_chunk)
                            if voice_command and voice_command.result == VoiceCommandResult.SUCCESS:
                                logger.info("Playback interrupted by voice")
                                return False
                        except OSError:
                            pass
                            
                    playback_stream.write(data)
                    data = wf.readframes(self.chunk_size)
                
                return True

        except Exception as e:
            logger.error(f"Error playing audio: {e}")
            return False

        finally:
            if 'playback_stream' in locals():
                playback_stream.stop_stream()
                playback_stream.close()
            if 'input_stream' in locals() and input_stream:
                input_stream.stop_stream()
                input_stream.close()
            if 'recorder' in locals() and recorder:
                recorder.stop() 