import csv
import re

# Tone mark mappings
tone_marks = {
    'a': 'āáǎàa',
    'e': 'ēéěèe',
    'i': 'īíǐìi',
    'o': 'ōóǒòo',
    'u': 'ūúǔùu',
    'ü': 'ǖǘǚǜü'
}

# Pinyin (with tone marks) to Chinese characters
pinyin_to_chinese = {
    'ài': '爱',
    'bèi sī': '贝斯',
    'bīng jī lín': '冰淇淋',
    'bú cuò': '不错',
    'bú kèqì': '不客气'
}

def apply_tone(syllable):
    match = re.match(r"([a-zü]+)([1-5])?$", syllable)
    if not match:
        return syllable

    body, tone = match.groups()
    tone = int(tone) if tone else 5
    if tone == 5 or tone < 1 or tone > 5:
        return body

    for vowel_group in ['a', 'e', 'o', 'iu', 'ui', 'i', 'u', 'ü']:
        for vowel in vowel_group:
            if vowel in body:
                return re.sub(vowel, tone_marks[vowel][tone - 1], body, count=1)
    return body

def convert_phrase(phrase):
    syllables = phrase.strip().split()
    return ' '.join(apply_tone(syllable) for syllable in syllables)

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
            chinese = pinyin_to_chinese.get(pinyin, '')  # Leave blank if not found
            writer.writerow([pinyin, chinese, english])

# Run the conversion
convert_csv()
