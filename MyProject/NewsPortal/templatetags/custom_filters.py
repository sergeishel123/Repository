from django import template

register = template.Library()


OBSCENE_WORDS = ['редиск','училк','сволоч','твар','гадин','мраз']

@register.filter()
def censor(value):
    value_list = value.split(' ')
    if not isinstance(value,str):
        raise ValueError('Данный фильтр применим к строке')
    else:
        for word in value_list:
            if word[:-1] in OBSCENE_WORDS:
                value_list[value_list.index(word)] = word[0] + '*' * (len(word) -1)
    return ' '.join(value_list)
