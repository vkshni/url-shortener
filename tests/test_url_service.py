import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from pathlib import Path
from url_service import URLService
from storage import URLDB
from url_entity import URL

TEST_FILE = "test_service_urls.json"


@pytest.fixture
def service():
    """Create a fresh service with test database"""
    db = URLDB(TEST_FILE)
    yield URLService(db)
    
    # Cleanup
    test_path = Path(__file__).parent.parent / TEST_FILE
    if test_path.exists():
        test_path.unlink()


def test_shorten_url(service):
    """Test shortening a URL"""
    long_url = "https://example.com/very/long/path"
    short_code = service.shorten(long_url)
    
    assert short_code is not None
    assert len(short_code) == 6
    assert isinstance(short_code, str)


def test_shorten_returns_existing_code_for_duplicate_url(service):
    """Test that shortening same URL returns same code"""
    long_url = "https://example.com/test"
    
    code1 = service.shorten(long_url)
    code2 = service.shorten(long_url)
    
    assert code1 == code2


def test_shorten_different_urls_get_different_codes(service):
    """Test different URLs get different short codes"""
    url1 = "https://example.com/page1"
    url2 = "https://example.com/page2"
    
    code1 = service.shorten(url1)
    code2 = service.shorten(url2)
    
    assert code1 != code2


def test_resolve_returns_original_url(service):
    """Test resolving a short code returns the original URL"""
    long_url = "https://github.com/user/repo"
    short_code = service.shorten(long_url)
    
    resolved = service.resolve(short_code)
    
    assert resolved == long_url


def test_resolve_increments_visit_count(service):
    """Test that resolving increments the visit count"""
    long_url = "https://example.com/popular"
    short_code = service.shorten(long_url)
    
    # Resolve multiple times
    service.resolve(short_code)
    service.resolve(short_code)
    service.resolve(short_code)
    
    stats = service.get_stats(short_code)
    assert stats['visit_count'] == 3


def test_resolve_nonexistent_code_raises_error(service):
    """Test resolving non-existent code raises ValueError"""
    with pytest.raises(ValueError, match="not found"):
        service.resolve("notfound")


def test_list_all_empty(service):
    """Test listing all URLs when database is empty"""
    urls = service.list_all()
    assert len(urls) == 0


def test_list_all_returns_all_urls(service):
    """Test listing all URLs returns all shortened URLs"""
    service.shorten("https://one.com")
    service.shorten("https://two.com")
    service.shorten("https://three.com")
    
    urls = service.list_all()
    
    assert len(urls) == 3
    assert all(isinstance(u, URL) for u in urls)


def test_get_stats_returns_correct_info(service):
    """Test getting stats returns all relevant information"""
    long_url = "https://example.com/stats"
    short_code = service.shorten(long_url)
    
    stats = service.get_stats(short_code)
    
    assert stats['short_code'] == short_code
    assert stats['long_url'] == long_url
    assert stats['visit_count'] == 0
    assert 'created_at' in stats
    assert 'url_id' in stats


def test_get_stats_nonexistent_raises_error(service):
    """Test getting stats for non-existent code raises error"""
    with pytest.raises(ValueError, match="not found"):
        service.get_stats("invalid")


def test_collision_handling(service):
    """Test that collision handling works by forcing many URLs"""
    # Generate 100 URLs - should handle any collisions automatically
    urls = []
    for i in range(100):
        url = f"https://example.com/page{i}"
        code = service.shorten(url)
        urls.append(code)
    
    # All codes should be unique
    assert len(set(urls)) == 100


def test_shorten_and_resolve_workflow(service):
    """Test complete workflow: shorten -> resolve -> check visits"""
    long_url = "https://workflow.test.com/complete"
    
    # Shorten
    short_code = service.shorten(long_url)
    assert short_code is not None
    
    # Resolve first time
    resolved1 = service.resolve(short_code)
    assert resolved1 == long_url
    
    # Resolve second time
    resolved2 = service.resolve(short_code)
    assert resolved2 == long_url
    
    # Check stats
    stats = service.get_stats(short_code)
    assert stats['visit_count'] == 2
    assert stats['long_url'] == long_url


def test_multiple_services_share_same_db(service):
    """Test that multiple service instances can share the same database"""
    # Service 1 shortens URL
    long_url = "https://shared.com/test"
    code = service.shorten(long_url)
    
    # Service 2 with same DB file should see the URL
    service2 = URLService(URLDB(TEST_FILE))
    resolved = service2.resolve(code)
    
    assert resolved == long_url


def test_visit_count_persists_across_service_instances(service):
    """Test visit count persists across service restarts"""
    long_url = "https://persist.com/visits"
    code = service.shorten(long_url)
    
    # Make some visits
    service.resolve(code)
    service.resolve(code)
    
    # Create new service instance (simulates restart)
    service2 = URLService(URLDB(TEST_FILE))
    
    # Continue visiting
    service2.resolve(code)
    
    # Check total visits
    stats = service2.get_stats(code)
    assert stats['visit_count'] == 3