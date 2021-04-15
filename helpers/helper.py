import random

def make_ordinal(n):
    n = int(n)
    suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    return str(n) + suffix

def homoglyph_convert(pokemon_name, msg):
    msg = msg.replace(pokemon_name, "<redacted>")
    m = list(msg)
    homoglyphs = {
        "a": "а",
        "c": "с",
        "e": "е",
        "o": "o",
        "p": "р",
        "x": "х",
        "y": "y",
    }
    for i, char in enumerate(m):
        if random.randint(1,5) > 3:
            m[i] = homoglyphs.get(m[i], m[i])

    return "".join(m)

def hintify(pokemon_name):
    inds = [i for i, x in enumerate(pokemon_name) if x.isalpha()]
    blanks = random.sample(inds, len(inds) // 2)
    hint = " ".join(
        "".join(x if i in blanks else "\\_" for i, x in enumerate(x))
        for x in pokemon_name.split()
    )
    return hint