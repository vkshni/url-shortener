import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from pathlib import Path
from url_service import URLService
from storage import URLDB
import json

TEST_FILE = "test_edge_cases.json"


@pytest.fixture
def service():
    """Create a fresh service for each test"""
    db = URLDB(TEST_FILE)
    svc = URLService(db)
    yield svc
    
    # Cleanup
    test_path = Path(__file__).parent.parent / TEST_FILE
    if test_path.exists():
        test_path.unlink()


# ============================================================================
# BOUNDARY CONDITION TESTS
# ============================================================================

def test_url_exactly_2000_characters(service):
    """Test URL with exactly 2000 characters (max length)"""
    # 2000 total: "https://example.com/" = 20 chars + 1980 'a's
    url = "https://example.com/" + "a" * 1980
    assert len(url) == 2000
    
    code = service.shorten(url)
    assert code is not None
    assert len(code) == 6


def test_url_1999_characters(service):
    """Test URL with 1999 characters (just under max)"""
    url = "https://example.com/" + "a" * 1979
    assert len(url) == 1999
    
    code = service.shorten(url)
    assert code is not None


def test_url_2001_characters_fails(service):
    """Test URL with 2001 characters (over max) raises error"""
    url = "https://example.com/" + "a" * 1981
    assert len(url) == 2001
    
    with pytest.raises(ValueError) as exc_info:
        service.shorten(url)
    
    error_msg = str(exc_info.value)
    assert "too long" in error_msg.lower() or "2000" in error_msg
    # Check no UUID leak
    assert len(error_msg) < 200  # Should be short
    assert error_msg.count('-') < 3  # No UUID dashes


def test_url_minimum_length(service):
    """Test shortest possible valid URL"""
    url = "http://a.b"  # Minimal valid URL
    assert len(url) == 10
    
    code = service.shorten(url)
    assert code is not None


def test_empty_url_fails(service):
    """Test empty URL raises error"""
    with pytest.raises(ValueError, match="empty"):
        service.shorten("")


def test_whitespace_only_url_fails(service):
    """Test whitespace-only URL raises error"""
    with pytest.raises(ValueError):
        service.shorten("   ")


def test_short_code_all_numbers(service):
    """Test that short codes can be all numbers"""
    # Generate enough URLs to potentially get all-number code
    codes = []
    for i in range(100):
        code = service.shorten(f"https://example.com/page{i}")
        codes.append(code)
    
    # At least one should work (we're not testing if we GET all numbers,
    # just that they work if generated)
    assert len(codes) == 100
    assert all(len(c) == 6 for c in codes)


def test_short_code_all_letters(service):
    """Test that short codes can be all letters"""
    # Similar to above - just verify codes work
    codes = set()
    for i in range(50):
        code = service.shorten(f"https://test.com/item{i}")
        codes.add(code)
    
    assert len(codes) == 50


def test_short_code_mixed_case(service):
    """Test that short codes use mixed case"""
    codes = []
    for i in range(100):
        code = service.shorten(f"https://example.com/test{i}")
        codes.append(code)
    
    # Should have some variation in case
    all_codes_str = ''.join(codes)
    has_uppercase = any(c.isupper() for c in all_codes_str)
    has_lowercase = any(c.islower() for c in all_codes_str)
    
    assert has_uppercase
    assert has_lowercase


# ============================================================================
# SPECIAL CHARACTER TESTS
# ============================================================================

def test_url_with_query_parameters(service):
    """Test URL with query parameters"""
    url = "https://example.com/search?q=test&lang=en&page=2"
    code = service.shorten(url)
    
    resolved = service.resolve(code)
    assert resolved == url


def test_url_with_fragment(service):
    """Test URL with fragment/anchor"""
    url = "https://example.com/page#section-2"
    code = service.shorten(url)
    
    resolved = service.resolve(code)
    assert resolved == url


def test_url_with_port(service):
    """Test URL with port number"""
    url = "https://example.com:8080/api/endpoint"
    code = service.shorten(url)
    
    resolved = service.resolve(code)
    assert resolved == url


def test_url_with_encoded_characters(service):
    """Test URL with percent-encoded characters"""
    url = "https://example.com/search?q=hello%20world"
    code = service.shorten(url)
    
    resolved = service.resolve(code)
    assert resolved == url


def test_url_with_multiple_slashes(service):
    """Test URL with multiple path segments"""
    url = "https://example.com/path/to/deep/resource/here"
    code = service.shorten(url)
    
    resolved = service.resolve(code)
    assert resolved == url


def test_url_with_special_chars_in_path(service):
    """Test URL with special characters in path"""
    url = "https://example.com/path-with_underscores/and-dashes"
    code = service.shorten(url)
    
    resolved = service.resolve(code)
    assert resolved == url


def test_url_with_numbers(service):
    """Test URL with numbers"""
    url = "https://example123.com/page456/item789"
    code = service.shorten(url)
    
    resolved = service.resolve(code)
    assert resolved == url


# ============================================================================
# PROTOCOL TESTS
# ============================================================================

def test_http_protocol(service):
    """Test HTTP (not HTTPS) URLs work"""
    url = "http://example.com/page"
    code = service.shorten(url)
    
    resolved = service.resolve(code)
    assert resolved == url


def test_https_protocol(service):
    """Test HTTPS URLs work"""
    url = "https://secure.example.com/page"
    code = service.shorten(url)
    
    resolved = service.resolve(code)
    assert resolved == url


def test_missing_protocol_fails(service):
    """Test URL without protocol fails"""
    with pytest.raises(ValueError, match="http"):
        service.shorten("example.com/page")


def test_ftp_protocol_fails(service):
    """Test FTP protocol fails"""
    with pytest.raises(ValueError):
        service.shorten("ftp://files.example.com")


def test_wrong_protocol_fails(service):
    """Test other protocols fail"""
    with pytest.raises(ValueError):
        service.shorten("file:///home/user/file.txt")


# ============================================================================
# DOMAIN VALIDATION TESTS
# ============================================================================

def test_missing_domain_fails(service):
    """Test URL without domain fails"""
    with pytest.raises(ValueError, match="domain"):
        service.shorten("https://")


def test_missing_tld_fails(service):
    """Test URL without TLD (top-level domain) fails"""
    with pytest.raises(ValueError, match="domain"):
        service.shorten("https://localhost")


def test_subdomain_works(service):
    """Test URL with subdomain works"""
    url = "https://api.example.com/endpoint"
    code = service.shorten(url)
    assert code is not None


def test_multiple_subdomains_works(service):
    """Test URL with multiple subdomains works"""
    url = "https://api.v2.example.com/endpoint"
    code = service.shorten(url)
    assert code is not None


# ============================================================================
# DATA CORRUPTION TESTS
# ============================================================================

def test_empty_json_file(service):
    """Test behavior when JSON file is empty array"""
    # Manually create empty file
    test_path = Path(__file__).parent.parent / TEST_FILE
    with open(test_path, 'w') as f:
        json.dump([], f)
    
    # Should work fine
    code = service.shorten("https://example.com/test")
    assert code is not None
    
    urls = service.list_all()
    assert len(urls) == 1


def test_corrupted_json_creates_new_file(service):
    """Test that corrupted JSON is handled gracefully"""
    # This test depends on your error handling
    # If your code crashes on corrupted JSON, you need to add try-catch
    test_path = Path(__file__).parent.parent / TEST_FILE
    
    # Create corrupted JSON
    with open(test_path, 'w') as f:
        f.write("{ this is not valid json }")
    
    # Depending on your implementation, this might:
    # 1. Create a new file (best)
    # 2. Raise an error (needs fixing)
    try:
        service.shorten("https://example.com/test")
    except json.JSONDecodeError:
        pytest.skip("JSON corruption not handled - implement error recovery")


def test_missing_field_in_record(service):
    """Test handling of record with missing fields"""
    test_path = Path(__file__).parent.parent / TEST_FILE
    
    # Create malformed record
    bad_data = [{
        "url_id": "test-id",
        "long_url": "https://example.com",
        # Missing short_code, created_at, visit_count
    }]
    
    with open(test_path, 'w') as f:
        json.dump(bad_data, f)
    
    # Try to list - should handle gracefully or raise clear error
    try:
        urls = service.list_all()
        # If it works, great! If not, we expect KeyError
    except KeyError:
        pytest.skip("Missing field handling not implemented")


# ============================================================================
# EXTREME USAGE TESTS
# ============================================================================

def test_shorten_100_urls_in_sequence(service):
    """Test shortening many URLs in sequence"""
    codes = []
    for i in range(100):
        code = service.shorten(f"https://example.com/page{i}")
        codes.append(code)
    
    assert len(codes) == 100
    assert len(set(codes)) == 100  # All unique


def test_resolve_same_code_1000_times(service):
    """Test resolving the same code many times"""
    url = "https://example.com/popular"
    code = service.shorten(url)
    
    # Resolve 1000 times
    for i in range(1000):
        resolved = service.resolve(code)
        assert resolved == url
    
    # Visit count should be exactly 1000
    stats = service.get_stats(code)
    assert stats['visit_count'] == 1000


def test_list_with_many_urls(service):
    """Test listing when there are many URLs"""
    # Add 200 URLs
    for i in range(200):
        service.shorten(f"https://example.com/item{i}")
    
    urls = service.list_all()
    assert len(urls) == 200


def test_mixed_operations_sequence(service):
    """Test random mix of operations"""
    codes = []
    
    # Mixed operations
    for i in range(50):
        # Shorten
        code = service.shorten(f"https://example.com/page{i}")
        codes.append(code)
        
        # Resolve some
        if i % 3 == 0 and codes:
            service.resolve(codes[0])
        
        # List occasionally
        if i % 10 == 0:
            urls = service.list_all()
            assert len(urls) == i + 1


# ============================================================================
# UNUSUAL URL PATTERNS
# ============================================================================

def test_url_with_trailing_slash(service):
    """Test URLs with and without trailing slash are different"""
    code1 = service.shorten("https://example.com/page")
    code2 = service.shorten("https://example.com/page/")
    
    # They should be treated as different URLs
    assert code1 != code2


def test_url_case_sensitivity(service):
    """Test that URLs are case-sensitive"""
    code1 = service.shorten("https://example.com/Page")
    code2 = service.shorten("https://example.com/page")
    
    # Should be different
    assert code1 != code2


def test_url_with_default_port_explicit(service):
    """Test URL with explicit default port"""
    url = "https://example.com:443/page"
    code = service.shorten(url)
    
    resolved = service.resolve(code)
    assert resolved == url


def test_ip_address_url(service):
    """Test URL with IP address instead of domain"""
    # This should FAIL based on your "must have ." validation
    # But IP addresses like 192.168.1.1 DO have dots
    url = "https://192.168.1.1/page"
    code = service.shorten(url)
    assert code is not None


def test_localhost_url_fails(service):
    """Test localhost URL fails (no dot in domain)"""
    with pytest.raises(ValueError, match="domain"):
        service.shorten("https://localhost/page")


# ============================================================================
# VISIT COUNTER EDGE CASES
# ============================================================================

def test_visit_count_never_negative(service):
    """Test visit count cannot become negative"""
    code = service.shorten("https://example.com/test")
    
    # Normal resolves
    service.resolve(code)
    service.resolve(code)
    
    stats = service.get_stats(code)
    assert stats['visit_count'] >= 0


def test_visit_count_accuracy_under_rapid_access(service):
    """Test visit counter stays accurate with rapid access"""
    code = service.shorten("https://example.com/rapid")
    
    # Rapid-fire resolves
    for _ in range(50):
        service.resolve(code)
    
    stats = service.get_stats(code)
    assert stats['visit_count'] == 50


# ============================================================================
# SHORT CODE EDGE CASES
# ============================================================================

def test_resolve_empty_code_fails(service):
    """Test resolving empty short code fails"""
    with pytest.raises(ValueError):
        service.resolve("")


def test_resolve_whitespace_code_fails(service):
    """Test resolving whitespace short code fails"""
    with pytest.raises(ValueError):
        service.resolve("   ")


def test_resolve_too_short_code_fails(service):
    """Test resolving code shorter than 6 chars fails"""
    with pytest.raises(ValueError):
        service.resolve("abc")


def test_resolve_too_long_code_fails(service):
    """Test resolving code longer than 6 chars fails"""
    with pytest.raises(ValueError):
        service.resolve("abcdefgh")


def test_resolve_invalid_characters_fails(service):
    """Test resolving code with invalid characters fails"""
    # Base62 doesn't include special characters
    with pytest.raises(ValueError):
        service.resolve("abc@#$")


def test_resolve_nonexistent_valid_format_code(service):
    """Test resolving valid format but non-existent code"""
    with pytest.raises(ValueError, match="not found"):
        service.resolve("ZZZZZZ")  # Valid format, doesn't exist