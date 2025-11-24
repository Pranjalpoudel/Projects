import customtkinter as ctk
import requests
from geopy.geocoders import Nominatim
from datetime import datetime
import threading
import json
import os

# --- Configuration ---
CONFIG_FILE = "weather_config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"api_key": "", "last_city": "London"}

def save_config(api_key, city):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"api_key": api_key, "last_city": city}, f)

# --- Main App ---
class WeatherWidget(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Weather & AQI")
        self.geometry("300x350")
        self.resizable(False, False)

        self.config = load_config()
        self.api_key = self.config.get("api_key", "")
        self.current_city = self.config.get("last_city", "London")

        # UI Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) # Main content expands

        # 1. Search Bar
        self.search_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.search_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        
        self.city_entry = ctk.CTkEntry(self.search_frame, placeholder_text="City Name")
        self.city_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.city_entry.insert(0, self.current_city)
        
        self.search_btn = ctk.CTkButton(self.search_frame, text="🔍", width=40, command=self.start_fetch_thread)
        self.search_btn.pack(side="right")

        # 2. API Key Input (Hidden if set)
        self.api_frame = ctk.CTkFrame(self, fg_color="transparent")
        if not self.api_key:
            self.api_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        self.api_entry = ctk.CTkEntry(self.api_frame, placeholder_text="Enter OpenWeatherMap API Key")
        self.api_entry.pack(fill="x")
        if self.api_key:
            self.api_entry.insert(0, self.api_key)

        # 3. Weather Display
        self.weather_frame = ctk.CTkFrame(self, corner_radius=15)
        self.weather_frame.grid(row=2, column=0, padx=15, pady=10, sticky="nsew")
        
        self.temp_label = ctk.CTkLabel(self.weather_frame, text="--°C", font=ctk.CTkFont(size=40, weight="bold"))
        self.temp_label.pack(pady=(20, 5))
        
        self.desc_label = ctk.CTkLabel(self.weather_frame, text="Condition", font=ctk.CTkFont(size=16))
        self.desc_label.pack(pady=5)

        self.details_label = ctk.CTkLabel(self.weather_frame, text="Humidity: --% | Wind: -- m/s", text_color="gray")
        self.details_label.pack(pady=5)

        # 4. AQI Display
        self.aqi_frame = ctk.CTkFrame(self, height=50, corner_radius=10, fg_color="#FFFFFF")
        self.aqi_frame.grid(row=3, column=0, padx=15, pady=(0, 15), sticky="ew")
        
        self.aqi_label = ctk.CTkLabel(self.aqi_frame, text="AQI: --", font=ctk.CTkFont(size=16, weight="bold"))
        self.aqi_label.pack(pady=10)

        # Initial Load
        if self.api_key:
            self.start_fetch_thread()

    def start_fetch_thread(self):
        city = self.city_entry.get()
        api_key = self.api_entry.get()
        
        if not city or not api_key:
            return

        self.api_key = api_key
        self.search_btn.configure(state="disabled")
        threading.Thread(target=self.fetch_data, args=(city, api_key), daemon=True).start()

    def fetch_data(self, city, api_key):
        try:
            # 1. Get Coordinates
            geolocator = Nominatim(user_agent="weather_widget_app")
            location = geolocator.geocode(city)
            
            if not location:
                self.update_ui_error("City not found")
                return

            lat, lon = location.latitude, location.longitude

            # 2. Get Weather
            weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
            w_res = requests.get(weather_url).json()
            
            if w_res.get("cod") != 200:
                self.update_ui_error(w_res.get("message", "API Error"))
                return

            # 3. Get AQI
            aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"
            a_res = requests.get(aqi_url).json()

            # Process Data
            temp = w_res["main"]["temp"]
            desc = w_res["weather"][0]["description"].title()
            humidity = w_res["main"]["humidity"]
            wind = w_res["wind"]["speed"]
            
            aqi_val = a_res["list"][0]["main"]["aqi"]
            aqi_text = ["Good", "Fair", "Moderate", "Poor", "Very Poor"][aqi_val - 1]
            aqi_color = ["#00e400", "#ffff00", "#ff7e00", "#ff0000", "#7e0023"][aqi_val - 1]

            # Update UI (Thread safe)
            self.after(0, lambda: self.update_ui_success(city, temp, desc, humidity, wind, aqi_val, aqi_text, aqi_color))
            
            # Save successful config
            save_config(api_key, city)

        except Exception as e:
            self.after(0, lambda: self.update_ui_error(str(e)))

    def update_ui_success(self, city, temp, desc, humidity, wind, aqi_val, aqi_text, aqi_color):
        self.search_btn.configure(state="normal")
        self.api_frame.grid_forget() # Hide API input on success
        
        self.temp_label.configure(text=f"{temp:.1f}°C")
        self.desc_label.configure(text=f"{desc}")
        self.details_label.configure(text=f"Humidity: {humidity}% | Wind: {wind} m/s")
        
        self.aqi_label.configure(text=f"AQI: {aqi_val} ({aqi_text})", text_color=aqi_color if aqi_val != 2 else "black") 
        # Yellow text on dark bg is hard to read, keep it readable or change bg. 
        # Let's just set the text color for now.
        
        self.title(f"Weather: {city}")

    def update_ui_error(self, message):
        self.search_btn.configure(state="normal")
        self.desc_label.configure(text=f"Error: {message}")

if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    
    app = WeatherWidget()
    app.mainloop()
