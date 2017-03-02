import re

def isChinese(word):
    for w in word:
        if re.match('[ \u4e00 -\u9fa5]+',w) == None:
            continue
        else:
            return False
    return True

def isEnglish(word):
    try:
        word.decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        print word
        return True

def isNumber(word):
    try:
        float(word)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(word)
        return True
    except (TypeError, ValueError):
        pass
    return False

def isWORD(word):
    if isChinese(word):
        return True
    if isEnglish(word):
        return True
    return False
