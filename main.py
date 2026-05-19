import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import pyttsx3
from gtts import gTTS
import pygame
import threading
import re
import os
from PyPDF2 import PdfReader

# ================== INITIAL SETUP ==================
engine = pyttsx3.init()
pygame.mixer.init()

# ================== MAIN WINDOW ==================
app = tk.Tk()
app.title("SmartSpeech Studio - AI Text To Speech")
app.geometry("750x750")
app.resizable(False, False)
app.configure(bg="#1e1e1e")

# ================== COLORS ==================
BG_COLOR = "#1e1e1e"
FG_COLOR = "white"
BTN_COLOR = "#4CAF50"
BTN_TEXT = "white"

# ================== LANGUAGE MAP ==================
language_map = {
    "English": "en",
    "Hindi": "hi",
    "French": "fr",
    "Spanish": "es",
    "German": "de",
    "Italian": "it"
}

# ================== VOICE ENGINE ==================
voices = engine.getProperty('voices')

def set_voice(gender):
    try:
        if gender == "Female":
            engine.setProperty('voice', voices[1].id)
        else:
            engine.setProperty('voice', voices[0].id)
    except:
        pass

# ================== CLEAN TEXT ==================
def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# ================== STATUS ==================
def update_status(message):
    status_label.config(text=message)
    app.update()

# ================== WORD COUNTER ==================
def count_words(event=None):
    text = text_entry.get("1.0", tk.END)
    words = len(text.split())
    word_label.config(text=f"Words: {words}")

# ================== OFFLINE SPEAK ==================
def speak_offline(text, rate, volume, gender):
    try:
        update_status("Speaking...")
        set_voice(gender)

        engine.setProperty('rate', rate)
        engine.setProperty('volume', volume)

        engine.say(text)
        engine.runAndWait()

        update_status("Speech Completed")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# ================== STOP SPEECH ==================
def stop_speech():
    try:
        engine.stop()
        pygame.mixer.music.stop()
        update_status("Speech Stopped")
    except:
        pass

# ================== SAVE AI SPEECH ==================
saved_audio_path = ""

def save_ai_speech(text, lang):
    global saved_audio_path

    save_path = filedialog.asksaveasfilename(
        defaultextension=".mp3",
        filetypes=[("MP3 Files", "*.mp3")]
    )

    if save_path:
        try:
            update_status("Generating AI Voice...")

            tts = gTTS(text=text, lang=lang)
            tts.save(save_path)

            saved_audio_path = save_path

            update_status("Audio Saved Successfully")
            messagebox.showinfo("Success", "Audio saved successfully!")

        except Exception as e:
            messagebox.showerror("Error", str(e))

# ================== PLAY AUDIO ==================
def play_audio():
    global saved_audio_path

    if saved_audio_path and os.path.exists(saved_audio_path):
        try:
            pygame.mixer.music.load(saved_audio_path)
            pygame.mixer.music.play()
            update_status("Playing Audio...")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    else:
        messagebox.showwarning("Warning", "No saved audio found!")

# ================== LOAD TXT FILE ==================
def load_text_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("Text Files", "*.txt")]
    )

    if file_path:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

                text_entry.delete("1.0", tk.END)
                text_entry.insert(tk.END, content)

                count_words()
                update_status("TXT File Loaded")

        except Exception as e:
            messagebox.showerror("Error", str(e))

# ================== LOAD PDF FILE ==================
def load_pdf_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("PDF Files", "*.pdf")]
    )

    if file_path:
        try:
            pdf = PdfReader(file_path)
            text = ""

            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"

            text_entry.delete("1.0", tk.END)
            text_entry.insert(tk.END, text)

            count_words()
            update_status("PDF Loaded Successfully")

        except Exception as e:
            messagebox.showerror("Error", str(e))

# ================== GENERATE SPEECH ==================
def generate_speech():
    text = text_entry.get("1.0", tk.END)
    text = clean_text(text)

    if not text:
        messagebox.showwarning("Warning", "Please enter some text!")
        return

    rate = rate_scale.get()
    volume = volume_scale.get() / 100
    method = method_var.get()
    lang = language_map[language_var.get()]
    gender = voice_var.get()

    if method == "Offline (Instant Speak)":
        threading.Thread(
            target=speak_offline,
            args=(text, rate, volume, gender)
        ).start()

    else:
        threading.Thread(
            target=save_ai_speech,
            args=(text, lang)
        ).start()

# ================== TITLE ==================
title_label = tk.Label(
    app,
    text="SmartSpeech Studio",
    font=("Arial", 22, "bold"),
    bg=BG_COLOR,
    fg="#4CAF50"
)
title_label.pack(pady=10)

subtitle = tk.Label(
    app,
    text="AI-Powered Text To Speech Converter",
    font=("Arial", 11),
    bg=BG_COLOR,
    fg="lightgray"
)
subtitle.pack()

# ================== TEXT AREA ==================
text_entry = tk.Text(
    app,
    height=12,
    width=75,
    font=("Arial", 11),
    bg="#2d2d2d",
    fg="white",
    insertbackground="white"
)
text_entry.pack(pady=15)

text_entry.bind("<KeyRelease>", count_words)

# ================== WORD LABEL ==================
word_label = tk.Label(
    app,
    text="Words: 0",
    bg=BG_COLOR,
    fg="lightblue",
    font=("Arial", 10)
)
word_label.pack()

# ================== LANGUAGE ==================
tk.Label(
    app,
    text="Select Language",
    bg=BG_COLOR,
    fg=FG_COLOR,
    font=("Arial", 10, "bold")
).pack(pady=5)

language_var = tk.StringVar(value="English")

language_menu = ttk.Combobox(
    app,
    textvariable=language_var,
    values=list(language_map.keys()),
    state="readonly",
    width=20
)
language_menu.pack()

# ================== VOICE SELECTION ==================
tk.Label(
    app,
    text="Select Voice",
    bg=BG_COLOR,
    fg=FG_COLOR,
    font=("Arial", 10, "bold")
).pack(pady=5)

voice_var = tk.StringVar(value="Male")

voice_menu = ttk.Combobox(
    app,
    textvariable=voice_var,
    values=["Male", "Female"],
    state="readonly",
    width=20
)
voice_menu.pack()

# ================== MODE ==================
tk.Label(
    app,
    text="Select Mode",
    bg=BG_COLOR,
    fg=FG_COLOR,
    font=("Arial", 10, "bold")
).pack(pady=5)

method_var = tk.StringVar(value="Offline (Instant Speak)")

mode_menu = ttk.Combobox(
    app,
    textvariable=method_var,
    values=[
        "Offline (Instant Speak)",
        "AI Mode (Save MP3)"
    ],
    state="readonly",
    width=30
)
mode_menu.pack()

# ================== SPEECH RATE ==================
tk.Label(
    app,
    text="Speech Rate",
    bg=BG_COLOR,
    fg=FG_COLOR,
    font=("Arial", 10, "bold")
).pack(pady=5)

rate_scale = tk.Scale(
    app,
    from_=100,
    to=250,
    orient="horizontal",
    length=300,
    bg=BG_COLOR,
    fg=FG_COLOR,
    highlightbackground=BG_COLOR
)
rate_scale.set(150)
rate_scale.pack()

# ================== VOLUME ==================
tk.Label(
    app,
    text="Volume",
    bg=BG_COLOR,
    fg=FG_COLOR,
    font=("Arial", 10, "bold")
).pack(pady=5)

volume_scale = tk.Scale(
    app,
    from_=0,
    to=100,
    orient="horizontal",
    length=300,
    bg=BG_COLOR,
    fg=FG_COLOR,
    highlightbackground=BG_COLOR
)
volume_scale.set(100)
volume_scale.pack()

# ================== BUTTON FRAME ==================
button_frame = tk.Frame(app, bg=BG_COLOR)
button_frame.pack(pady=15)

# Generate Button
generate_btn = tk.Button(
    button_frame,
    text="Generate Speech",
    command=generate_speech,
    bg=BTN_COLOR,
    fg=BTN_TEXT,
    width=18,
    height=2,
    font=("Arial", 10, "bold")
)
generate_btn.grid(row=0, column=0, padx=10, pady=10)

# Stop Button
stop_btn = tk.Button(
    button_frame,
    text="Stop Speech",
    command=stop_speech,
    bg="red",
    fg="white",
    width=18,
    height=2,
    font=("Arial", 10, "bold")
)
stop_btn.grid(row=0, column=1, padx=10)

# Play Audio Button
play_btn = tk.Button(
    button_frame,
    text="Play Saved Audio",
    command=play_audio,
    bg="#2196F3",
    fg="white",
    width=18,
    height=2,
    font=("Arial", 10, "bold")
)
play_btn.grid(row=1, column=0, padx=10, pady=10)

# Load TXT Button
txt_btn = tk.Button(
    button_frame,
    text="Load TXT File",
    command=load_text_file,
    bg="#9C27B0",
    fg="white",
    width=18,
    height=2,
    font=("Arial", 10, "bold")
)
txt_btn.grid(row=1, column=1, padx=10)

# Load PDF Button
pdf_btn = tk.Button(
    button_frame,
    text="Load PDF File",
    command=load_pdf_file,
    bg="#FF9800",
    fg="white",
    width=18,
    height=2,
    font=("Arial", 10, "bold")
)
pdf_btn.grid(row=2, column=0, columnspan=2, pady=10)

# ================== STATUS LABEL ==================
status_label = tk.Label(
    app,
    text="Ready",
    bg=BG_COLOR,
    fg="lightgreen",
    font=("Arial", 10, "italic")
)
status_label.pack(pady=10)

# ================== FOOTER ==================
footer = tk.Label(
    app,
    text="Offline Mode = Instant Voice | AI Mode = MP3 Export",
    bg=BG_COLOR,
    fg="gray",
    font=("Arial", 9)
)
footer.pack(side="bottom", pady=10)

# ================== RUN APP ==================
app.mainloop()