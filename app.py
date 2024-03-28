import tkinter as tk
import sounddevice as sd
from scipy.io.wavfile import write
from openai import OpenAI
from dotenv import load_dotenv
from tqdm import tqdm
import os

'''
Create a file ".env" in the same directory as this script and add the following line:
OPENAI_API_KEY=your_openai_api_key_here
Make sure to include .env in your .gitignore file to avoid exposing your API key.
'''
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def record_audio(duration, filename="recording.wav", fs=16000):
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=2, device=2) # Adjust device number based on your microphone, use sd.query_devices() to list available devices
    for _ in tqdm(range(duration), desc="Recording..."):
        sd.sleep(1000)  # Sleep for a second at a time to simulate wait with progress
    write(filename, fs, recording)
    print("Recording complete.")

def transcribe_audio(filename="recording.wav"):
    response = client.audio.transcriptions.create(
        model="whisper-1", 
        file=open(filename, "rb")
    )
    f = open("transcription.txt", "a")
    f.write(response.text)
    f.close()
    return response.text

def compare_texts(original_text, transcribed_text):
    prompt = f"Compare the following texts and provide feedback on differences:\nOriginal: {original_text}\nTranscribed: {transcribed_text}"

    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "system", "content": "You are a highly intelligent assistant. You give feedback on speeches, the original is what the person wanted to write. The transcribed is what they actually said. Give constructive feedback on the differences. Focus more on semantics, since the speech is getting transcribed it might be a bit wrong. Whats really important is that all the bullet points are covered. Keep feedback relatively brief with 1-2 sentences per bullet point."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1500
    )
    print("Received Feedback")
    return response.choices[0].message.content

def start_recording(duration=60):
    record_audio(duration)
    transcribed_text = transcribe_audio()
    feedback = compare_texts(text_entry.get("1.0", "end-1c"), transcribed_text)
    feedback_text.config(state=tk.NORMAL)
    feedback_text.delete('1.0', tk.END)
    feedback_text.insert('1.0', f"Feedback: {feedback}")
    feedback_text.config(state=tk.DISABLED)

duration = 180 # Duration of recording in seconds

window = tk.Tk()
window.title("Speech Memorization Helper")

window.geometry("800x600")

text_label = tk.Label(window, text="Paste your speech text here:")
text_label.pack()

text_frame = tk.Frame(window)
text_scroll = tk.Scrollbar(text_frame)
text_entry = tk.Text(text_frame, height=20, width=100, yscrollcommand=text_scroll.set)
text_scroll.config(command=text_entry.yview)
text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
text_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
text_frame.pack(expand=True, fill=tk.BOTH)

record_button = tk.Button(window, text="Record Speech", command=lambda: start_recording(duration=duration))
record_button.pack()

feedback_frame = tk.Frame(window)
feedback_scroll = tk.Scrollbar(feedback_frame)
feedback_text = tk.Text(feedback_frame, height=20, width=100, wrap=tk.WORD, yscrollcommand=feedback_scroll.set)
feedback_scroll.config(command=feedback_text.yview)
feedback_scroll.pack(side=tk.RIGHT, fill=tk.Y)
feedback_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
feedback_frame.pack(expand=True, fill=tk.BOTH)

window.mainloop()
