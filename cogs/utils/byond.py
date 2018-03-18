import re

def get_ckey(name):
    name = str(name).lower()

    return re.sub(r"\W+", "", name)
