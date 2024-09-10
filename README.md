
# FRIDAY - A Open Source AI Assistant

Introducing FRIDAY, your cutting-edge speech-to-speech AI assistant that brings seamless voice interactions to life. Powered by OpenVoice for advanced voice cloning, FRIDAY captures and replicates voice styles with emotional depth, accents, and tone for a more personalized user experience. With Whisper's high-accuracy speech-to-text capabilities, FRIDAY flawlessly transcribes spoken words into text, ensuring precise understanding of user input. Paired with state-of-the-art large language models, FRIDAY processes this input to generate intelligent, contextually relevant responses.



## Tech Stack

**OpenVoice:** For voice cloning and flexible voice style control (emotion, accents, and tone).

**Whisper:** For high-accuracy speech-to-text transcription.

**LM Studio:** A software platform for using and fine-tuning language models locally on your machine.

**sounddevice, pyaudio, and speechrecognition:** Essential for audio recording and playback.




## Architecture 
- **User Console:** The system begins by recording the user's speech through the user interface or console.

- **Whisper STT:** This component transcribes the recorded speech into text using high-accuracy speech-to-text technology.

- **Conversational Chain:** The transcribed text is processed by a conversational chain powered by LM Studio and any large language model (LLM) to generate a meaningful response.

- **MyShell OpenVoice:** The generated response is converted into speech using open-source voice cloning technology, providing flexibility in voice style (emotion, accents, tone).

![FRIDAY](https://github.com/user-attachments/assets/f1075f62-b9d0-45ee-919c-3327eebf3e10)



## Prerequisites
 - Make sure to set up a *virtual Python environment*. You have several options for this, including pyenv, virtualenv and others that serve a similar purpose.

 - Set up [OpenVoice](https://github.com/myshell-ai/OpenVoice) from their masterful repo.

 - Install *requirements.txt* on your environemnt.

 - Test different LLMs with varying parameter sizes to determine which provides the best token-per-second output on your device. Currently, I'm using TheBloke/phi-2 - 3B model for comparison. 
