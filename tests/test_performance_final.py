import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import time
from pathlib import Path
from url_service import URLService
from storage import URLDB
import json

TEST_FILE = "test_performance_final.json"


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
# SINGLE OPERATION PERFORMANCE
# ============================================================================

def test_single_shorten_performance(service):
    """Test that shortening a single URL is fast"""
    url = "https://example.com/test"
    
    start = time.time()
    code = service.shorten(url)
    duration = time.time() - start
    
    assert code is not None
    assert duration < 0.5  # Should take less than 500ms
    print(f"\n✓ Single shorten: {duration*1000:.2f}ms")


def test_single_resolve_performance(service):
    """Test that resolving a single code is fast"""
    code = service.shorten("https://example.com/test")
    
    start = time.time()
    url = service.resolve(code)
    duration = time.time() - start
    
    assert url is not None
    assert duration < 0.5  # Should take less than 500ms
    print(f"\n✓ Single resolve: {duration*1000:.2f}ms")


def test_single_list_performance(service):
    """Test that listing is fast with a few URLs"""
    # Add 10 URLs
    for i in range(10):
        service.shorten(f"https://example.com/page{i}")
    
    start = time.time()
    urls = service.list_all()
    duration = time.time() - start
    
    assert len(urls) == 10
    assert duration < 0.5  # Should be instant
    print(f"\n✓ List 10 URLs: {duration*1000:.2f}ms")


# ============================================================================
# BULK SHORTEN PERFORMANCE
# ============================================================================

def test_shorten_100_urls_performance(service):
    """Test shortening 100 URLs"""
    start = time.time()
    
    codes = []
    for i in range(100):
        code = service.shorten(f"https://example.com/page{i}")
        codes.append(code)
    
    duration = time.time() - start
    avg_per_url = (duration / 100) * 1000
    
    assert len(codes) == 100
    print(f"\n✓ Shortened 100 URLs in {duration:.2f}s ({avg_per_url:.2f}ms per URL)")
    
    # Document acceptable performance (adjust based on your results)
    # This is informational, not a hard requirement
    if duration > 10:
        print(f"  ⚠️  This is slow - consider optimization")


def test_shorten_500_urls_performance(service):
    """Test shortening 500 URLs"""
    start = time.time()
    
    codes = []
    for i in range(500):
        code = service.shorten(f"https://example.com/page{i}")
        codes.append(code)
    
    duration = time.time() - start
    avg_per_url = (duration / 500) * 1000
    
    assert len(codes) == 500
    assert len(set(codes)) == 500  # All unique
    print(f"\n✓ Shortened 500 URLs in {duration:.2f}s ({avg_per_url:.2f}ms per URL)")


def test_shorten_1000_urls_performance(service):
    """Test shortening 1000 URLs (stress test)"""
    print("\n⏳ Shortening 1000 URLs (this may take a while)...")
    start = time.time()
    
    codes = []
    for i in range(1000):
        if i % 100 == 0 and i > 0:
            elapsed = time.time() - start
            print(f"   Progress: {i}/1000 ({elapsed:.1f}s elapsed)")
        
        code = service.shorten(f"https://example.com/page{i}")
        codes.append(code)
    
    duration = time.time() - start
    avg_per_url = (duration / 1000) * 1000
    
    assert len(codes) == 1000
    assert len(set(codes)) == 1000  # All unique
    print(f"\n✓ Shortened 1000 URLs in {duration:.2f}s ({avg_per_url:.2f}ms per URL)")
    
    # Performance benchmarks (informational)
    if duration < 5:
        print("  🚀 Excellent performance!")
    elif duration < 30:
        print("  ✓ Good performance")
    elif duration < 60:
        print("  ⚠️  Acceptable performance for CLI")
    else:
        print("  ⚠️  Slow - consider optimization for larger datasets")


# ============================================================================
# BULK RESOLVE PERFORMANCE
# ============================================================================

def test_resolve_100_urls_performance(service):
    """Test resolving 100 different codes"""
    # Setup: Create 100 URLs
    codes = []
    for i in range(100):
        code = service.shorten(f"https://example.com/page{i}")
        codes.append(code)
    
    # Test: Resolve all
    start = time.time()
    for code in codes:
        service.resolve(code)
    duration = time.time() - start
    
    avg_per_resolve = (duration / 100) * 1000
    print(f"\n✓ Resolved 100 URLs in {duration:.2f}s ({avg_per_resolve:.2f}ms per resolve)")


def test_resolve_same_code_1000_times_performance(service):
    """Test resolving the same code 1000 times"""
    code = service.shorten("https://example.com/popular")
    
    start = time.time()
    for _ in range(1000):
        service.resolve(code)
    duration = time.time() - start
    
    avg_per_resolve = (duration / 1000) * 1000
    
    # Verify correctness
    stats = service.get_stats(code)
    assert stats['visit_count'] == 1000
    
    print(f"\n✓ Resolved same code 1000x in {duration:.2f}s ({avg_per_resolve:.2f}ms per resolve)")


# ============================================================================
# LIST PERFORMANCE AT SCALE
# ============================================================================

def test_list_100_urls_performance(service):
    """Test listing 100 URLs"""
    # Setup
    for i in range(100):
        service.shorten(f"https://example.com/page{i}")
    
    # Test
    start = time.time()
    urls = service.list_all()
    duration = time.time() - start
    
    assert len(urls) == 100
    print(f"\n✓ Listed 100 URLs in {duration*1000:.2f}ms")


def test_list_500_urls_performance(service):
    """Test listing 500 URLs"""
    # Setup
    print("\n⏳ Adding 500 URLs for list test...")
    for i in range(500):
        service.shorten(f"https://example.com/page{i}")
    
    # Test
    start = time.time()
    urls = service.list_all()
    duration = time.time() - start
    
    assert len(urls) == 500
    print(f"\n✓ Listed 500 URLs in {duration*1000:.2f}ms")


# ============================================================================
# MIXED OPERATIONS PERFORMANCE
# ============================================================================

def test_mixed_operations_performance(service):
    """Test realistic mix of operations"""
    print("\n⏳ Running mixed operations test...")
    
    start = time.time()
    codes = []
    
    # Simulate realistic usage
    for i in range(100):
        # Shorten 3 URLs
        for j in range(3):
            code = service.shorten(f"https://example.com/page{i}-{j}")
            codes.append(code)
        
        # Resolve some random codes
        if codes:
            service.resolve(codes[0])
            if len(codes) > 5:
                service.resolve(codes[-5])
        
        # List occasionally
        if i % 20 == 0:
            service.list_all()
    
    duration = time.time() - start
    
    total_operations = 300 + 200 + 5  # 300 shortens, 200 resolves, 5 lists
    avg_per_op = (duration / total_operations) * 1000
    
    print(f"\n✓ Mixed operations (300 shorten, 200 resolve, 5 list) in {duration:.2f}s")
    print(f"  Average: {avg_per_op:.2f}ms per operation")


# ============================================================================
# FILE SIZE GROWTH TESTS
# ============================================================================

def test_file_size_with_10_urls(service):
    """Measure file size with 10 URLs"""
    for i in range(10):
        service.shorten(f"https://example.com/page{i}")
    
    test_path = Path(__file__).parent.parent / TEST_FILE
    size = test_path.stat().st_size
    
    print(f"\n✓ File size with 10 URLs: {size:,} bytes ({size/1024:.2f} KB)")


def test_file_size_with_100_urls(service):
    """Measure file size with 100 URLs"""
    for i in range(100):
        service.shorten(f"https://example.com/page{i}")
    
    test_path = Path(__file__).parent.parent / TEST_FILE
    size = test_path.stat().st_size
    
    print(f"\n✓ File size with 100 URLs: {size:,} bytes ({size/1024:.2f} KB)")


def test_file_size_with_500_urls(service):
    """Measure file size with 500 URLs"""
    print("\n⏳ Adding 500 URLs to measure file size...")
    for i in range(500):
        service.shorten(f"https://example.com/page{i}")
    
    test_path = Path(__file__).parent.parent / TEST_FILE
    size = test_path.stat().st_size
    
    print(f"\n✓ File size with 500 URLs: {size:,} bytes ({size/1024:.2f} KB)")
    
    # Check linear growth (roughly)
    bytes_per_url = size / 500
    print(f"  Average: {bytes_per_url:.0f} bytes per URL")
    
    # Estimate for 10,000 URLs
    estimated_10k = (bytes_per_url * 10000) / (1024 * 1024)
    print(f"  Estimated size for 10,000 URLs: {estimated_10k:.2f} MB")


def test_file_size_growth_is_linear(service):
    """Verify file size grows linearly, not exponentially"""
    test_path = Path(__file__).parent.parent / TEST_FILE
    
    sizes = []
    
    # Measure at different scales
    for count in [10, 50, 100]:
        # Clear and recreate
        if test_path.exists():
            test_path.unlink()
        service.db = URLDB(TEST_FILE)
        
        # Add URLs
        for i in range(count):
            service.shorten(f"https://example.com/item{i}")
        
        size = test_path.stat().st_size
        sizes.append((count, size))
        print(f"  {count} URLs → {size:,} bytes")
    
    # Check growth rate
    growth_10_to_50 = sizes[1][1] / sizes[0][1]
    growth_50_to_100 = sizes[2][1] / sizes[1][1]
    
    print(f"\n  Growth 10→50: {growth_10_to_50:.2f}x")
    print(f"  Growth 50→100: {growth_50_to_100:.2f}x")
    
    # Should be roughly linear (2x growth for 2x URLs)
    # Allow some variance for JSON overhead
    assert 3 < growth_10_to_50 < 7  # Roughly 5x for 5x URLs
    assert 1.5 < growth_50_to_100 < 2.5  # Roughly 2x for 2x URLs


# ============================================================================
# PERFORMANCE DEGRADATION TESTS
# ============================================================================

def test_no_performance_degradation_over_time(service):
    """Test that performance doesn't degrade as database grows"""
    times = []
    
    # Measure resolve time at different database sizes
    for batch in range(5):
        # Add 50 URLs
        for i in range(50):
            service.shorten(f"https://example.com/batch{batch}-item{i}")
        
        # Measure resolve time
        code = service.shorten(f"https://example.com/test{batch}")
        
        start = time.time()
        for _ in range(10):
            service.resolve(code)
        duration = time.time() - start
        
        avg_time = (duration / 10) * 1000
        times.append(avg_time)
        print(f"  After {(batch+1)*50} URLs: {avg_time:.2f}ms per resolve")
    
    # First vs last should be similar (not 10x slower)
    degradation = times[-1] / times[0]
    print(f"\n  Performance degradation: {degradation:.2f}x")
    
    # Allow some slowdown but not exponential
    assert degradation < 5  # No more than 5x slower


def test_resolve_performance_with_large_db(service):
    """Test resolve performance with large database"""
    # Create large database
    print("\n⏳ Creating database with 500 URLs...")
    codes = []
    for i in range(500):
        code = service.shorten(f"https://example.com/large{i}")
        codes.append(code)
    
    # Test resolve performance
    print("Testing resolve performance...")
    
    # Resolve first URL (worst case if searching from start)
    start = time.time()
    service.resolve(codes[0])
    time_first = (time.time() - start) * 1000
    
    # Resolve last URL (worst case if searching from end)
    start = time.time()
    service.resolve(codes[-1])
    time_last = (time.time() - start) * 1000
    
    # Resolve middle URL
    start = time.time()
    service.resolve(codes[len(codes)//2])
    time_middle = (time.time() - start) * 1000
    
    print(f"\n  Resolve first URL: {time_first:.2f}ms")
    print(f"  Resolve middle URL: {time_middle:.2f}ms")
    print(f"  Resolve last URL: {time_last:.2f}ms")
    
    # All should be reasonable
    assert time_first < 500  # Less than 500ms
    assert time_middle < 500
    assert time_last < 500


# ============================================================================
# MEMORY AND RESOURCE TESTS
# ============================================================================

def test_repeated_operations_no_memory_leak(service):
    """Test that repeated operations don't cause memory issues"""
    # This is a basic test - for real memory testing you'd use memory_profiler
    
    code = service.shorten("https://example.com/test")
    
    # Perform 1000 operations
    for i in range(1000):
        service.resolve(code)
        if i % 100 == 0:
            service.list_all()
    
    # If we got here without crashing, that's good
    stats = service.get_stats(code)
    assert stats['visit_count'] == 1000
    print(f"\n✓ 1000 operations completed without issues")


# ============================================================================
# PERFORMANCE SUMMARY
# ============================================================================

def test_performance_summary(service):
    """Generate a performance summary report"""
    print("\n" + "="*60)
    print("PERFORMANCE SUMMARY")
    print("="*60)
    
    # Single operations
    print("\n📊 Single Operations:")
    start = time.time()
    code = service.shorten("https://example.com/test")
    shorten_time = (time.time() - start) * 1000
    print(f"  Shorten: {shorten_time:.2f}ms")
    
    start = time.time()
    service.resolve(code)
    resolve_time = (time.time() - start) * 1000
    print(f"  Resolve: {resolve_time:.2f}ms")
    
    # Bulk operations
    print("\n📊 Bulk Operations (100 URLs):")
    service.db = URLDB(TEST_FILE)  # Fresh start
    
    start = time.time()
    for i in range(100):
        service.shorten(f"https://example.com/bulk{i}")
    bulk_time = time.time() - start
    print(f"  100 shortens: {bulk_time:.2f}s ({bulk_time*10:.2f}ms avg)")
    
    # File size
    test_path = Path(__file__).parent.parent / TEST_FILE
    size = test_path.stat().st_size
    print(f"\n📊 Storage:")
    print(f"  100 URLs: {size:,} bytes ({size/1024:.2f} KB)")
    print(f"  Per URL: ~{size/100:.0f} bytes")
    
    print("\n" + "="*60)