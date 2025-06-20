import csv
from googletrans import Translator

translator = Translator()

def translate_to_chinese(english):
    try:
        result = translator.translate(english, src='en', dest='zh-CN')
        return result.text
    except Exception as e:
        print(f"Translation error: {e}")
        return ''

def convert_csv(input_file='export.csv', output_file='vocab.csv'):
    with open(input_file, newline='', encoding='utf-8') as infile, \
         open(output_file, 'w', newline='', encoding='utf-8') as outfile:

        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        next(reader)  # Skip header
        writer.writerow(['Pinyin', 'Chinese', 'English'])

        for row in reader:
            shorthand_pinyin, english = row
            pinyin = convert_phrase(shorthand_pinyin)
            chinese = translate_to_chinese(english)
            writer.writerow([pinyin, chinese, english])

# Keep your apply_tone() and convert_phrase() from earlier
# Include here for completeness:

import re

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

# Run the final conversion
convert_csv()
