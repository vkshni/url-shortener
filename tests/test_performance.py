import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import time
from pathlib import Path
from url_service import URLService
from storage import URLDB

TEST_FILE = "test_performance_urls.json"


@pytest.fixture
def service():
    """Create service with test database"""
    db = URLDB(TEST_FILE)
    yield URLService(db)
    
    # Cleanup
    test_path = Path(__file__).parent.parent / TEST_FILE
    if test_path.exists():
        test_path.unlink()


def test_resolve_speed_single_url(service):
    """Test that resolving a single URL is fast"""
    # Setup
    long_url = "https://example.com/test"
    short_code = service.shorten(long_url)
    
    # Measure resolve time
    start = time.time()
    resolved = service.resolve(short_code)
    end = time.time()
    
    duration = end - start
    
    assert resolved == long_url
    assert duration < 0.1  # Should be under 100ms
    print(f"\n✓ Single resolve took: {duration*1000:.2f}ms")


def test_resolve_speed_with_100_urls(service):
    """Test resolve performance with 100 URLs in database"""
    # Add 100 URLs
    codes = []
    for i in range(100):
        url = f"https://example.com/page{i}"
        code = service.shorten(url)
        codes.append(code)
    
    # Measure resolve time for last URL (worst case - searched last)
    test_code = codes[-1]
    
    start = time.time()
    service.resolve(test_code)
    end = time.time()
    
    duration = end - start
    
    assert duration < 0.2  # Should be under 200ms even with 100 URLs
    print(f"\n✓ Resolve with 100 URLs took: {duration*1000:.2f}ms")


def test_resolve_speed_with_1000_urls(service):
    """Test resolve performance with 1000 URLs in database"""
    # Add 1000 URLs
    codes = []
    print("\n⏳ Adding 1000 URLs...")
    
    for i in range(1000):
        url = f"https://example.com/page{i}"
        code = service.shorten(url)
        codes.append(code)
    
    # Measure resolve time
    test_code = codes[500]  # Middle of dataset
    
    start = time.time()
    service.resolve(test_code)
    end = time.time()
    
    duration = end - start
    
    assert duration < 0.5  # Should be under 500ms with 1000 URLs
    print(f"\n✓ Resolve with 1000 URLs took: {duration*1000:.2f}ms")


def test_resolve_100_times_same_code(service):
    """Test resolving the same code 100 times (stress test)"""
    # Setup
    long_url = "https://example.com/popular"
    short_code = service.shorten(long_url)
    
    # Resolve 100 times
    start = time.time()
    for _ in range(100):
        service.resolve(short_code)
    end = time.time()
    
    total_duration = end - start
    avg_duration = total_duration / 100
    
    # Check visit count
    stats = service.get_stats(short_code)
    
    assert stats['visit_count'] == 100
    assert total_duration < 10  # 100 resolves should take less than 10 seconds
    print(f"\n✓ 100 resolves took: {total_duration:.2f}s (avg: {avg_duration*1000:.2f}ms each)")


def test_visit_count_accuracy_under_load(service):
    """Test that visit counter remains accurate under repeated access"""
    long_url = "https://example.com/counter-test"
    short_code = service.shorten(long_url)
    
    # Resolve 50 times
    for i in range(50):
        service.resolve(short_code)
        
        # Periodically check accuracy
        if (i + 1) % 10 == 0:
            stats = service.get_stats(short_code)
            assert stats['visit_count'] == i + 1, f"Expected {i+1}, got {stats['visit_count']}"
    
    # Final check
    final_stats = service.get_stats(short_code)
    assert final_stats['visit_count'] == 50
    print(f"\n✓ Visit count accurate: {final_stats['visit_count']}/50")


def test_visit_count_persists_across_service_restarts(service):
    """Test that visit counts survive program restarts"""
    long_url = "https://example.com/persist-visits"
    short_code = service.shorten(long_url)
    
    # Make some visits
    for _ in range(10):
        service.resolve(short_code)
    
    # Verify count
    stats1 = service.get_stats(short_code)
    assert stats1['visit_count'] == 10
    
    # Simulate restart: create new service instance
    service2 = URLService(URLDB(TEST_FILE))
    
    # Make more visits
    for _ in range(5):
        service2.resolve(short_code)
    
    # Total should be 15
    stats2 = service2.get_stats(short_code)
    assert stats2['visit_count'] == 15
    print(f"\n✓ Visit count persisted across restart: {stats2['visit_count']}")


def test_resolve_does_not_slow_down_over_time(service):
    """Test that repeated resolves don't degrade performance"""
    long_url = "https://example.com/timing-test"
    short_code = service.shorten(long_url)
    
    timings = []
    
    # Resolve 20 times and record each timing
    for i in range(20):
        start = time.time()
        service.resolve(short_code)
        end = time.time()
        timings.append(end - start)
    
    # First 10 vs last 10 should be similar
    first_10_avg = sum(timings[:10]) / 10
    last_10_avg = sum(timings[10:]) / 10
    
    # Last 10 shouldn't be more than 2x slower than first 10
    assert last_10_avg < first_10_avg * 2
    print(f"\n✓ First 10 avg: {first_10_avg*1000:.2f}ms, Last 10 avg: {last_10_avg*1000:.2f}ms")


def test_multiple_urls_resolve_independently(service):
    """Test that resolving one URL doesn't affect others"""
    # Create 10 URLs
    urls_and_codes = []
    for i in range(10):
        url = f"https://example.com/independent{i}"
        code = service.shorten(url)
        urls_and_codes.append((url, code))
    
    # Resolve each 5 times
    for url, code in urls_and_codes:
        for _ in range(5):
            service.resolve(code)
    
    # Check each has exactly 5 visits
    for url, code in urls_and_codes:
        stats = service.get_stats(code)
        assert stats['visit_count'] == 5
        assert stats['long_url'] == url
    
    print(f"\n✓ All 10 URLs maintained independent visit counts")


def test_file_size_growth(service):
    """Monitor how file size grows with URLs"""
    test_path = Path(__file__).parent.parent / TEST_FILE
    
    # Initial size
    service.shorten("https://example.com/initial")
    size_1 = test_path.stat().st_size
    
    # Add 100 more
    for i in range(100):
        service.shorten(f"https://example.com/page{i}")
    size_101 = test_path.stat().st_size
    
    # Add 100 more
    for i in range(100, 200):
        service.shorten(f"https://example.com/page{i}")
    size_201 = test_path.stat().st_size
    
    print(f"\n✓ File sizes: 1 URL={size_1}b, 101 URLs={size_101}b, 201 URLs={size_201}b")
    
    # File should grow linearly, not exponentially
    growth_rate_1 = (size_101 - size_1) / 100
    growth_rate_2 = (size_201 - size_101) / 100
    
    # Growth rate shouldn't increase by more than 20%
    assert growth_rate_2 < growth_rate_1 * 1.2