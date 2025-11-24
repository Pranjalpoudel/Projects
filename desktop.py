import customtkinter as ctk
import json
import os
import threading
import time
from datetime import datetime, timedelta
from plyer import notification
from tkinter import messagebox

# --- Configuration ---
DATA_FILE = "habits.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"last_opened": "", "habits": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- Main App ---
class HabitTrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Daily Habits")
        self.geometry("350x600")
        self.resizable(False, True)

        self.data = load_data()
        self.check_daily_reset()

        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # 1. Header
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        date_str = datetime.now().strftime("%A, %b %d")
        ctk.CTkLabel(self.header_frame, text="Daily Habits", font=ctk.CTkFont(size=24, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(self.header_frame, text=date_str, font=ctk.CTkFont(size=14), text_color="gray").pack(anchor="w")

        # 2. Progress Bar
        self.progress_bar = ctk.CTkProgressBar(self, height=10)
        self.progress_bar.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.progress_bar.set(0)

        # 3. Habit List (Scrollable)
        self.scroll_frame = ctk.CTkScrollableFrame(self, corner_radius=10)
        self.scroll_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")

        # 4. Add Button
        self.add_btn = ctk.CTkButton(self, text="+ Add New Habit", command=self.open_add_dialog, height=40)
        self.add_btn.grid(row=3, column=0, padx=20, pady=20, sticky="ew")

        self.refresh_list()
        
        # Start Reminder Thread
        self.running = True
        threading.Thread(target=self.reminder_loop, daemon=True).start()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def check_daily_reset(self):
        today = datetime.now().strftime("%Y-%m-%d")
        last_opened = self.data.get("last_opened", "")

        if last_opened != today:
            # New Day Logic
            for habit in self.data["habits"]:
                if habit["completed"]:
                    # If completed yesterday (or whenever last opened if we assume daily usage), increment streak
                    # Ideally we check if last_opened was yesterday. For simplicity, if completed, we keep streak.
                    # If not completed, reset streak? 
                    # Let's do a simpler logic: If not completed yesterday, reset streak.
                    pass 
                else:
                    # Missed a day -> Reset streak
                    # Only if last_opened was strictly yesterday or before. 
                    # If first time run, streak is 0.
                    if last_opened: # If not first run
                         habit["streak"] = 0
                
                habit["completed"] = False
            
            self.data["last_opened"] = today
            save_data(self.data)

    def refresh_list(self):
        # Clear existing
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        habits = self.data["habits"]
        total = len(habits)
        completed_count = 0

        for i, habit in enumerate(habits):
            self.create_habit_card(habit, i)
            if habit["completed"]:
                completed_count += 1

        # Update Progress
        if total > 0:
            self.progress_bar.set(completed_count / total)
        else:
            self.progress_bar.set(0)

    def create_habit_card(self, habit, index):
        card = ctk.CTkFrame(self.scroll_frame, fg_color="#2b2b2b")
        card.pack(fill="x", pady=5)

        # Checkbox
        var = ctk.BooleanVar(value=habit["completed"])
        cb = ctk.CTkCheckBox(card, text="", variable=var, width=24, checkbox_width=24, corner_radius=12,
                             command=lambda: self.toggle_habit(index, var.get()))
        cb.pack(side="left", padx=10, pady=10)

        # Text Info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True)
        
        name_lbl = ctk.CTkLabel(info_frame, text=habit["name"], font=ctk.CTkFont(size=14, weight="bold"))
        name_lbl.pack(anchor="w")
        
        details_text = f"Goal: {habit['goal']}"
        if habit.get("reminder"):
            details_text += f" | ⏰ {habit['reminder']}"
        
        goal_lbl = ctk.CTkLabel(info_frame, text=details_text, font=ctk.CTkFont(size=11), text_color="gray")
        goal_lbl.pack(anchor="w")

        # Streak
        streak_lbl = ctk.CTkLabel(card, text=f"🔥 {habit['streak']}", font=ctk.CTkFont(size=14), text_color="#FFA500")
        streak_lbl.pack(side="right", padx=10)

        # Delete (Right click or small button? Let's use small button)
        del_btn = ctk.CTkButton(card, text="×", width=20, height=20, fg_color="transparent", text_color="red", hover_color="#440000",
                                command=lambda: self.delete_habit(index))
        del_btn.pack(side="right", padx=(0, 5))

    def toggle_habit(self, index, completed):
        habit = self.data["habits"][index]
        habit["completed"] = completed
        
        if completed:
            habit["streak"] += 1
        else:
            habit["streak"] = max(0, habit["streak"] - 1)
            
        save_data(self.data)
        self.refresh_list()

    def delete_habit(self, index):
        del self.data["habits"][index]
        save_data(self.data)
        self.refresh_list()

    def open_add_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Habit")
        dialog.geometry("300x350")
        dialog.attributes("-topmost", True)

        ctk.CTkLabel(dialog, text="Habit Name").pack(pady=(20, 5))
        name_entry = ctk.CTkEntry(dialog, placeholder_text="e.g. Drink Water")
        name_entry.pack(pady=5, padx=20, fill="x")

        ctk.CTkLabel(dialog, text="Goal").pack(pady=(10, 5))
        goal_entry = ctk.CTkEntry(dialog, placeholder_text="e.g. 2 Liters")
        goal_entry.pack(pady=5, padx=20, fill="x")

        ctk.CTkLabel(dialog, text="Reminder Time (HH:MM) [Optional]").pack(pady=(10, 5))
        time_entry = ctk.CTkEntry(dialog, placeholder_text="e.g. 14:30")
        time_entry.pack(pady=5, padx=20, fill="x")

        def save():
            name = name_entry.get()
            goal = goal_entry.get()
            reminder = time_entry.get()
            
            if not name:
                return

            new_habit = {
                "name": name,
                "goal": goal if goal else "Daily",
                "reminder": reminder,
                "completed": False,
                "streak": 0
            }
            self.data["habits"].append(new_habit)
            save_data(self.data)
            self.refresh_list()
            dialog.destroy()

        ctk.CTkButton(dialog, text="Add Habit", command=save).pack(pady=30)

    def reminder_loop(self):
        while self.running:
            now = datetime.now().strftime("%H:%M")
            # Check every habit
            for habit in self.data["habits"]:
                if habit.get("reminder") == now and not habit["completed"]:
                    # Send Notification
                    try:
                        notification.notify(
                            title=f"Reminder: {habit['name']}",
                            message=f"Don't forget to {habit['name']}! Goal: {habit['goal']}",
                            app_name="Habit Tracker",
                            timeout=10
                        )
                    except Exception as e:
                        print(f"Notification error: {e}")
                    
                    # Prevent spamming notification for the whole minute
                    time.sleep(60) 
            
            time.sleep(10) # Check every 10 seconds

    def on_closing(self):
        self.running = False
        self.quit()
        self.destroy()

if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("green")
    
    app = HabitTrackerApp()
    app.mainloop()
