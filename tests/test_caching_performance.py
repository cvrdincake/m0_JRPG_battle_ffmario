"""Performance test for AssetManager caching.

This script verifies that caching works by loading the same sprite
multiple times and measuring the time.
"""

import pygame
import time
from src.utils.asset_manager import AssetManager


def test_caching_performance():
    """Test that caching provides significant performance improvement."""
    pygame.init()
    pygame.display.set_mode((1, 1))
    
    manager = AssetManager()
    
    # First load (will be slower - generates placeholder)
    start = time.time()
    first_sprite = manager.load_sprite("hero.png")
    first_load_time = time.time() - start
    
    # Load same sprite 1000 times (should be instant from cache)
    start = time.time()
    for i in range(1000):
        sprite = manager.load_sprite("hero.png")
        assert sprite is first_sprite  # Verify it's the same object
    cache_load_time = time.time() - start
    
    print(f"First load time: {first_load_time*1000:.2f}ms")
    print(f"1000 cached loads time: {cache_load_time*1000:.2f}ms")
    print(f"Average per cached load: {cache_load_time*1000000:.2f}μs")
    
    # Verify caching works (should be < 10ms total for 1000 loads)
    assert cache_load_time < 0.010, f"Cached loading too slow: {cache_load_time*1000:.2f}ms"
    
    print("✓ Caching performance test PASSED")
    print(f"✓ Loading sprite 1000 times took {cache_load_time*1000:.2f}ms (< 10ms requirement)")


if __name__ == "__main__":
    test_caching_performance()
