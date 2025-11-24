import customtkinter as ctk
import psutil
import GPUtil
import threading
import time
from datetime import datetime

class PCHealthApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PC Health Monitor")
        self.geometry("800x500")
        self.resizable(True, True)

        # Layout
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1), weight=1)

        # --- CPU Frame ---
        self.cpu_frame = ctk.CTkFrame(self)
        self.cpu_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(self.cpu_frame, text="CPU", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)
        
        self.cpu_usage_label = ctk.CTkLabel(self.cpu_frame, text="0%", font=ctk.CTkFont(size=40, weight="bold"), text_color="#3B8ED0")
        self.cpu_usage_label.pack(pady=10)
        
        self.cpu_bar = ctk.CTkProgressBar(self.cpu_frame, width=200)
        self.cpu_bar.pack(pady=10)
        self.cpu_bar.set(0)
        
        self.cpu_info_label = ctk.CTkLabel(self.cpu_frame, text="Cores: -- | Threads: --")
        self.cpu_info_label.pack(pady=5)

        # --- RAM Frame ---
        self.ram_frame = ctk.CTkFrame(self)
        self.ram_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(self.ram_frame, text="RAM", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)
        
        self.ram_usage_label = ctk.CTkLabel(self.ram_frame, text="0%", font=ctk.CTkFont(size=40, weight="bold"), text_color="#E04F5F")
        self.ram_usage_label.pack(pady=10)
        
        self.ram_bar = ctk.CTkProgressBar(self.ram_frame, width=200, progress_color="#E04F5F")
        self.ram_bar.pack(pady=10)
        self.ram_bar.set(0)
        
        self.ram_info_label = ctk.CTkLabel(self.ram_frame, text="Used: -- GB / Total: -- GB")
        self.ram_info_label.pack(pady=5)

        # --- GPU Frame ---
        self.gpu_frame = ctk.CTkFrame(self)
        self.gpu_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(self.gpu_frame, text="GPU", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)
        
        self.gpu_name_label = ctk.CTkLabel(self.gpu_frame, text="No GPU Detected", font=ctk.CTkFont(size=12))
        self.gpu_name_label.pack(pady=5)
        
        self.gpu_usage_label = ctk.CTkLabel(self.gpu_frame, text="0%", font=ctk.CTkFont(size=40, weight="bold"), text_color="#2CC985")
        self.gpu_usage_label.pack(pady=10)
        
        self.gpu_bar = ctk.CTkProgressBar(self.gpu_frame, width=200, progress_color="#2CC985")
        self.gpu_bar.pack(pady=10)
        self.gpu_bar.set(0)
        
        self.gpu_temp_label = ctk.CTkLabel(self.gpu_frame, text="Temp: --°C | VRAM: --%")
        self.gpu_temp_label.pack(pady=5)

        # --- Disk & Network Frame ---
        self.disk_frame = ctk.CTkFrame(self)
        self.disk_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(self.disk_frame, text="System", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)
        
        self.disk_label = ctk.CTkLabel(self.disk_frame, text="Disk Usage: --%", font=ctk.CTkFont(size=16))
        self.disk_label.pack(pady=5)
        
        self.disk_bar = ctk.CTkProgressBar(self.disk_frame, width=200, progress_color="#FFA500")
        self.disk_bar.pack(pady=5)
        self.disk_bar.set(0)
        
        self.net_label = ctk.CTkLabel(self.disk_frame, text="Net: ↓ 0 KB/s  ↑ 0 KB/s", font=ctk.CTkFont(size=14))
        self.net_label.pack(pady=20)

        # Start Monitoring
        self.running = True
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Initial static info
        self.update_static_info()
        
        # Start thread
        threading.Thread(target=self.update_stats, daemon=True).start()

    def update_static_info(self):
        # CPU Info
        cores = psutil.cpu_count(logical=False)
        threads = psutil.cpu_count(logical=True)
        self.cpu_info_label.configure(text=f"Cores: {cores} | Threads: {threads}")

        # GPU Name (if available)
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                self.gpu_name_label.configure(text=gpus[0].name)
        except:
            pass

    def update_stats(self):
        last_net_io = psutil.net_io_counters()
        last_time = time.time()
        gpu_enabled = True # Flag to disable GPU monitoring if it fails

        while self.running:
            try:
                # CPU
                cpu_percent = psutil.cpu_percent(interval=None)
                
                # RAM
                ram = psutil.virtual_memory()
                ram_percent = ram.percent
                ram_used = round(ram.used / (1024**3), 1)
                ram_total = round(ram.total / (1024**3), 1)

                # Disk
                try:
                    disk = psutil.disk_usage('C:') # Monitor C drive
                    disk_percent = disk.percent
                except:
                    disk_percent = 0

                # Network Speed
                try:
                    net_io = psutil.net_io_counters()
                    curr_time = time.time()
                    time_delta = curr_time - last_time
                    
                    if time_delta > 0:
                        down_speed = (net_io.bytes_recv - last_net_io.bytes_recv) / time_delta / 1024 # KB/s
                        up_speed = (net_io.bytes_sent - last_net_io.bytes_sent) / time_delta / 1024 # KB/s
                    else:
                        down_speed, up_speed = 0, 0
                    
                    last_net_io = net_io
                    last_time = curr_time
                except:
                    down_speed, up_speed = 0, 0

                # GPU
                gpu_load = 0
                gpu_temp = 0
                gpu_mem = 0
                
                if gpu_enabled:
                    try:
                        gpus = GPUtil.getGPUs()
                        if gpus:
                            gpu = gpus[0]
                            gpu_load = gpu.load * 100
                            gpu_temp = gpu.temperature
                            gpu_mem = gpu.memoryUtil * 100
                    except Exception as e:
                        print(f"GPU Monitoring Failed (Disabling): {e}")
                        gpu_enabled = False

                # Update UI (Thread safe)
                if self.running:
                    self.after(0, lambda: self.update_ui(cpu_percent, ram_percent, ram_used, ram_total, 
                                                       disk_percent, down_speed, up_speed, 
                                                       gpu_load, gpu_temp, gpu_mem))
                
                time.sleep(1)
            except Exception as e:
                print(f"Error in main loop: {e}")
                time.sleep(1)

    def update_ui(self, cpu, ram_p, ram_u, ram_t, disk, down, up, gpu_l, gpu_t, gpu_m):
        # CPU
        self.cpu_usage_label.configure(text=f"{cpu}%")
        self.cpu_bar.set(cpu / 100)
        
        # RAM
        self.ram_usage_label.configure(text=f"{ram_p}%")
        self.ram_bar.set(ram_p / 100)
        self.ram_info_label.configure(text=f"Used: {ram_u} GB / Total: {ram_t} GB")
        
        # Disk
        self.disk_label.configure(text=f"Disk (C:): {disk}%")
        self.disk_bar.set(disk / 100)
        
        # Network
        self.net_label.configure(text=f"Net: ↓ {down:.1f} KB/s  ↑ {up:.1f} KB/s")
        
        # GPU
        self.gpu_usage_label.configure(text=f"{gpu_l:.0f}%")
        self.gpu_bar.set(gpu_l / 100)
        self.gpu_temp_label.configure(text=f"Temp: {gpu_t}°C | VRAM: {gpu_m:.0f}%")

    def on_closing(self):
        self.running = False
        self.quit()
        self.destroy()

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    
    app = PCHealthApp()
    app.mainloop()
