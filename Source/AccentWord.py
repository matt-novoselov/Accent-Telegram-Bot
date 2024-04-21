import random
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Load dictionary with all words
Dict = open("Data/dictionary.txt", encoding="utf8").readlines()

# Define vowel letters
Vowels = ['а', 'о', 'и', 'ы', 'у', 'э', 'е', 'ё', 'ю', 'я']

# Define vowel letters with accents
AccentVowels = ['а́', 'о́', 'и́', 'ы́', 'у́', 'э́', 'е́', 'ё', 'ю́', 'я́']


# Add accent to the vowel
async def AddAccent(word, index):
    # Exception letter fix
    fix_accent = word[index].replace("ё", "е")
    return word[:index] + AccentVowels[Vowels.index(fix_accent)] + word[index + 1:]


# Generate all possible accents in the word
async def GenerateAccents():
    try:
        word = Dict[random.randint(0, len(Dict) - 1)].rstrip()
        correct_accent = [idx for idx in range(len(word)) if word[idx].isupper()][0]
        word = word.lower()
        correct_word = await AddAccent(word, correct_accent)
        variations = []
        for i in range(len(word)):
            if word[i] in Vowels:
                variations.append(await AddAccent(word, i))

        dictionary = {"CorrectWord": correct_word, "VariationsArray": variations}

        inline_kb_full = InlineKeyboardMarkup(row_width=2)
        i = len(dictionary['VariationsArray'])
        while i > 0:
            if i % 2 == 0:
                inline_kb_full.add(
                    InlineKeyboardButton(dictionary['VariationsArray'][i - 1],
                                         callback_data=f"{dictionary['VariationsArray'][i - 1]}#{dictionary['CorrectWord']}"),
                    InlineKeyboardButton(dictionary['VariationsArray'][i - 2],
                                         callback_data=f"{dictionary['VariationsArray'][i - 2]}#{dictionary['CorrectWord']}"),
                )
                i -= 2
            else:
                inline_kb_full.add(
                    InlineKeyboardButton(dictionary['VariationsArray'][i - 1],
                                         callback_data=f"{dictionary['VariationsArray'][i - 1]}#{dictionary['CorrectWord']}"),
                )
                i -= 1
        return inline_kb_full

    except Exception as e:
        print(f'[!] There was an error in generating accents: {e}')
        pass
