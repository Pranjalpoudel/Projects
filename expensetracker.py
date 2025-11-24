import customtkinter as ctk
import sqlite3
from datetime import datetime
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS expenses
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  amount REAL,
                  category TEXT,
                  description TEXT,
                  date TEXT)''')
    conn.commit()
    conn.close()

# --- Main App Class ---
class ExpenseTrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Personal Expense Tracker")
        self.geometry("900x600")

        # Layout configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Expense Tracker", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.sidebar_button_1 = ctk.CTkButton(self.sidebar_frame, text="Add Expense", command=self.show_add_expense)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)

        self.sidebar_button_2 = ctk.CTkButton(self.sidebar_frame, text="View History", command=self.show_history)
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)

        self.sidebar_button_3 = ctk.CTkButton(self.sidebar_frame, text="Reports", command=self.show_reports)
        self.sidebar_button_3.grid(row=3, column=0, padx=20, pady=10)
        
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["System", "Dark", "Light"],
                                                               command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 20))


        # Main Content Area
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # Initialize Frames
        self.add_expense_frame = None
        self.history_frame = None
        self.reports_frame = None

        # Handle window closing to prevent "invalid command" errors
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Show default
        self.show_add_expense()

    def on_closing(self):
        self.quit()
        self.destroy()

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # --- Add Expense View ---
    def show_add_expense(self):
        self.clear_main_frame()
        
        title = ctk.CTkLabel(self.main_frame, text="Add New Expense", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=20)

        self.amount_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Amount")
        self.amount_entry.pack(pady=10, padx=20, fill="x")

        self.category_var = ctk.StringVar(value="Food")
        categories = ["Food", "Transport", "Bills", "Entertainment", "Shopping", "Other"]
        self.category_menu = ctk.CTkOptionMenu(self.main_frame, values=categories, variable=self.category_var)
        self.category_menu.pack(pady=10, padx=20, fill="x")

        self.desc_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Description")
        self.desc_entry.pack(pady=10, padx=20, fill="x")

        add_btn = ctk.CTkButton(self.main_frame, text="Save Expense", command=self.add_expense_to_db)
        add_btn.pack(pady=20)

    def add_expense_to_db(self):
        amount = self.amount_entry.get()
        category = self.category_var.get()
        description = self.desc_entry.get()
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not amount:
            messagebox.showerror("Error", "Please enter an amount")
            return

        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number")
            return

        conn = sqlite3.connect('expenses.db')
        c = conn.cursor()
        c.execute("INSERT INTO expenses (amount, category, description, date) VALUES (?, ?, ?, ?)",
                  (amount, category, description, date))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Expense added successfully!")
        self.amount_entry.delete(0, 'end')
        self.desc_entry.delete(0, 'end')

    # --- History View ---
    def show_history(self):
        self.clear_main_frame()
        
        title = ctk.CTkLabel(self.main_frame, text="Expense History", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=20)

        # Scrollable Frame for list
        scroll_frame = ctk.CTkScrollableFrame(self.main_frame)
        scroll_frame.pack(fill="both", expand=True)

        conn = sqlite3.connect('expenses.db')
        c = conn.cursor()
        c.execute("SELECT * FROM expenses ORDER BY date DESC LIMIT 50")
        rows = c.fetchall()
        conn.close()

        if not rows:
            ctk.CTkLabel(scroll_frame, text="No expenses found.").pack(pady=10)
            return

        # Headers
        header_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(header_frame, text="Date", width=150, anchor="w", font=("Arial", 12, "bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="Category", width=100, anchor="w", font=("Arial", 12, "bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="Desc", width=150, anchor="w", font=("Arial", 12, "bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="Amount", width=80, anchor="e", font=("Arial", 12, "bold")).pack(side="right", padx=5)

        for row in rows:
            # row: id, amount, category, description, date
            f = ctk.CTkFrame(scroll_frame)
            f.pack(fill="x", pady=2)
            
            date_str = row[4].split()[0] # Just date
            ctk.CTkLabel(f, text=date_str, width=150, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(f, text=row[2], width=100, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(f, text=row[3], width=150, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(f, text=f"${row[1]:.2f}", width=80, anchor="e").pack(side="right", padx=5)

    # --- Reports View ---
    def show_reports(self):
        self.clear_main_frame()
        plt.close('all') # Close any previous figures to prevent memory leaks
        
        title = ctk.CTkLabel(self.main_frame, text="Spending Analysis", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=20)

        conn = sqlite3.connect('expenses.db')
        c = conn.cursor()
        c.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
        data = c.fetchall()
        conn.close()

        if not data:
            ctk.CTkLabel(self.main_frame, text="No data to display.").pack(pady=20)
            return

        categories = [x[0] for x in data]
        amounts = [x[1] for x in data]

        # Matplotlib Figure
        fig, ax = plt.subplots(figsize=(6, 5), dpi=100)
        # Dark background for plot to match theme
        fig.patch.set_facecolor('#2b2b2b') 
        ax.set_facecolor('#2b2b2b')
        
        wedges, texts, autotexts = ax.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90, 
                                          textprops=dict(color="white"))
        
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.title("Expenses by Category", color="white")

        canvas = FigureCanvasTkAgg(fig, master=self.main_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


if __name__ == "__main__":
    ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
    
    init_db()
    app = ExpenseTrackerApp()
    app.mainloop()
