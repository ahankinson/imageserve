# module for matching names with folders
from unidecode import unidecode

KNOWN_EXCEPTIONS = {
    "Ross_[=Rossiano]_1033": "Ross_1033"
}

def name(name):
    # transliterate the name to plain ascii
    nm = unidecode(name)
    # do replacements
    nm = nm.replace('.','').replace(' ','_')

    # check if what we have is a known exception
    if KNOWN_EXCEPTIONS.get(nm, None):
        nm = KNOWN_EXCEPTIONS[nm]

    return nm

def valid_id(id):
    # checks for a valid id. Doesn't do anything right now.
    return True