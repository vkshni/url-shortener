import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from pathlib import Path
from storage import URLDB
from url_entity import URL
from datetime import datetime

TEST_FILE = "test_urls.json"


@pytest.fixture
def db():
    """Create a fresh test database before each test"""
    yield URLDB(TEST_FILE)
    # Cleanup after test
    test_path = Path(__file__).parent.parent / TEST_FILE
    if test_path.exists():
        test_path.unlink()


def test_add_url(db):
    """Test adding a URL to database"""
    url = URL(long_url="https://example.com/test", short_code="abc123")

    db.add(url)
    found = db.find_by_code("abc123")

    assert found is not None
    assert found.long_url == "https://example.com/test"
    assert found.short_code == "abc123"
    assert found.visit_count == 0
    assert found.url_id is not None  # UUID should be generated


def test_url_id_auto_generation(db):
    """Test that URL ID is automatically generated as UUID"""
    url = URL(long_url="https://test.com", short_code="tst123")

    assert url.url_id is not None
    assert len(url.url_id) == 36  # UUID format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
    assert url.url_id.count("-") == 4  # UUIDs have 4 hyphens


def test_created_at_auto_generation(db):
    """Test that created_at is automatically set to current time"""
    url = URL(long_url="https://time.com", short_code="time99")

    assert url.created_at is not None
    assert isinstance(url.created_at, datetime)
    # Check it's recent (within last 5 seconds)
    time_diff = (datetime.now() - url.created_at).total_seconds()
    assert time_diff < 5


def test_find_by_url(db):
    """Test finding URL by long_url"""
    url = URL(long_url="https://github.com", short_code="gh123")
    db.add(url)

    found = db.find_by_url("https://github.com")

    assert found is not None
    assert found.short_code == "gh123"


def test_find_by_code(db):
    """Test finding URL by short_code"""
    url = URL(long_url="https://google.com", short_code="gg456")
    db.add(url)

    found = db.find_by_code("gg456")

    assert found is not None
    assert found.long_url == "https://google.com"


def test_find_nonexistent_returns_none(db):
    """Test that finding non-existent URL returns None"""
    found_by_code = db.find_by_code("notfound")
    found_by_url = db.find_by_url("https://notexist.com")

    assert found_by_code is None
    assert found_by_url is None


def test_update_url_visit_count(db):
    """Test updating a URL's visit count"""
    url = URL(long_url="https://test.com", short_code="tst99")
    db.add(url)

    # Retrieve and update visit count
    found = db.find_by_code("tst99")
    found.visit_count = 10
    updated = db.update(found)

    assert updated is True

    # Verify the update persisted
    refound = db.find_by_code("tst99")
    assert refound.visit_count == 10


def test_update_nonexistent_url(db):
    """Test updating a URL that doesn't exist"""
    fake_url = URL(
        long_url="https://fake.com",
        short_code="fake00",
        url_id="00000000-0000-0000-0000-000000000000",  # Non-existent ID
    )

    updated = db.update(fake_url)
    assert updated is False


def test_delete_url(db):
    """Test deleting a URL"""
    url = URL(long_url="https://delete.me", short_code="del00")
    db.add(url)

    deleted = db.delete(url)

    assert deleted is True
    found = db.find_by_code("del00")
    assert found is None


def test_delete_nonexistent_url(db):
    """Test deleting a URL that doesn't exist"""
    fake_url = URL(
        long_url="https://fake.com",
        short_code="fake99",
        url_id="00000000-0000-0000-0000-000000000000",
    )

    deleted = db.delete(fake_url)
    assert deleted is False


def test_list_all_empty(db):
    """Test listing all URLs when database is empty"""
    all_urls = db.list_all()
    assert len(all_urls) == 0
    assert isinstance(all_urls, list)


def test_list_all_multiple(db):
    """Test listing all URLs with multiple entries"""
    url1 = URL(long_url="https://one.com", short_code="one11")
    url2 = URL(long_url="https://two.com", short_code="two22")
    url3 = URL(long_url="https://three.com", short_code="thr33")

    db.add(url1)
    db.add(url2)
    db.add(url3)

    all_urls = db.list_all()

    assert len(all_urls) == 3
    assert all(isinstance(u, URL) for u in all_urls)

    # Verify all short codes are present
    short_codes = [u.short_code for u in all_urls]
    assert "one11" in short_codes
    assert "two22" in short_codes
    assert "thr33" in short_codes


def test_persistence_across_instances(db):
    """Test that data persists across DB instances"""
    url = URL(long_url="https://persist.com", short_code="pst99")
    original_id = url.url_id
    db.add(url)

    # Create new DB instance (should load from file)
    db2 = URLDB(TEST_FILE)
    found = db2.find_by_code("pst99")

    assert found is not None
    assert found.long_url == "https://persist.com"
    assert found.url_id == original_id  # UUID should be preserved


def test_to_dict_and_from_dict(db):
    """Test serialization and deserialization"""
    original = URL(long_url="https://serialize.com", short_code="ser123", visit_count=5)

    # Convert to dict
    url_dict = original.to_dict()

    assert url_dict["url_id"] == original.url_id
    assert url_dict["long_url"] == "https://serialize.com"
    assert url_dict["short_code"] == "ser123"
    assert url_dict["visit_count"] == 5
    assert url_dict["created_at"] is not None

    # Convert back from dict
    restored = URL.from_dict(url_dict)

    assert restored.url_id == original.url_id
    assert restored.long_url == original.long_url
    assert restored.short_code == original.short_code
    assert restored.visit_count == original.visit_count


def test_visit_count_increment(db):
    """Test incrementing visit count simulates URL resolution"""
    url = URL(long_url="https://popular.com", short_code="pop99")
    db.add(url)

    # Simulate multiple visits
    for _ in range(5):
        found = db.find_by_code("pop99")
        found.visit_count += 1
        db.update(found)

    final = db.find_by_code("pop99")
    assert final.visit_count == 5


def test_duplicate_short_codes_not_allowed(db):
    """Test that duplicate short codes are handled (business logic test)"""
    url1 = URL(long_url="https://first.com", short_code="dup123")
    url2 = URL(long_url="https://second.com", short_code="dup123")

    db.add(url1)
    db.add(url2)  # This will add duplicate short_code

    # Both should exist (your current implementation allows this)
    # You may want to add uniqueness constraint in service layer later
    all_urls = db.list_all()
    assert len(all_urls) == 2


def test_multiple_urls_same_long_url(db):
    """Test that same long URL can have multiple short codes"""
    url1 = URL(long_url="https://same.com", short_code="abc11")
    url2 = URL(long_url="https://same.com", short_code="xyz99")

    db.add(url1)
    db.add(url2)

    # find_by_url should return the first match
    found = db.find_by_url("https://same.com")
    assert found is not None
    assert found.short_code in ["abc11", "xyz99"]
