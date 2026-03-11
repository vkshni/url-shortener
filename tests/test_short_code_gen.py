import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from short_code_gen import (
    generate, 
    is_valid_code, 
    generate_batch,
    ALPHABET,
    CODE_LENGTH
)


def test_generate_returns_string():
    """Test that generate returns a string"""
    code = generate()
    assert isinstance(code, str)


def test_generate_correct_length():
    """Test that generated code is exactly 6 characters"""
    code = generate()
    assert len(code) == CODE_LENGTH


def test_generate_uses_valid_characters():
    """Test that all characters are from base62 alphabet"""
    code = generate()
    assert all(c in ALPHABET for c in code)


def test_generate_randomness():
    """Test that consecutive generations produce different codes"""
    codes = [generate() for _ in range(100)]
    unique_codes = set(codes)
    
    # With 62^6 possibilities, 100 codes should be unique
    assert len(unique_codes) == 100


def test_is_valid_code_accepts_valid():
    """Test validation accepts valid codes"""
    valid_codes = ['aB3x9Z', 'AAAAAA', 'zzzzzz', '123456', 'aBcDeF']
    
    for code in valid_codes:
        assert is_valid_code(code) is True


def test_is_valid_code_rejects_invalid_length():
    """Test validation rejects codes with wrong length"""
    invalid_codes = ['abc', 'abcdefg', '', 'a']
    
    for code in invalid_codes:
        assert is_valid_code(code) is False


def test_is_valid_code_rejects_invalid_characters():
    """Test validation rejects codes with non-base62 characters"""
    invalid_codes = ['abc@#$', 'test!!', 'url-me', 'abc def']
    
    for code in invalid_codes:
        assert is_valid_code(code) is False


def test_is_valid_code_rejects_none():
    """Test validation rejects None"""
    assert is_valid_code(None) is False


def test_generate_batch_returns_list():
    """Test batch generation returns a list"""
    batch = generate_batch(10)
    assert isinstance(batch, list)


def test_generate_batch_correct_count():
    """Test batch generation returns requested count"""
    batch = generate_batch(25)
    assert len(batch) == 25


def test_generate_batch_all_unique():
    """Test batch generation returns unique codes"""
    batch = generate_batch(50)
    assert len(batch) == len(set(batch))


def test_generate_batch_all_valid():
    """Test all codes in batch are valid"""
    batch = generate_batch(20)
    assert all(is_valid_code(code) for code in batch)


def test_alphabet_is_base62():
    """Test that alphabet contains exactly 62 characters"""
    assert len(ALPHABET) == 62
    assert len(set(ALPHABET)) == 62  # No duplicates


def test_alphabet_contains_expected_chars():
    """Test alphabet contains a-z, A-Z, 0-9"""
    import string
    expected = set(string.ascii_letters + string.digits)
    assert set(ALPHABET) == expected


def test_generate_statistical_distribution():
    """Test that generated codes have good statistical distribution"""
    # Generate many codes and check character frequency
    codes = [generate() for _ in range(1000)]
    all_chars = ''.join(codes)
    
    # Each character should appear roughly equally
    # With 6000 total chars and 62 possible chars, expect ~97 per char
    # Allow 50% variance
    from collections import Counter
    char_counts = Counter(all_chars)
    
    for char in ALPHABET:
        count = char_counts.get(char, 0)
        assert 48 < count < 146  # Roughly 97 ± 50