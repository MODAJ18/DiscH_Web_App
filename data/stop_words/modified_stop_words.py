import re
import pandas as pd
arabic_diacritics = re.compile("""
                             ّ    | # Shadda
                             َ    | # Fatha
                             ً    | # Tanwin Fath
                             ُ    | # Damma
                             ٌ    | # Tanwin Damm
                             ِ    | # Kasra
                             ٍ    | # Tanwin Kasr
                             ْ    | # Sukun
                             ـ     # Tatwil/Kashida
                         """, re.VERBOSE)

with open('../Data/arabic-stop-words/list.txt','r', encoding="utf8") as f:
    stop_word_data= f.read()

stop_word_data = re.sub(arabic_diacritics, '', stop_word_data)
stop_word_data = re.sub("[إأآا]", "ا", stop_word_data)
stop_word_data = stop_word_data.split('\n')[:-1]  # last element is empty string, so we remove it 
pd.DataFrame(stop_word_data, columns=['words']).to_csv('../Data/stop_words/list.csv', index=False, encoding='utf-8-sig')