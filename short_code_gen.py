"""
Short Code Generator

Generates random Base62 short codes for URL shortening with validation utilities.
Uses characters a-z, A-Z, 0-9 for URL-safe, case-sensitive codes.
"""

import string
import random

# Base62 alphabet: a-z, A-Z, 0-9 (62 characters total)
ALPHABET = string.ascii_letters + string.digits

# Standard short code length (62^6 = 56.8 billion possible codes)
CODE_LENGTH = 6


def generate(code_length: int = CODE_LENGTH) -> str:
    """
    Generate a random short code using Base62 encoding.
    
    Args:
        code_length: Length of code to generate (default: 6)
        
    Returns:
        str: Random alphanumeric code
        
    Example:
        >>> code = generate()
        >>> len(code)
        6
        >>> all(c in ALPHABET for c in code)
        True
    """
    short_code = "".join(random.choices(ALPHABET, k=code_length))
    return short_code


def is_valid_code(code: str) -> bool:
    """
    Validate if a string is a valid short code.
    
    Checks that code is exactly 6 characters and contains only
    Base62 alphabet characters.
    
    Args:
        code: String to validate
        
    Returns:
        bool: True if valid, False otherwise
        
    Example:
        >>> is_valid_code('aB3x9Z')
        True
        >>> is_valid_code('abc')  # Too short
        False
        >>> is_valid_code('abc@#$')  # Invalid characters
        False
    """
    # Check length
    if not code or len(code) != CODE_LENGTH:
        return False
    
    # Check all characters are in Base62 alphabet
    return all(c in ALPHABET for c in code)


def generate_batch(count: int = 10) -> list[str]:
    """
    Generate multiple unique short codes at once.
    
    Useful for testing or pre-generating codes. Guarantees uniqueness
    within the batch only (not against database).
    
    Args:
        count: Number of unique codes to generate
        
    Returns:
        list[str]: List of unique short codes
        
    Example:
        >>> codes = generate_batch(5)
        >>> len(codes)
        5
        >>> len(set(codes))  # All unique
        5
    """
    codes = set()
    
    # Keep generating until we have enough unique codes
    while len(codes) < count:
        codes.add(generate())
    
    return list(codes)