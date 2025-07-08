import threading
import os
import json
from datetime import datetime

# File where episodic memory is stored
EPISODIC_FILE = os.path.join('knowledge', 'episodic_memory.jsonl')

class MemoryManager:
    """
    Singleton manager for handling short-term, episodic, and long-term memory.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MemoryManager, cls).__new__(cls)
                cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        # In-memory stores
        self.short_term = {}
        self.episodic = []
        self.long_term = {}

        # Ensure the knowledge folder exists
        os.makedirs('knowledge', exist_ok=True)

    # Short-term memory
    def write_short(self, key: str, value):
        self.short_term[key] = value

    def read_short(self, key: str):
        return self.short_term.get(key)

    def clear_short(self):
        self.short_term.clear()

    # Episodic memory
    def append_episode(self, episode_data: dict):
        episode = {
            'timestamp': datetime.utcnow().isoformat(),
            **episode_data
        }
        # Persist to file
        with open(EPISODIC_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(episode) + '\n')

        # Update in-memory cache
        self.episodic.append(episode)

    def get_episodes(self, user_id: str = None) -> list:
        if not os.path.exists(EPISODIC_FILE):
            return []

        episodes = []
        with open(EPISODIC_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    ep = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if user_id is None or ep.get('user_id') == user_id:
                    episodes.append(ep)
        return episodes

    def clear_episodes(self):
        if os.path.exists(EPISODIC_FILE):
            open(EPISODIC_FILE, 'w', encoding='utf-8').close()
        self.episodic = []

    # Long-term memory
    def write_long(self, user_id: str, key: str, value):
        if user_id not in self.long_term:
            self.long_term[user_id] = {}
        self.long_term[user_id][key] = value

    def read_long(self, user_id: str, key: str):
        return self.long_term.get(user_id, {}).get(key)
    
    def send_message(self, from_agent: str, to_agent: str, message: str):
        if not hasattr(self, 'messages'):
            self.messages = {}
        if to_agent not in self.messages:
            self.messages[to_agent] = []
        self.messages[to_agent].append({'from': from_agent, 'message': message})

    def get_messages(self, agent_name: str):
        if not hasattr(self, 'messages'):
            self.messages = {}
        msgs = self.messages.get(agent_name, [])
        self.messages[agent_name] = []
        return msgs

    def share_data(self, key: str, value):
        if not hasattr(self, 'shared_data'):
            self.shared_data = {}
        self.shared_data[key] = value

    def get_shared_data(self, key: str):
        if not hasattr(self, 'shared_data'):
            self.shared_data = {}
        return self.shared_data.get(key)

# Provide a module-level singleton instance
memory_manager = MemoryManager()