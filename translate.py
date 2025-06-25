import csv
import re
import os
import openai
from math import ceil

# Load OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY") or "")

# Tone mark mapping
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

def convert_phrase(phrase):
    syllables = phrase.strip().split()
    return ' '.join(apply_tone(s) for s in syllables)

def batch_translate_to_chinese(english_phrases, pinyin_phrases):
    prompt = (
        "Translate the following English phrases into Simplified Chinese. "
        "Each item includes the English meaning and the expected Pinyin pronunciation. "
        "Return only the matching Chinese characters (no English or Pinyin), one per line, numbered.\n\n"
    )

    combined = "\n".join(
        f"{i+1}. English: {eng} | Pinyin: {pin}" for i, (eng, pin) in enumerate(zip(english_phrases, pinyin_phrases))
    )
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a precise Chinese translator who uses both English and Pinyin to find the correct characters."},
                {"role": "user", "content": prompt + combined}
            ],
            temperature=0.3
        )
        result = response.choices[0].message.content.strip()
        lines = result.splitlines()
        chinese_translations = []
        for line in lines:
            if ". " in line:
                chinese = line.split(". ", 1)[-1].strip()
                chinese_translations.append(chinese)
        return chinese_translations
    except Exception as e:
        print(f"\nError during translation batch: {e}")
        return [''] * len(english_phrases)

def convert_csv(input_file='export.csv', output_file='vocab.csv', batch_size=20):
    with open(input_file, newline='', encoding='utf-8') as infile:
        reader = list(csv.reader(infile))
        rows = reader[1:]  # skip header

    shorthand_pinyins = [row[0] for row in rows]
    english_phrases = [row[1] for row in rows]
    true_pinyins = [convert_phrase(p) for p in shorthand_pinyins]

    chinese_translations = []
    total_batches = ceil(len(english_phrases) / batch_size)

    for i in range(0, len(english_phrases), batch_size):
        batch = english_phrases[i:i + batch_size]
        translated = batch_translate_to_chinese(english_phrases[i:i + batch_size], true_pinyins[i:i + batch_size])
        chinese_translations.extend(translated)
        percent = int(((i + batch_size) / len(english_phrases)) * 100)
        print(f"\rProgress: {min(percent, 100)}%", end='', flush=True)

    with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['Pinyin', 'Chinese', 'English'])
        for pinyin, chinese, english in zip(true_pinyins, chinese_translations, english_phrases):
            writer.writerow([pinyin, chinese, english])

    print("\nDone!")

# Run the script
convert_csv()
