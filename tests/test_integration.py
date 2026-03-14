import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from pathlib import Path
from url_service import URLService
from storage import URLDB

TEST_FILE = "test_integration_direct.json"


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
# HAPPY PATH WORKFLOW TESTS
# ============================================================================

def test_complete_workflow_happy_path(service):
    """Test complete workflow: shorten -> list -> resolve -> list again"""
    
    # Step 1: Shorten a URL
    short_code = service.shorten("https://example.com/test")
    assert short_code is not None
    assert len(short_code) == 6
    
    # Step 2: List URLs (should show 1)
    urls = service.list_all()
    assert len(urls) == 1
    assert urls[0].long_url == "https://example.com/test"
    assert urls[0].short_code == short_code
    assert urls[0].visit_count == 0
    
    # Step 3: Resolve the short code
    resolved_url = service.resolve(short_code)
    assert resolved_url == "https://example.com/test"
    
    # Step 4: List again (visit count should be 1)
    urls = service.list_all()
    assert len(urls) == 1
    assert urls[0].visit_count == 1


def test_shorten_duplicate_url_returns_same_code(service):
    """Test that shortening the same URL twice returns the same code"""
    
    code1 = service.shorten("https://github.com/test/repo")
    code2 = service.shorten("https://github.com/test/repo")
    
    assert code1 == code2
    
    # Should only have 1 URL in database
    urls = service.list_all()
    assert len(urls) == 1


def test_multiple_urls_workflow(service):
    """Test shortening and managing multiple URLs"""
    
    urls_to_shorten = [
        'https://example.com/page1',
        'https://example.com/page2',
        'https://github.com/user/repo',
        'https://google.com',
        'https://stackoverflow.com/questions/12345'
    ]
    
    short_codes = []
    
    # Shorten all URLs
    for url in urls_to_shorten:
        code = service.shorten(url)
        short_codes.append(code)
    
    # All codes should be unique
    assert len(short_codes) == len(set(short_codes))
    
    # List should show all 5
    all_urls = service.list_all()
    assert len(all_urls) == 5
    
    # Verify each URL is present
    long_urls = [u.long_url for u in all_urls]
    for url in urls_to_shorten:
        assert url in long_urls
    
    # Resolve each one
    for i, code in enumerate(short_codes):
        resolved = service.resolve(code)
        assert resolved == urls_to_shorten[i]


def test_visit_counter_increments_correctly(service):
    """Test that visit counter increments with each resolve"""
    
    short_code = service.shorten("https://example.com/popular")
    
    # Resolve 5 times
    for _ in range(5):
        service.resolve(short_code)
    
    # Check visit count is 5
    stats = service.get_stats(short_code)
    assert stats['visit_count'] == 5


def test_data_persists_across_service_instances(service):
    """Test that data persists across service restarts"""
    
    # First service: shorten and resolve
    short_code = service.shorten("https://example.com/persist")
    service.resolve(short_code)
    
    # Create new service instance (simulates restart)
    service2 = URLService(URLDB(TEST_FILE))
    
    # Should still have the URL
    all_urls = service2.list_all()
    assert len(all_urls) == 1
    assert all_urls[0].short_code == short_code
    assert all_urls[0].visit_count == 1
    
    # Resolve again with new instance
    resolved = service2.resolve(short_code)
    assert resolved == "https://example.com/persist"
    
    # Visit count should be 2
    stats = service2.get_stats(short_code)
    assert stats['visit_count'] == 2


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

def test_shorten_invalid_url_missing_protocol(service):
    """Test shortening URL without http/https raises error"""
    
    with pytest.raises(ValueError):
        service.shorten("example.com")


def test_shorten_empty_url(service):
    """Test shortening empty URL raises error"""
    
    with pytest.raises(ValueError):
        service.shorten("")


def test_resolve_nonexistent_code(service):
    """Test resolving a code that doesn't exist raises error"""
    
    with pytest.raises(ValueError, match="not found"):
        service.resolve("zzzzzz")


def test_get_stats_nonexistent_code(service):
    """Test getting stats for nonexistent code raises error"""
    
    with pytest.raises(ValueError, match="not found"):
        service.get_stats("notreal")


def test_list_when_empty(service):
    """Test list returns empty list when no URLs exist"""
    
    urls = service.list_all()
    assert urls == []
    assert len(urls) == 0


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

def test_shorten_url_with_special_characters(service):
    """Test URL with query parameters and special characters"""
    
    url = 'https://example.com/search?q=test&lang=en&sort=desc'
    short_code = service.shorten(url)
    
    # Resolve and verify
    resolved = service.resolve(short_code)
    assert resolved == url


def test_shorten_very_long_url(service):
    """Test shortening a very long URL"""
    
    long_path = '/'.join([f'segment{i}' for i in range(50)])
    url = f'https://example.com/{long_path}?param=value'
    
    short_code = service.shorten(url)
    assert len(short_code) == 6
    
    # Resolve and verify
    resolved = service.resolve(short_code)
    assert resolved == url


def test_concurrent_resolves_maintain_accurate_count(service):
    """Test that multiple resolves maintain accurate counter"""
    
    short_code = service.shorten("https://example.com/concurrent")
    
    # Resolve 10 times
    for _ in range(10):
        service.resolve(short_code)
    
    # Verify count is exactly 10
    stats = service.get_stats(short_code)
    assert stats['visit_count'] == 10


def test_url_with_https(service):
    """Test HTTPS URLs work correctly"""
    
    url = "https://secure.example.com/path"
    code = service.shorten(url)
    resolved = service.resolve(code)
    assert resolved == url


def test_url_with_http(service):
    """Test HTTP URLs work correctly"""
    
    url = "http://example.com/path"
    code = service.shorten(url)
    resolved = service.resolve(code)
    assert resolved == url


# ============================================================================
# DATA INTEGRITY TESTS
# ============================================================================

def test_short_codes_are_unique(service):
    """Test that all generated short codes are unique"""
    
    codes = []
    for i in range(20):
        code = service.shorten(f'https://example.com/page{i}')
        codes.append(code)
    
    # All should be unique
    assert len(codes) == len(set(codes))


def test_visit_count_starts_at_zero(service):
    """Test that new URLs have visit count of 0"""
    
    short_code = service.shorten("https://example.com/newurl")
    stats = service.get_stats(short_code)
    assert stats['visit_count'] == 0


def test_created_at_is_set(service):
    """Test that created_at timestamp is set"""
    
    short_code = service.shorten("https://example.com/timestamped")
    stats = service.get_stats(short_code)
    assert 'created_at' in stats
    assert stats['created_at'] is not None


def test_url_id_is_unique(service):
    """Test that each URL gets a unique ID"""
    
    code1 = service.shorten("https://example.com/id1")
    code2 = service.shorten("https://example.com/id2")
    
    stats1 = service.get_stats(code1)
    stats2 = service.get_stats(code2)
    
    assert stats1['url_id'] != stats2['url_id']


# ============================================================================
# BUSINESS LOGIC TESTS
# ============================================================================

def test_same_url_different_protocols_are_different(service):
    """Test that http and https versions are treated as different URLs"""
    
    code1 = service.shorten("http://example.com/page")
    code2 = service.shorten("https://example.com/page")
    
    # Should have different codes
    assert code1 != code2
    
    # Should have 2 URLs
    assert len(service.list_all()) == 2


def test_urls_with_trailing_slash_treated_as_different(service):
    """Test URL normalization behavior"""
    
    code1 = service.shorten("https://example.com/page")
    code2 = service.shorten("https://example.com/page/")
    
    # These are different URLs (no normalization)
    assert code1 != code2


def test_case_sensitive_urls(service):
    """Test that URLs are case-sensitive"""
    
    code1 = service.shorten("https://example.com/Page")
    code2 = service.shorten("https://example.com/page")
    
    # Should be different
    assert code1 != code2


def test_resolve_increments_only_target_url(service):
    """Test that resolving one URL doesn't affect others"""
    
    code1 = service.shorten("https://example.com/url1")
    code2 = service.shorten("https://example.com/url2")
    
    # Resolve first URL 3 times
    for _ in range(3):
        service.resolve(code1)
    
    # Check counts
    stats1 = service.get_stats(code1)
    stats2 = service.get_stats(code2)
    
    assert stats1['visit_count'] == 3
    assert stats2['visit_count'] == 0


def test_stats_contain_all_fields(service):
    """Test that stats return all expected fields"""
    
    short_code = service.shorten("https://example.com/stats")
    stats = service.get_stats(short_code)
    
    required_fields = ['short_code', 'long_url', 'visit_count', 'created_at', 'url_id']
    for field in required_fields:
        assert field in stats