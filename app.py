import os
import tkinter as tk
from tkinter import scrolledtext
import subprocess
from dotenv import load_dotenv
import threading
import sys

# Load environment variables from .env file if it exists
load_dotenv()


# Function to save environment variables to .env file
def save_env_variables():
    with open(".env", "w") as f:
        f.write(f"LOGIN_EMAIL={email_var.get()}\n")
        f.write(f"LOGIN_PASSWORD={password_var.get()}\n")
        f.write(f"COLLECTION={collection_var.get()}\n")
        f.write(f"MAIN_DIR={main_dir_var.get()}\n")
        f.write(f"NUMBER_OF_PHOTOS={num_photos_var.get()}\n")


# Function to run the script
def run_script():
    save_env_variables()
    log_text.config(state=tk.NORMAL, bg="white", fg="black")
    log_text.delete("1.0", tk.END)  # Delete previous logs
    log_text.config(state=tk.DISABLED)
    run_button.config(state=tk.DISABLED)

    def target():
        process = subprocess.Popen(
            [sys.executable, "script.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )
        for line in iter(process.stdout.readline, ""):
            log_text.config(state=tk.NORMAL)
            log_text.insert(tk.END, line)
            log_text.config(state=tk.DISABLED)
            log_text.yview(tk.END)
        process.stdout.close()
        process.wait()

        rc = process.returncode
        if rc == 0:
            log_text.config(state=tk.NORMAL)
            log_text.insert(tk.END, "\nProcess completed successfully!")
            log_text.config(state=tk.DISABLED)
            log_text.yview(tk.END)
            log_text.config(bg="lightgreen")
        else:
            log_text.config(state=tk.NORMAL)
            log_text.insert(tk.END, "\nProcess encountered an error.")
            log_text.config(state=tk.DISABLED)
            log_text.yview(tk.END)
            log_text.config(bg="red")
        run_button.config(state=tk.NORMAL)

    threading.Thread(target=target).start()


# Create the main window
root = tk.Tk()
root.title("BlueCanvas Upload Application")

# Create input fields for environment variables
tk.Label(root, text="Login Email:").grid(row=0, column=0, sticky=tk.W)
email_var = tk.StringVar(value=os.getenv("LOGIN_EMAIL"))
tk.Entry(root, textvariable=email_var).grid(row=0, column=1)

tk.Label(root, text="Login Password:").grid(row=1, column=0, sticky=tk.W)
password_var = tk.StringVar(value=os.getenv("LOGIN_PASSWORD"))
tk.Entry(root, textvariable=password_var, show="*").grid(row=1, column=1)

tk.Label(root, text="Collection:").grid(row=2, column=0, sticky=tk.W)
collection_var = tk.StringVar(value=os.getenv("COLLECTION"))
tk.Entry(root, textvariable=collection_var).grid(row=2, column=1)

tk.Label(root, text="Main Directory:").grid(row=3, column=0, sticky=tk.W)
main_dir_var = tk.StringVar(value=os.getenv("MAIN_DIR"))
tk.Entry(root, textvariable=main_dir_var).grid(row=3, column=1)

tk.Label(root, text="Number of Photos:").grid(row=4, column=0, sticky=tk.W)
num_photos_var = tk.StringVar(value=os.getenv("NUMBER_OF_PHOTOS"))
tk.Entry(root, textvariable=num_photos_var).grid(row=4, column=1)

# Create a Run button
run_button = tk.Button(root, text="Run", command=run_script)
run_button.grid(row=5, column=0, columnspan=2)

# Create a scrolled text widget for displaying logs
log_text = scrolledtext.ScrolledText(root, state=tk.DISABLED, width=80, height=20)
log_text.grid(row=6, column=0, columnspan=2)

# Run the application
root.mainloop()
