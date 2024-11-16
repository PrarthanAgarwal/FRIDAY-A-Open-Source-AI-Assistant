import datetime
import pytz
import requests
import json

class ChatHandler:
    def __init__(self, memory):
        self.memory = memory
        self.PINK = '\033[95m'
        self.RESET_COLOR = '\033[0m'
        
    def get_time_info(self, query):
        if "time" in query.lower():
            tz = pytz.timezone('Asia/Kolkata')
            return datetime.now(tz).strftime("It's %H:%M in India (IST)")
    
    def query_ollama(self, prompt):
        # Get personality context
        try:
            with open("Personality.txt", 'r', encoding='utf-8') as f:
                personality = f.read()
        except Exception as e:
            print(f"Error reading personality file: {e}")
            personality = ""
        
        # Get relevant context from memory
        relevant_memories = self.memory.search_memory(prompt)
        context = ""
        if relevant_memories:
            context = "Previous relevant conversations:\n"
            for mem in relevant_memories[-2:]:
                context += f"User: {mem['user']}\nAssistant: {mem['assistant']}\n"
            context += "\nBased on these previous conversations, "
        
        # Combine personality, context and prompt
        enhanced_prompt = f"{personality}\n\nContext: {context}\nUser: {prompt}"
        
        url = "http://localhost:11434/api/generate"
        headers = {"Content-Type": "application/json"}
        data = {
            "model": "llama3.2",
            "prompt": enhanced_prompt,
            "stream": True,
            "options": {
                "num_ctx": 1024,
                "temperature": 0.7,
                "top_p": 0.9
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, stream=True)
            response.raise_for_status()
            
            full_response = ""
            print(self.PINK, end='', flush=True)  # Start pink color
            
            for line in response.iter_lines():
                if line:
                    json_response = json.loads(line)
                    if 'response' in json_response:
                        chunk = json_response['response']
                        print(chunk, end='', flush=True)
                        full_response += chunk
            
            print(self.RESET_COLOR, end='', flush=True)  # Reset color
            return full_response
            
        except Exception as e:
            print(f"Error querying Ollama: {e}")
            return None 