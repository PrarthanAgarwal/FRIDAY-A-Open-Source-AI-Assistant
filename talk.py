import os
import torch
import argparse
import pyaudio
import logging
import wave
from zipfile import ZipFile
import langid
from openvoice import se_extractor
from api import BaseSpeakerTTS, ToneColorConverter 
import time
import speech_recognition as sr
import whisper
import numpy as np
import datetime
import requests
import json

from record import speech_to_text

# ANSI escape codes for colors
PINK = '\033[95m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
NEON_GREEN = '\033[92m'
RESET_COLOR = '\033[0m'

# Function to open a file and return its contents as a string
def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

# Define the name of the log file
chat_log_filename = "chatbot_conversation_log.txt"

# Ollama query function
def query_ollama(prompt):
    url = "http://localhost:11434/api/generate"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3.2",  # You can change this to your preferred model
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            try:
                data = response.json()
                return data["response"]
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {e}")
                return None
        else:
            print(f"Error querying Ollama: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"Error querying Ollama: {e}")
        return None

# Command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--share", action='store_true', default=False, help="make link public")
args = parser.parse_args()

# Model and device setup
en_ckpt_base = 'checkpoints/base_speakers/EN'
ckpt_converter = 'checkpoints/converter'
device = 'cuda' if torch.cuda.is_available() else 'cpu'

output_dir = 'outputs'
try:
    os.makedirs(output_dir, exist_ok=True)
except Exception as e:

# Load models
    en_base_speaker_tts = BaseSpeakerTTS(f'{en_ckpt_base}/config.json', device=device)
    en_base_speaker_tts.load_ckpt(f'{en_ckpt_base}/checkpoint.pth')

tone_color_converter = ToneColorConverter(f'{ckpt_converter}/config.json', device=device)
tone_color_converter.load_ckpt(f'{ckpt_converter}/checkpoint.pth')

# Load speaker embeddings for English
en_source_default_se = torch.load(f'{en_ckpt_base}/en_default_se.pth').to(device)
en_source_style_se = torch.load(f'{en_ckpt_base}/en_style_se.pth').to(device)

def get_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def chatgpt_streamed(user_input, system_message, conversation_history, bot_name):
    """
    Function to send a query to Ollama, process the response, and print each line in green color.
    Logs the conversation to a file.
    """
    # Combine system message, conversation history, and user input
    full_prompt = f"{system_message}\n\nConversation history:\n"
    for message in conversation_history:
        role = message["role"]
        content = message["content"]
        full_prompt += f"{role}: {content}\n"
    full_prompt += f"user: {user_input}\nassistant:"

    # Get response from Ollama
    response = query_ollama(full_prompt)
    
    if response is None:
        print("Failed to get response from Ollama")
        return ""

    # Process and print the response
    full_response = ""

    with open(chat_log_filename, "a") as log_file:
        lines = response.split('\n')
        for line in lines:
            if line.strip():
                print(NEON_GREEN + line + RESET_COLOR)
                full_response += line + '\n'
                log_line = f"{get_timestamp()} {bot_name}: {line}\n"
                log_file.write(log_line)

    return full_response.strip()

# Main processing function
def process_and_play(prompt, style, audio_file_pth2):
    tts_model = en_base_speaker_tts
    source_se = en_source_default_se if style == 'default' else en_source_style_se

    speaker_wav = audio_file_pth2

    try:
        target_se, audio_name = se_extractor.get_se(speaker_wav, tone_color_converter, target_dir='processed', vad=True)

        src_path = f'{output_dir}/tmp.wav'
        tts_model.tts(prompt, src_path, speaker=style, language='English')

        save_path = f'{output_dir}/output.wav'
        
        encode_message = "@MyShell"
        tone_color_converter.convert(audio_src_path=src_path, src_se=source_se, tgt_se=target_se, output_path=save_path, message=encode_message)

        print("Here is the audio:")
        play_audio(save_path)

    except Exception as e:
        print(f"Error during audio generation: {e}")

#Function to play audio using PyAudio
def play_audio(file_path):
    wf = wave.open(file_path, 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    data = wf.readframes(1024)
    while data:
        stream.write(data)
        data = wf.readframes(1024)
    stream.stop_stream()
    stream.close()
    p.terminate()

# Function to handle a conversation with a user
def user_chatbot_conversation():
    conversation_history = []
    system_message = open_file("Personality.txt")  # Loads the instructions
    
    while True:
        user_input = speech_to_text()  # Record and transcribe the audio
        
        if user_input.lower() == "exit":  # Say 'exit' to end the conversation
            break
        
        print(CYAN + "You:", user_input + RESET_COLOR)
        conversation_history.append({"role": "user", "content": user_input})
        
        print(PINK + "Friday:" + RESET_COLOR)
        # Process user input and get chatbot response
        chatbot_response = chatgpt_streamed(user_input, system_message, conversation_history, "Friday")
        conversation_history.append({"role": "assistant", "content": chatbot_response})
        
        # Process the chatbot's response and play the audio output
        prompt2 = chatbot_response
        style = "default"
        audio_file_pth2 = "resources\\example_reference.mp3"
        process_and_play(prompt2, style, audio_file_pth2)

        if len(conversation_history) > 20:
            conversation_history = conversation_history[-20:]

# Start the conversation
if __name__ == "__main__":
    user_chatbot_conversation()
