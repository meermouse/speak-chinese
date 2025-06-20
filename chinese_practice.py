import pandas as pd
from gtts import gTTS
import pygame
import time
import os
import keyboard

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

# Load vocab
df = pd.read_csv("vocab.csv")

index = 0
while index < len(df):
    row = df.iloc[index]
    pinyin = str(row['Chinese Pinyin'])
    english = str(row['English'])

    print(f"\n{pinyin} - {english}")

    speak(pinyin, "zh-cn", "pinyin.mp3")
    time.sleep(0.5)
    speak(english, "en", "english.mp3")

    print("Press [Enter] to continue, [Space] to repeat.")

    # Wait for either Enter or Space
    while True:
        if keyboard.is_pressed("enter"):
            index += 1
            break
        elif keyboard.is_pressed("space"):
            break
        time.sleep(0.1)
