import sys
import os
import time
import random
import pandas as pd
import pygame
from gtts import gTTS

# === CONFIG ===
USE_OPENAI_WHISPER = True  # set True to use OpenAI Whisper API; False uses offline Vosk
RECORD_SECONDS = 4          # how long to record each attempt
SAMPLE_RATE = 16000         # 16kHz works well for ASR
SIMILARITY_PASS_THRESHOLD = 0.75  # 0..1, how strict the match is
N_ITEMS = 8                 # how many rows to drill per lesson

# Input CSV expected columns: Pinyin,Chinese,English
CSV_PATH = "vocab.csv"

# === AUDIO PLAYBACK ===
def speak(text, lang, filename):
    tts = gTTS(text=text, lang=lang)
    tts.save(filename)

    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
    pygame.mixer.music.unload()
    try:
        os.remove(filename)
    except Exception:
        pass

# === KEY INPUT (Up/Down) ===
# Note: on Windows the keyboard package may require running terminal as administrator
try:
    import keyboard
    HAVE_KEYBOARD = True
except Exception:
    HAVE_KEYBOARD = False

def wait_for_up_or_down():
    """Return 'repeat' for Up, 'next' for Down."""
    print("Press [↓] next, [↑] try again.")
    if not HAVE_KEYBOARD:
        input("(keyboard module not available) Press Enter to continue...")
        return "next"
    while True:
        if keyboard.is_pressed("down"):
            return "next"
        if keyboard.is_pressed("up"):
            return "repeat"
        time.sleep(0.05)

# === RECORDING ===
import sounddevice as sd
import soundfile as sf

def record_wav(path, seconds=RECORD_SECONDS, samplerate=SAMPLE_RATE):
    print(f"Recording for {seconds} seconds… Speak now.")
    audio = sd.rec(int(seconds * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    sf.write(path, audio, samplerate)
    return path

# === TRANSCRIPTION (Two options) ===

# Option A: OpenAI Whisper API (set USE_OPENAI_WHISPER=True)
def transcribe_openai(wav_path):
    import openai
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY") or "")
    with open(wav_path, "rb") as f:
        result = client.audio.transcriptions.create(
            model="whisper-1",     # or a newer STT model if you prefer
            file=f,
            language="zh"
        )
    # result.text should contain the recognized Chinese text
    return getattr(result, "text", "").strip()

# Option B: Offline via Vosk (set USE_OPENAI_WHISPER=False)
#   pip install vosk
#   Download a Mandarin model (e.g., small one) and set VOSK_MODEL_PATH env var to its folder.
def transcribe_vosk(wav_path):
    from vosk import Model, KaldiRecognizer
    import json
    model_path = os.getenv("VOSK_MODEL_PATH")
    if not model_path or not os.path.isdir(model_path):
        print("Vosk model not found. Set VOSK_MODEL_PATH to your Mandarin model folder.")
        return ""
    model = Model(model_path)
    rec = KaldiRecognizer(model, SAMPLE_RATE)
    rec.SetWords(True)

    # stream audio
    import wave
    wf = wave.open(wav_path, "rb")
    result_text = ""
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            result_text += " " + res.get("text", "")
    # final partial
    res = json.loads(rec.FinalResult())
    result_text += " " + res.get("text", "")
    # Vosk often outputs pinyin-ish/Latin; for Mandarin models it may output characters depending on model.
    return result_text.strip()

def transcribe(wav_path):
    if USE_OPENAI_WHISPER:
        return transcribe_openai(wav_path)
    return transcribe_vosk(wav_path)

# === SIMILARITY CHECK ===
# Convert both target and recognized text to pinyin and compare for robustness.
from difflib import SequenceMatcher
from pypinyin import lazy_pinyin, Style

def han_to_pinyin_syllables(text):
    # numbered tones for stability; fallback to normal pinyin if tones unavailable
    try:
        # Style.TONE3 = tone numbers (ni3 hao3)
        syls = lazy_pinyin(text, style=Style.TONE3, errors="ignore")
    except Exception:
        syls = lazy_pinyin(text, style=Style.NORMAL, errors="ignore")
    # normalize spacing/case
    return " ".join(s.lower().strip() for s in syls if s.strip())

def pinyin_text_to_base(text):
    # if recognizer returns Latin text (e.g., vosk), normalize spacing
    return " ".join(text.lower().split())

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def score_pronunciation(target_chinese, recognized_text):
    # Try to map both to pinyin space and compare
    target_py = han_to_pinyin_syllables(target_chinese)
    if any('\u4e00' <= ch <= '\u9fff' for ch in recognized_text):
        recog_py = han_to_pinyin_syllables(recognized_text)
    else:
        recog_py = pinyin_text_to_base(recognized_text)
    return similarity(target_py, recog_py), target_py, recog_py

# === ONE ROUND ===
def run_pronunciation_round(row):
    pinyin = str(row['Pinyin'])
    chinese = str(row['Chinese'])
    english = str(row['English'])

    print(f"\n{english} → {chinese} ({pinyin})")

    # Speak: English then Chinese
    speak(english, "en", "english_tmp.mp3")
    time.sleep(0.3)
    speak(chinese, "zh-cn", "chinese_tmp.mp3")

    # Record and transcribe
    wav_path = "attempt.wav"
    record_wav(wav_path, seconds=RECORD_SECONDS, samplerate=SAMPLE_RATE)
    recognized = transcribe(wav_path)
    try:
        os.remove(wav_path)
    except Exception:
        pass

    if not recognized:
        print("I couldn’t recognize anything. Let’s try again.")
        return "repeat"

    sc, tgt_py, rec_py = score_pronunciation(chinese, recognized)
    print(f"Recognized: {recognized}")
    print(f"Target PY:  {tgt_py}")
    print(f"Heard PY:   {rec_py}")
    print(f"Similarity: {sc:.2f}")

    if sc >= SIMILARITY_PASS_THRESHOLD:
        print("✅ Nice! That’s close enough.")
        return "next"
    else:
        print("↻ Not quite—try again (↑) or go next (↓).")
        return wait_for_up_or_down()

# === LESSON FLOW ===
def run_pronunciation_lesson(df, lesson_title, n_items=N_ITEMS):
    print(f"\n=== Lesson: {lesson_title} ===")
    # sample rows to practice; you can customize selection logic
    indices = list(df.index)
    random.shuffle(indices)
    indices = indices[:min(n_items, len(indices))]

    i = 0
    while i < len(indices):
        row = df.loc[indices[i]]
        outcome = run_pronunciation_round(row)
        if outcome == "next":
            i += 1
        else:
            # 'repeat' means stay on same i
            pass

# === MAIN ===
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pronunciation_lesson.py <lesson_number>")
        sys.exit(1)

    lesson_number = str(sys.argv[1])
    if not os.path.exists(CSV_PATH):
        print(f"Missing {CSV_PATH}. Expected columns: Pinyin,Chinese,English")
        sys.exit(1)

    # Load vocab
    df = pd.read_csv(CSV_PATH)

    # Choose a title based on lesson param
    lesson_titles = {
        "1": "Repeat-after-me: Phrases using what, when, where, why, how",
        "2": "Repeat-after-me: Greetings and introductions",
        "3": "Repeat-after-me: Numbers and time",
    }
    title = lesson_titles.get(lesson_number, f"Repeat-after-me: Custom Lesson {lesson_number}")

    run_pronunciation_lesson(df, title)
