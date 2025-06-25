import pandas as pd
from gtts import gTTS
import pygame
import time
import os
import keyboard
import sys
import random

sys.stdout.reconfigure(encoding='utf-8')

def speak(text, lang, filename):
    tts = gTTS(text=text, lang=lang)
    tts.save(filename)

    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

    pygame.mixer.music.unload()
    os.remove(filename)

# Load and shuffle vocab
df = pd.read_csv("vocab.csv")  # Columns: Pinyin, Chinese, English
shuffled_indices = list(df.index)
random.shuffle(shuffled_indices)

index = 0
while index < len(shuffled_indices):
    row = df.loc[shuffled_indices[index]]
    pinyin = str(row['Pinyin'])
    chinese = str(row['Chinese'])
    english = str(row['English'])

    print(f"\n{pinyin} ({english} - {chinese})")

    # Speak English
    speak(english, "en", "english.mp3")

    time.sleep(0.25)

    # Speak Chinese characters (with tones)
    speak(chinese, "zh-cn", "chinese.mp3")

    print("Press [↓] to continue, [↑] to repeat this pair.")

    # Wait for arrow key input
    while True:
        if keyboard.is_pressed("down"):
            index += 1
            break
        elif keyboard.is_pressed("up"):
            break
        time.sleep(0.1)
