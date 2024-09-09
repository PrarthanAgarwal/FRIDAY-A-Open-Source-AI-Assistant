
# FRIDAY - A Open Source AI Assistant

Introducing FRIDAY, your cutting-edge speech-to-speech AI assistant that brings seamless voice interactions to life. Powered by OpenVoice for advanced voice cloning, FRIDAY captures and replicates voice styles with emotional depth, accents, and tone for a more personalized user experience. With Whisper's high-accuracy speech-to-text capabilities, FRIDAY flawlessly transcribes spoken words into text, ensuring precise understanding of user input. Paired with state-of-the-art large language models, FRIDAY processes this input to generate intelligent, contextually relevant responses.



## Tech Stack

**OpenVoice:** For voice cloning and flexible voice style control (emotion, accents, and tone).

**Whisper:** For high-accuracy speech-to-text transcription.

**LM Studio:** A software platform for using and fine-tuning language models locally on your machine.

**sounddevice, pyaudio, and speechrecognition:** Essential for audio recording and playback.




## Architecture 
**User Console:** The system begins by recording the user's speech through the user interface or console.

**Whisper STT:** This component transcribes the recorded speech into text using high-accuracy speech-to-text technology.

**Conversational Chain:** The transcribed text is processed by a conversational chain powered by LM Studio and any large language model (LLM) to generate a meaningful response.

**MyShell OpenVoice:** The generated response is converted into speech using open-source voice cloning technology, providing flexibility in voice style (emotion, accents, tone).

**User Console (Playback):** Finally, the system plays the generated audio response back to the user, completing the interaction.

![App Screenshot](https://via.placeholder.com/468x300?text=App+Screenshot+Here)

