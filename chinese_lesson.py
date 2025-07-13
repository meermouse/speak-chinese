import sys
import time
import pygame
import os
import keyboard
import pandas as pd

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

def run_lesson(row):
    pinyin = str(row['Pinyin'])
    chinese = str(row['Chinese'])
    english = str(row['English'])

    print(f"\n{english} → {chinese} ({pinyin})")

    speak(english, "en", "english.mp3")
    time.sleep(0.5)
    speak(chinese, "zh-cn", "chinese.mp3")

    print("Press [↓] to continue, [↑] to repeat.")

    while True:
        if keyboard.is_pressed("down"):
            return "next"
        elif keyboard.is_pressed("up"):
            return "repeat"
        time.sleep(0.1)

if __name__ == "__main__":
    from gtts import gTTS  # Import here to avoid issues during test/import
    if len(sys.argv) < 2:
        print("Usage: python chinese_lesson.py <lesson_number>")
        sys.exit(1)

    lesson_number = sys.argv[1]

    # Placeholder: Load lesson data here
    # For now, just print the lesson number
    print(f"Starting Chinese lesson {lesson_number}")

    # Example placeholder list of rows
    sample_data = [
        {"Pinyin": "nǐ hǎo", "Chinese": "你好", "English": "hello"},
        {"Pinyin": "zàijiàn", "Chinese": "再见", "English": "goodbye"}
    ]

    df = pd.DataFrame(sample_data)

    index = 0
    while index < len(df):
        result = run_lesson(df.loc[index])
        if result == "next":
            index += 1
        # if "repeat", stay on same index
