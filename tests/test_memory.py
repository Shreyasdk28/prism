import pytest
import sys, os

# Add src directory to path so that shop_agent can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from shop_agent.memory import MemoryManager, memory_manager
from datetime import datetime

def test_short_term_memory_write_read_clear():
    # Ensure fresh state
    memory_manager.clear_short()

    # Write and read
    memory_manager.write_short('key1', 'value1')
    assert memory_manager.read_short('key1') == 'value1'

    # Overwrite existing key
    memory_manager.write_short('key1', 'value2')
    assert memory_manager.read_short('key1') == 'value2'

    # Clear and confirm
    memory_manager.clear_short()
    assert memory_manager.read_short('key1') is None


def test_episodic_memory_append_and_retrieve():
    # Reset episodic list
    mem = MemoryManager()  # gets singleton
    mem.episodic.clear()

    # Append episodes
    episode_data1 = {'query': 'test1', 'result': [1, 2, 3]}
    episode_data2 = {'query': 'test2', 'result': [4, 5]}
    mem.append_episode(episode_data1)
    mem.append_episode(episode_data2)

    episodes = mem.get_episodes()
    assert len(episodes) == 2
    # Check that timestamp field was added and keys exist
    for ep, orig in zip(episodes, [episode_data1, episode_data2]):
        assert 'timestamp' in ep
        assert ep['query'] == orig['query']
        assert ep['result'] == orig['result']


def test_long_term_memory_write_read():
    # Use a fresh user_id context
    user_id = 'user123'
    # Clear any existing long-term for this user
    mem = MemoryManager()
    mem.long_term.pop(user_id, None)

    # Write preferences
    mem.write_long(user_id, 'pref_brand', ['BrandA', 'BrandB'])
    mem.write_long(user_id, 'price_range', {'min': 10, 'max': 100})

    # Read back
    assert mem.read_long(user_id, 'pref_brand') == ['BrandA', 'BrandB']
    assert mem.read_long(user_id, 'price_range') == {'min': 10, 'max': 100}

    # Reading non-existent key returns None
    assert mem.read_long(user_id, 'nonexistent') is None

if __name__ == '__main__':
    pytest.main()
