import csv
import re

# Mapping from tone number to vowel diacritics
tone_marks = {
    'a': 'āáǎàa',
    'e': 'ēéěèe',
    'i': 'īíǐìi',
    'o': 'ōóǒòo',
    'u': 'ūúǔùu',
    'ü': 'ǖǘǚǜü'
}

# Helper to apply tone mark to a single syllable
def apply_tone(syllable):
    match = re.match(r"([a-zü]+)([1-5])?$", syllable)
    if not match:
        return syllable

    body, tone = match.groups()
    tone = int(tone) if tone else 5

    if tone == 5 or tone < 1 or tone > 5:
        return body

    # Vowel priority for tone mark placement
    for vowel_group in ['a', 'e', 'o', 'iu', 'ui', 'i', 'u', 'ü']:
        for vowel in vowel_group:
            if vowel in body:
                return re.sub(vowel, tone_marks[vowel][tone - 1], body, count=1)
    return body

# Convert a whole phrase (e.g. "bu2 ke4qi") to true pinyin
def convert_phrase(phrase):
    syllables = phrase.strip().split()
    return ' '.join(apply_tone(syllable) for syllable in syllables)

# Main function
def convert_csv(input_file='export.csv', output_file='vocab.csv'):
    with open(input_file, newline='', encoding='utf-8') as infile, \
         open(output_file, 'w', newline='', encoding='utf-8') as outfile:

        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        header = next(reader)
        writer.writerow(['Chinese Pinyin', 'English'])

        for row in reader:
            shorthand_pinyin, english = row
            converted = convert_phrase(shorthand_pinyin)
            writer.writerow([converted, english])

# Run conversion
convert_csv()
