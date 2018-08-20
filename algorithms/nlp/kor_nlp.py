from konlpy.tag import Okt, Hannanum, Kkma, Mecab, Komoran
from nltk import pos_tag, FreqDist
from nltk.corpus import stopwords
from collections import Counter
twitter = Okt()
hannanum = Hannanum()
kkma = Kkma()
komoran = Komoran()

import operator

def korean_text_pre(sentence, func):
    tokens = hannanum.morphs(sentence)
    pos = hannanum.pos(sentence, ntags=22)
    noun = hannanum.nouns(sentence)
    stop_words = set(stopwords.words('english'))
    stop_words.add(',')
    stop_words.add('.')
    filtered_sentence = [w for w in tokens if not w in stop_words]
    filtered_sentence = [word for word in filtered_sentence if len(word) > 1]
    filtered_sentence = [word for word in filtered_sentence if not word.isnumeric()]
    if func == 'count':
        freq = Counter(filtered_sentence)
        word_freq = sorted(dict(freq).items(), key=operator.itemgetter(1), reverse=True)
        result = [{'name':name,'y':value} for name, value in word_freq]
    elif func == 'token':
        result = filtered_sentence
    elif func == 'pos':
        filtered_sentence = [w for w in pos if not w[0] in stop_words]
        filtered_sentence = [word for word in filtered_sentence if not word[1] == 'JC']
        filtered_sentence = [word for word in filtered_sentence if not word[1] == 'ET']
        result = filtered_sentence
    elif func == 'noun':
        result = noun
    elif func == 'noun_count':
        freq = Counter(noun)
        word_freq = sorted(dict(freq).items(), key=operator.itemgetter(1), reverse=True)
        result = [{'name':name,'y':value} for name, value in word_freq]
    return result
