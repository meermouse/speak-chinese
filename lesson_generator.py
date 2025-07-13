import openai
import os
import re

# Load OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY") or "")

# For applying tone marks
tone_marks = {
    'a': 'āáǎàa',
    'e': 'ēéěèe',
    'i': 'īíǐìi',
    'o': 'ōóǒòo',
    'u': 'ūúǔùu',
    'ü': 'ǖǘǚǜü'
}

def apply_tone(syllable):
    match = re.match(r"([a-zü]+)([1-5])?$", syllable)
    if not match:
        return syllable
    body, tone = match.groups()
    tone = int(tone) if tone else 5
    if tone == 5:
        return body
    for vowel_group in ['a', 'e', 'o', 'iu', 'ui', 'i', 'u', 'ü']:
        for vowel in vowel_group:
            if vowel in body:
                return re.sub(vowel, tone_marks[vowel][tone - 1], body, count=1)
    return body

def convert_pinyin_line(pinyin_line):
    syllables = pinyin_line.strip().split()
    return ' '.join(apply_tone(s) for s in syllables)

def generate_lesson_rows(lesson_number):
    lesson_titles = {
        "1": "Phrases using what, when, where, why, how"
        # You can add more lessons later
    }

    title = lesson_titles.get(str(lesson_number), "Basic Chinese Phrases")

    print(f"\nLesson {lesson_number}: {title}")

    # Ask GPT to generate lesson content
    prompt = (
        f"Create a list of 6 very simple Mandarin Chinese phrases for a beginner. "
        f"The theme is: {title}. Output them in this format:\n"
        f"English: ...\nPinyin: ... (with tone numbers)\n"
        f"(Repeat for each phrase, no extra commentary)"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a Chinese tutor helping create language lessons."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )
        content = response.choices[0].message.content.strip()

        # Parse phrases
        english_phrases = []
        pinyin_raw = []

        lines = content.splitlines()
        for line in lines:
            if line.startswith("English:"):
                english_phrases.append(line.split("English:", 1)[-1].strip())
            elif line.startswith("Pinyin:"):
                pinyin_raw.append(line.split("Pinyin:", 1)[-1].strip())

        # Convert pinyin with tone marks
        pinyin_with_marks = [convert_pinyin_line(p) for p in pinyin_raw]

        # Batch translate to Chinese characters
        from your_module import batch_translate_to_chinese  # <- adjust this import if needed
        chinese_list = batch_translate_to_chinese(english_phrases, pinyin_with_marks)

        # Package into row-like dicts
        lesson_rows = [
            {"Pinyin": p, "Chinese": c, "English": e}
            for p, c, e in zip(pinyin_with_marks, chinese_list, english_phrases)
        ]

        return lesson_rows

    except Exception as e:
        print(f"\nError generating lesson: {e}")
        return []
