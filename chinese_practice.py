import pandas as pd
from gtts import gTTS
import pygame
import time
import os
import keyboard
import random

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
df = pd.read_csv("vocab.csv")  # Make sure it has: Pinyin,Chinese,English
shuffled_indices = list(df.index)
random.shuffle(shuffled_indices)

index = 0
while index < len(shuffled_indices):
    row = df.loc[shuffled_indices[index]]
    pinyin = str(row['Pinyin'])
    chinese = str(row['Chinese'])
    english = str(row['English'])

    print(f"\n{pinyin} ({chinese}) - {english}")

    # Speak the Chinese characters (more accurate tones)
    speak(chinese, "zh-cn", "chinese.mp3")
    time.sleep(0.5)

    # Speak the English translation
    speak(english, "en", "english.mp3")

    print("Press [Enter] to continue, [Space] to repeat.")

    while True:
        if keyboard.is_pressed("enter"):
            index += 1
            break
        elif keyboard.is_pressed("space"):
            break
        time.sleep(0.1)
