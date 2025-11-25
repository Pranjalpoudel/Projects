import customtkinter as ctk
import json
import os
import threading
from datetime import datetime
import requests
import time

# --- Configuration ---
CHAT_HISTORY_FILE = "chat_history.json"
# Using multiple free APIs for better responses
APIS = [
    {"url": "https://api.deepseek.com/v1/chat/completions", "type": "chat"},
    {"url": "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2", "type": "hf"},
    {"url": "https://api-inference.huggingface.co/models/google/flan-t5-large", "type": "hf"},
]

def load_chat_history():
    if os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_chat_history(history):
    with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)

# --- Chatbot App ---
class ChatbotApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Local Chatbot Assistant")
        self.geometry("800x600")
        
        self.chat_history = load_chat_history()
        self.is_generating = False

        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 1. Header with model selector
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent", height=60)
        self.header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        self.header_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(self.header_frame, text="🤖 AI Assistant", 
                    font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, sticky="w")
        
        # Clear button
        self.clear_btn = ctk.CTkButton(self.header_frame, text="Clear Chat", command=self.clear_chat, 
                                      width=100, fg_color="#d32f2f", hover_color="#b71c1c")
        self.clear_btn.grid(row=0, column=1, sticky="e")

        # 2. Chat Display Area (Scrollable)
        self.chat_frame = ctk.CTkScrollableFrame(self, corner_radius=10)
        self.chat_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.chat_frame.grid_columnconfigure(0, weight=1)

        # 3. Input Area
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.input_box = ctk.CTkTextbox(self.input_frame, height=80, wrap="word")
        self.input_box.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.input_box.bind("<Return>", self.on_enter_key)
        self.input_box.bind("<Shift-Return>", lambda e: None)  # Allow newline with Shift+Enter
        
        self.send_btn = ctk.CTkButton(self.input_frame, text="Send", command=self.send_message, 
                                     width=100, height=80, font=ctk.CTkFont(size=16, weight="bold"))
        self.send_btn.grid(row=0, column=1)

        # Status label
        self.status_label = ctk.CTkLabel(self.input_frame, text="Ready", 
                                        font=ctk.CTkFont(size=11), text_color="gray")
        self.status_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(5, 0))

        # Load previous chat history
        self.load_previous_messages()

    def load_previous_messages(self):
        for msg in self.chat_history:
            self.display_message(msg["role"], msg["content"], save=False)

    def display_message(self, role, content, save=True):
        # Create message bubble
        is_user = role == "user"
        msg_frame = ctk.CTkFrame(self.chat_frame, 
                                fg_color="#1e3a5f" if is_user else "#2d2d2d", 
                                corner_radius=15)
        msg_frame.grid(row=len(self.chat_frame.winfo_children()), column=0, 
                      sticky="e" if is_user else "w", 
                      pady=8, 
                      padx=(100 if is_user else 10, 10 if is_user else 100))
        
        # Header with role and timestamp
        header_frame = ctk.CTkFrame(msg_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=12, pady=(8, 4))
        
        role_text = "You" if is_user else "🤖 AI Assistant"
        role_color = "#64b5f6" if is_user else "#81c784"
        ctk.CTkLabel(header_frame, text=role_text, 
                    font=ctk.CTkFont(size=12, weight="bold"), 
                    text_color=role_color).pack(side="left")
        
        time_text = datetime.now().strftime("%I:%M %p")
        ctk.CTkLabel(header_frame, text=time_text, 
                    font=ctk.CTkFont(size=10), 
                    text_color="#888").pack(side="right")
        
        # Message content - using CTkLabel for better text display
        msg_container = ctk.CTkFrame(msg_frame, fg_color="transparent")
        msg_container.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        
        # Split content into lines for better display
        lines = content.split('\n')
        for line in lines:
            if line.strip():  # Only display non-empty lines
                label = ctk.CTkLabel(msg_container, 
                                   text=line, 
                                   font=ctk.CTkFont(size=13),
                                   wraplength=500,
                                   justify="left",
                                   anchor="w")
                label.pack(fill="x", pady=2, anchor="w")
            else:
                # Add spacing for empty lines
                ctk.CTkFrame(msg_container, height=5, fg_color="transparent").pack()
        
        # Auto-scroll to bottom
        self.chat_frame._parent_canvas.yview_moveto(1.0)
        self.update()
        
        if save:
            self.chat_history.append({
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            })
            save_chat_history(self.chat_history)

    def on_enter_key(self, event):
        # Send on Enter, newline on Shift+Enter
        if not event.state & 0x1:  # Check if Shift is not pressed
            self.send_message()
            return "break"  # Prevent newline

    def send_message(self):
        message = self.input_box.get("1.0", "end-1c").strip()
        if not message or self.is_generating:
            return
        
        # Display user message
        self.display_message("user", message)
        self.input_box.delete("1.0", "end")
        
        # Get AI response in background thread
        self.is_generating = True
        self.send_btn.configure(state="disabled", text="...")
        self.status_label.configure(text="Generating response...")
        
        threading.Thread(target=self.get_ai_response, args=(message,), daemon=True).start()

    def get_ai_response(self, user_message):
        response_text = ""
        try:
            # Show typing indicator
            self.show_typing_indicator()
            
            # Try different AI APIs
            response_text = self.get_smart_response(user_message)
            
            if not response_text:
                response_text = "I apologize, but I'm having trouble generating a response right now. Please try asking your question differently."
            
        except Exception as e:
            response_text = f"Sorry, I encountered an error: {str(e)}\n\nPlease try again."
        finally:
            # Remove typing indicator
            self.after(0, self.remove_typing_indicator)
            # Display response
            self.after(0, lambda: self.display_message("assistant", response_text))
            self.after(0, lambda: self.status_label.configure(text="Ready"))
            self.is_generating = False
            self.after(0, lambda: self.send_btn.configure(state="normal", text="Send"))
    
    def show_typing_indicator(self):
        """Show typing animation"""
        self.typing_frame = ctk.CTkFrame(self.chat_frame, fg_color="#2d2d2d", corner_radius=15)
        self.typing_frame.grid(row=len(self.chat_frame.winfo_children()), column=0, 
                              sticky="w", pady=8, padx=(10, 100))
        
        typing_label = ctk.CTkLabel(self.typing_frame, 
                                    text="🤖 AI is thinking...", 
                                    font=ctk.CTkFont(size=12),
                                    text_color="#81c784")
        typing_label.pack(padx=15, pady=10)
        
        self.chat_frame._parent_canvas.yview_moveto(1.0)
        self.update()
    
    def remove_typing_indicator(self):
        """Remove typing indicator"""
        if hasattr(self, 'typing_frame'):
            self.typing_frame.destroy()
            delattr(self, 'typing_frame')
    
    def get_smart_response(self, message):
        """Try multiple AI services for best response"""
        # Build conversation context
        context = self.build_text_context()
        
        # Try HuggingFace inference API with better models
        response = self.try_huggingface_api(message, context)
        if response:
            return response
        
        # Fallback to OpenRouter (free tier)
        response = self.try_openrouter(message, context)
        if response:
            return response
        
        # Final fallback - smart rule-based response
        return self.get_contextual_response(message)
    
    def try_huggingface_api(self, message, context):
        """Try HuggingFace models"""
        try:
            # Use Mistral model for better responses
            url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
            
            prompt = f"{context}\n\nUser: {message}\nAssistant:"
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 256,
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "return_full_text": False
                }
            }
            
            response = requests.post(url, json=payload, timeout=25)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    text = result[0].get("generated_text", "")
                    # Clean up the response
                    text = text.replace(prompt, "").strip()
                    if text and len(text) > 10:
                        return text
            
            # Try FLAN-T5 as backup
            url2 = "https://api-inference.huggingface.co/models/google/flan-t5-large"
            payload2 = {"inputs": message}
            response2 = requests.post(url2, json=payload2, timeout=20)
            
            if response2.status_code == 200:
                result2 = response2.json()
                if isinstance(result2, list) and len(result2) > 0:
                    return result2[0].get("generated_text", "").strip()
                    
        except Exception as e:
            print(f"HF API Error: {e}")
        
        return None
    
    def try_openrouter(self, message, context):
        """Try OpenRouter free models"""
        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:3000",
            }
            
            messages = [
                {"role": "system", "content": "You are a helpful AI assistant. Provide clear, concise, and friendly responses."},
                {"role": "user", "content": message}
            ]
            
            payload = {
                "model": "google/gemma-7b-it:free",
                "messages": messages
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=25)
            
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"].strip()
                    
        except Exception as e:
            print(f"OpenRouter Error: {e}")
        
        return None
    
    def get_contextual_response(self, message):
        """Intelligent fallback responses"""
        import re
        msg_lower = message.lower()
        
        # Greetings
        if re.search(r'^(hi|hello|hey|greetings|good morning|good evening)', msg_lower):
            return "Hello! I'm your AI assistant. How can I help you today? Feel free to ask me anything!"
        
        # Questions about capabilities
        if re.search(r'(what can you|help me|assist|do for me)', msg_lower):
            return """I'm an AI assistant that can help you with:

• Answering questions on various topics
• Providing explanations and information
• Having conversations and discussions
• Helping with problem-solving
• Creative writing and brainstorming
• General knowledge and advice

Just ask me anything you'd like to know!"""
        
        # Time/Date
        if re.search(r'(time|date|today|what day)', msg_lower):
            now = datetime.now()
            return f"Current time: {now.strftime('%I:%M %p')}\nDate: {now.strftime('%A, %B %d, %Y')}"
        
        # Thank you
        if re.search(r'(thank|thanks|thx|appreciate)', msg_lower):
            return "You're very welcome! I'm happy to help. Feel free to ask if you need anything else! 😊"
        
        # Goodbye
        if re.search(r'(bye|goodbye|see you|later)', msg_lower):
            return "Goodbye! It was nice chatting with you. Come back anytime! 👋"
        
        # Default intelligent response
        return f"""I understand you're asking about: "{message}"

While I'm having some connectivity issues with my advanced AI models right now, I'm still here to help! Could you please:

1. Rephrase your question
2. Ask something more specific
3. Or try asking in a different way

I'll do my best to assist you!"""
    
    def build_text_context(self):
        """Build simple text context from recent messages"""
        recent = self.chat_history[-4:] if len(self.chat_history) > 4 else self.chat_history
        context_parts = []
        
        for msg in recent:
            role = "User" if msg["role"] == "user" else "Assistant"
            context_parts.append(f"{role}: {msg['content']}")
        
        return "\n".join(context_parts) if context_parts else ""

    def build_context(self, max_messages=6):
        # Get last N messages for context
        recent = self.chat_history[-max_messages:] if len(self.chat_history) > max_messages else self.chat_history
        context_parts = []
        
        for msg in recent:
            role = "User" if msg["role"] == "user" else "Assistant"
            context_parts.append(f"{role}: {msg['content']}")
        
        return "\n".join(context_parts)



    def clear_chat(self):
        # Clear chat display
        for widget in self.chat_frame.winfo_children():
            widget.destroy()
        
        # Clear history
        self.chat_history = []
        save_chat_history(self.chat_history)
        self.status_label.configure(text="Chat cleared")

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    app = ChatbotApp()
    app.mainloop()
