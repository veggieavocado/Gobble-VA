from celery import shared_task

from algorithms.nlp.eng_nlp import (
    text_freq,
    sentence_tokenize,
    word_pos_tag,
)

@shared_task
def hello():
    print('hello there!')
    return True

@shared_task
def text_freq_task(data):
    result = text_freq(data)
    return result

@shared_task
def sentence_tokenize_task(data):
    result = sentence_tokenize(data)
    return result

@shared_task
def word_pos_tag_task(data):
    result = word_pos_tag(data)
    return result
