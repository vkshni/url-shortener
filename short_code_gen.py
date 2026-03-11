# Short Code Generator

import string
import random

ALPHABET = string.ascii_letters + string.digits
CODE_LENGTH = 6

def generate(code_length:int = CODE_LENGTH) -> str:
    short_code = "".join(random.choices(ALPHABET,k=code_length))
    return short_code

def is_valid_code(code:str) -> bool:

    if not code or len(code) != 6:
        return False
    
    return all(c in ALPHABET for c in code)

def generate_batch(count: int=10) -> list[str]:

    codes = set()
    while len(codes) < count:
        codes.add(generate())
    return list(codes)
