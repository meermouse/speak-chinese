import pandas as pd
from gtts import gTTS
import pygame
import time
import os

def speak(text, lang, filename):
    tts = gTTS(text=text, lang=lang)
    tts.save(filename)

    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    # Wait until it finishes playing
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

    pygame.mixer.music.unload()
    os.remove(filename)

# Load vocab
df = pd.read_csv("vocab.csv")

for idx, row in df.iterrows():
    pinyin = str(row['Chinese Pinyin'])
    english = str(row['English'])

    print(f"\n{pinyin} - {english}")

    speak(pinyin, "zh-cn", "pinyin.mp3")
    time.sleep(1)
    speak(english, "en", "english.mp3")

    input("Press Enter to continue...")
