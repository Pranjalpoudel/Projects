import customtkinter as ctk
import google.generativeai as genai
import pyperclip
from tkinter import filedialog, messagebox
import os
from pypdf import PdfReader
import threading

# Configuration
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class NoteSummarizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AI Note Summarizer")
        self.geometry("900x700")

        # Grid layout configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1) # Input area (Textbox)
        self.grid_rowconfigure(6, weight=1) # Output area (Textbox)

        # Header
        self.header_label = ctk.CTkLabel(self, text="AI Note Summarizer", font=ctk.CTkFont(size=24, weight="bold"))
        self.header_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # API Key Input
        self.api_key_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.api_key_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        self.api_key_label = ctk.CTkLabel(self.api_key_frame, text="Gemini API Key:", font=ctk.CTkFont(size=14, weight="bold"))
        self.api_key_label.pack(side="top", anchor="w", padx=5, pady=(0, 5))
        
        self.api_key_entry = ctk.CTkEntry(self.api_key_frame, show="*", width=400, height=35, font=ctk.CTkFont(size=14), placeholder_text="Paste your Google Gemini API Key here...")
        self.api_key_entry.pack(side="top", fill="x", padx=5)
        # Updated the placeholder text to be more explicit
        self.api_key_entry.insert(0, "YOUR_API_KEY_HERE") 

        self.api_help_label = ctk.CTkLabel(self.api_key_frame, text="Don't have a key? Get one from Google AI Studio", font=ctk.CTkFont(size=12), text_color="gray")
        self.api_help_label.pack(side="top", anchor="w", padx=5, pady=(2, 0))

        # Input Area
        self.input_label = ctk.CTkLabel(self, text="Input Text (Paste or Load File):", anchor="w", font=ctk.CTkFont(weight="bold"))
        self.input_label.grid(row=2, column=0, padx=20, pady=(10, 0), sticky="w")

        self.input_textbox = ctk.CTkTextbox(self, width=800, height=150)
        self.input_textbox.grid(row=3, column=0, padx=20, pady=(5, 10), sticky="nsew")

        # Buttons
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=4, column=0, padx=20, pady=10)

        # Blue Button
        self.load_btn = ctk.CTkButton(self.button_frame, text="Load File (txt, pdf)", command=self.load_file, width=160, height=40, font=ctk.CTkFont(size=14, weight="bold"), fg_color="#1F6AA5", hover_color="#144870")
        self.load_btn.pack(side="left", padx=15)

        # Green Button
        self.summarize_btn = ctk.CTkButton(self.button_frame, text="Summarize", command=self.start_summarization_thread, fg_color="#2CC985", hover_color="#229966", width=160, height=40, font=ctk.CTkFont(size=14, weight="bold"))
        self.summarize_btn.pack(side="left", padx=15)

        # Red Button
        self.clear_btn = ctk.CTkButton(self.button_frame, text="Clear", command=self.clear_text, fg_color="#D32F2F", hover_color="#B71C1C", width=120, height=40, font=ctk.CTkFont(size=14, weight="bold"))
        self.clear_btn.pack(side="left", padx=15)

        # Output Area
        self.output_label = ctk.CTkLabel(self, text="Summary:", anchor="w")
        self.output_label.grid(row=5, column=0, padx=20, pady=(10, 0), sticky="w")

        self.output_textbox = ctk.CTkTextbox(self, width=800, height=200, state="disabled") # Read-only initially
        self.output_textbox.grid(row=6, column=0, padx=20, pady=(5, 10), sticky="nsew")

        # Copy Button
        self.copy_btn = ctk.CTkButton(self, text="Copy Summary", command=self.copy_summary)
        self.copy_btn.grid(row=7, column=0, padx=20, pady=20)

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("PDF Files", "*.pdf")])
        if not file_path:
            return

        try:
            text_content = ""
            if file_path.lower().endswith(".pdf"):
                text_content = self.extract_text_from_pdf(file_path)
            else:
                with open(file_path, "r", encoding="utf-8") as f:
                    text_content = f.read()

            self.input_textbox.delete("0.0", "end")
            self.input_textbox.insert("0.0", text_content)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")

    def extract_text_from_pdf(self, file_path):
        text = ""
        try:
            reader = PdfReader(file_path)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        except Exception as e:
            # Re-raise the exception to be caught in load_file
            raise Exception(f"Error reading PDF: {e}")
        return text

    def start_summarization_thread(self):
        # Run in a separate thread to keep UI responsive
        threading.Thread(target=self.summarize_text, daemon=True).start()

    def summarize_text(self):
        api_key = self.api_key_entry.get().strip()
        text = self.input_textbox.get("0.0", "end").strip()

        if not api_key or api_key == "YOUR_API_KEY_HERE":
            messagebox.showwarning("Missing API Key", "Please enter your Google Gemini API Key.")
            return

        if not text:
            messagebox.showwarning("Missing Input", "Please enter some text or load a file to summarize.")
            return

        self.summarize_btn.configure(state="disabled", text="Summarizing...")
        self.output_textbox.configure(state="normal")
        self.output_textbox.delete("0.0", "end")
        self.output_textbox.insert("0.0", "Generating summary...")
        self.output_textbox.configure(state="disabled")

        try:
            # Configure the API key
            genai.configure(api_key=api_key)

            # --- FIX APPLIED HERE ---
            # Corrected the model name from 'genai.generate_text' to 'gemini-2.5-flash'
            model = genai.GenerativeModel('gemini-2.5-flash')

            prompt = f"Please provide a concise and structured summary of the following text:\n\n{text}"
            
            # Use generate_content to get the response
            response = model.generate_content(prompt)
            
            summary = response.text

            self.output_textbox.configure(state="normal")
            self.output_textbox.delete("0.0", "end")
            self.output_textbox.insert("0.0", summary)
            self.output_textbox.configure(state="disabled")

        except Exception as e:
            self.output_textbox.configure(state="normal")
            self.output_textbox.delete("0.0", "end")
            self.output_textbox.insert("0.0", f"Error: {str(e)}")
            self.output_textbox.configure(state="disabled")
            messagebox.showerror("API Error", f"An error occurred: {e}. Check if your API key is correct and valid.")
        
        finally:
            self.summarize_btn.configure(state="normal", text="Summarize")

    def clear_text(self):
        self.input_textbox.delete("0.0", "end")
        self.output_textbox.configure(state="normal")
        self.output_textbox.delete("0.0", "end")
        self.output_textbox.configure(state="disabled")

    def copy_summary(self):
        summary = self.output_textbox.get("0.0", "end").strip()
        if summary:
            pyperclip.copy(summary)
            messagebox.showinfo("Copied", "Summary copied to clipboard!")
        else:
            messagebox.showwarning("Empty", "No summary to copy.")

if __name__ == "__main__":
    app = NoteSummarizerApp()
    app.mainloop()