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
import openai
from openai import OpenAI
import time
import speech_recognition as sr
import whisper
import numpy as np
import datetime

from record import speech_to_text

# Setup logging
LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(filename="friday.log", level=logging.DEBUG, format=LOG_FORMAT)
logger = logging.getLogger()

# ANSI escape codes for colors
PINK = '\033[95m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
NEON_GREEN = '\033[92m'
RESET_COLOR = '\033[0m'

# Function to open a file and return its contents as a string
def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        logger.info(f"Opened file {filepath} successfully")
        return infile.read()

# Initialize the OpenAI client with the API key
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

# Define the name of the log file
chat_log_filename = "chatbot_conversation_log.txt"

# Command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--share", action='store_true', default=False, help="make link public")
args = parser.parse_args()

# Model and device setup
en_ckpt_base = 'checkpoints/base_speakers/EN'
ckpt_converter = 'checkpoints/converter'
device = 'cuda' if torch.cuda.is_available() else 'cpu'
logger.info(f"Device set to {device}")

output_dir = 'outputs'
try:
    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"Output directory '{output_dir}' created successfully")
except Exception as e:
    logger.error(f"Failed to create output directory '{output_dir}': {e}")

# Load models
en_base_speaker_tts = BaseSpeakerTTS(f'{en_ckpt_base}/config.json', device=device)
en_base_speaker_tts.load_ckpt(f'{en_ckpt_base}/checkpoint.pth')

tone_color_converter = ToneColorConverter(f'{ckpt_converter}/config.json', device=device)
tone_color_converter.load_ckpt(f'{ckpt_converter}/checkpoint.pth')

# Load speaker embeddings for English
en_source_default_se = torch.load(f'{en_ckpt_base}/en_default_se.pth').to(device)
en_source_style_se = torch.load(f'{en_ckpt_base}/en_style_se.pth').to(device)

# Main processing function
def process_and_play(prompt, style, audio_file_pth2):
    tts_model = en_base_speaker_tts
    source_se = en_source_default_se if style == 'default' else en_source_style_se

    speaker_wav = audio_file_pth2

    # Process text and generate audio
    try:
        target_se, audio_name = se_extractor.get_se(speaker_wav, tone_color_converter, target_dir='processed', vad=True)

        src_path = f'{output_dir}/tmp.wav'
        tts_model.tts(prompt, src_path, speaker=style, language='English')

        save_path = f'{output_dir}/output.wav'
        
        # Run the tone color converter
        encode_message = "@MyShell"
        tone_color_converter.convert(audio_src_path=src_path, src_se=source_se, tgt_se=target_se, output_path=save_path, message=encode_message)

        print("Here is the audio:")
        play_audio(save_path)

    except Exception as e:
        print(f"Error during audio generation: {e}")

# Define a function to get the current timestamp in a formatted string
def get_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def chatgpt_streamed(user_input, system_message, conversation_history, bot_name):
    """
    Function to send a query to GPT-3.5-model, stream the response, and print each full line in yellow color.
    Logs the conversation to a file.
    """
    messages = [{"role": "system", "content": system_message}] + conversation_history + [{"role": "user", "content": user_input}]
    temperature=0.7
    
    streamed_completion = client.chat.completions.create(
        model="TheBloke/phi-2-GGUF",
        messages=messages,
        stream=True
    )

    full_response = ""
    line_buffer = ""

    with open(chat_log_filename, "a") as log_file:  # Open the log file in append mode
        for chunk in streamed_completion:
            delta_content = chunk.choices[0].delta.content

            if delta_content is not None:
                line_buffer += delta_content

                if '\n' in line_buffer:
                    lines = line_buffer.split('\n')
                    for line in lines[:-1]:
                        print(NEON_GREEN + line + RESET_COLOR)
                        full_response += line + '\n'
                        log_line = f"{get_timestamp()} {bot_name}: {line}\n"  # Include timestamp in the log entry
                        #log_file.write(log_line)  # Log the line with the bot's name
                    line_buffer = lines[-1]

        if line_buffer:
            print(NEON_GREEN + line_buffer + RESET_COLOR)
            full_response += line_buffer
            log_line = f"{get_timestamp()} {bot_name}: {line_buffer}\n"  # Include timestamp in the log entry
            log_file.write(log_line)  # Log the remaining line

    return full_response

#Function to play audio using PyAudio
def play_audio(file_path):
    # Open the audio file
    wf = wave.open(file_path, 'rb')

    # Create a PyAudio instance
    p = pyaudio.PyAudio()

    # Open a stream to play audio
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    # Read and play audio data
    data = wf.readframes(1024)
    while data:
        stream.write(data)
        data = wf.readframes(1024)

    # Stop and close the stream and PyAudio instance
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
        chatbot_response = chatgpt_streamed(user_input, system_message, conversation_history, "Chatbot")
        conversation_history.append({"role": "assistant", "content": chatbot_response})
        
        # Process the chatbot's response and play the audio output
        prompt2 = chatbot_response
        style = "default"
        audio_file_pth2 = "resources\\example_reference.mp3"
        process_and_play(prompt2, style, audio_file_pth2)

        if len(conversation_history) > 20:
            conversation_history = conversation_history[-20:]

# Start the conversation
user_chatbot_conversation()