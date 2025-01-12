import tkinter as tk
from tkinter import filedialog, messagebox
import csv

def longest_match(sequence, subsequence):
    longest_run = 0
    subsequence_length = len(subsequence)
    sequence_length = len(sequence)

    for i in range(sequence_length):
        count = 0
        while True:
            start = i + count * subsequence_length
            end = start + subsequence_length
            if sequence[start:end] == subsequence:
                count += 1
            else:
                break
        longest_run = max(longest_run, count)

    return longest_run


def dna_match(database_file, sequence_file):
    try:
        with open(database_file) as file:
            reader = csv.DictReader(file)
            rows = [row for row in reader]

        with open(sequence_file) as file:
            dna = file.read()

        results = dict(rows[1])
        del results["name"]

        for i in results:
            results[i] = str(longest_match(dna, i))

        for row in rows:
            for key in results:
                if row[key] != results[key]:
                    break
            else:
                return row['name']
        return "No match"
    except FileNotFoundError:
        return "File not found"


def browse_file(entry):
    filename = filedialog.askopenfilename(title="Select a file", filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt")])
    if filename:
        entry.config(text=filename)


def run_program():
    db_file = db_button.cget("text")
    seq_file = seq_button.cget("text")

    if not db_file or not seq_file:
        messagebox.showerror("Error", "Both files must be selected.")
        return

    result.set("Processing...")
    root.update_idletasks()  # Refresh GUI to show loading message

    result_text = dna_match(db_file, seq_file)
    result.set(f"Result: {result_text}")


# Set up GUI
root = tk.Tk()
root.title("DNA Matcher")
root.geometry("600x350")
root.config(bg="#f0f0f0")

# Frame for content
frame = tk.Frame(root, bg="#f0f0f0")
frame.pack(padx=20, pady=20)

# Title label
title_label = tk.Label(frame, text="DNA Profile Matcher", font=("Helvetica", 18, "bold"), bg="#f0f0f0", fg="#4CAF50")
title_label.grid(row=0, column=0, columnspan=2, pady=10)

# Database file button
db_button = tk.Label(frame, text="Select Database File (CSV)", font=("Helvetica", 12), bg="#4CAF50", fg="white", width=30, height=2)
db_button.grid(row=1, column=0, columnspan=2, pady=10)
db_button.config(relief="raised", anchor="w", padx=10)
db_button.bind("<Button-1>", lambda e: browse_file(db_button))

# DNA sequence file button
seq_button = tk.Label(frame, text="Select DNA Sequence File (TXT)", font=("Helvetica", 12), bg="#4CAF50", fg="white", width=30, height=2)
seq_button.grid(row=2, column=0, columnspan=2, pady=10)
seq_button.config(relief="raised", anchor="w", padx=10)
seq_button.bind("<Button-1>", lambda e: browse_file(seq_button))

# Result area
result = tk.StringVar()
result.set("Result will be displayed here")
result_label = tk.Label(frame, textvariable=result, font=("Helvetica", 12), bg="#f0f0f0", fg="#333")
result_label.grid(row=3, column=0, columnspan=2, pady=20)

# Run button
run_button = tk.Button(frame, text="Run DNA Matcher", command=run_program, font=("Helvetica", 12, "bold"), bg="#4CAF50", fg="white")
run_button.grid(row=4, column=0, columnspan=2, pady=20)

# Start the GUI
root.mainloop()
