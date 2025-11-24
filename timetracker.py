import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime
import csv

DB_NAME = "study_tracker.db"

def initialize_db():
    """Creates the study_sessions table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS study_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            date TEXT NOT NULL,
            duration_minutes INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def log_session(subject, duration_minutes):
    """Logs a new study session."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Normalize subject: remove extra spaces and title case
    subject = subject.strip().title()
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    cursor.execute('''
        INSERT INTO study_sessions (subject, date, duration_minutes)
        VALUES (?, ?, ?)
    ''', (subject, date_str, duration_minutes))
    conn.commit()
    conn.close()
    print(f"Logged: {subject} for {duration_minutes} minutes.")

def get_study_data():
    """Retrieves total study time per subject."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT subject, SUM(duration_minutes)
        FROM study_sessions
        GROUP BY subject
    ''')
    data = cursor.fetchall()
    conn.close()
    return data

def export_to_csv():
    """Exports all study sessions to a CSV file."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT subject, date, duration_minutes FROM study_sessions')
    data = cursor.fetchall()
    conn.close()

    filename = "study_data.csv"
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Subject", "Date", "Duration (Minutes)"])
        writer.writerows(data)
    
    print(f"Data exported successfully to {filename}")

def plot_study_stats():
    """Plots a bar chart of study time per subject."""
    data = get_study_data()
    
    if not data:
        print("No data to plot yet.")
        return

    subjects = [row[0] for row in data]
    durations = [row[1] for row in data]

    plt.figure(figsize=(10, 6))
    plt.bar(subjects, durations, color='skyblue')
    plt.xlabel('Subject')
    plt.ylabel('Total Study Time (minutes)')
    plt.title('Study Time Tracker')
    plt.show()

def clean_database():
    """Normalizes existing subject names in the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, subject FROM study_sessions")
    rows = cursor.fetchall()
    
    for row_id, subject in rows:
        normalized_subject = subject.strip().title()
        if subject != normalized_subject:
            cursor.execute("UPDATE study_sessions SET subject = ? WHERE id = ?", (normalized_subject, row_id))
    
    conn.commit()
    conn.close()

def main():
    initialize_db()
    clean_database() # Ensure data is clean on startup
    while True:
        print("\n--- Study Time Tracker ---")
        print("1. Log Study Session")
        print("2. View Progress Chart")
        print("3. Export to CSV")
        print("4. Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            subject = input("Enter subject name: ")
            try:
                duration = int(input("Enter duration (minutes): "))
                log_session(subject, duration)
            except ValueError:
                print("Invalid input. Duration must be a number.")
        elif choice == '2':
            plot_study_stats()
        elif choice == '3':
            export_to_csv()
        elif choice == '4':
            print("Keep up the good work! Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
