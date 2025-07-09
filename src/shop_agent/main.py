import sys, os, warnings, uuid, json
from datetime import datetime
from shop_agent.memory import memory_manager
from shop_agent.crew import ShopAgent

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def get_user_preferences(user_id: str, item_name: str):
    path = os.path.join("knowledge", "user_preferences.json")
    if not os.path.exists(path):
        return None
    try:
        with open(path, 'r') as f:
            all_prefs = json.load(f)
        return all_prefs.get(user_id, {}).get(item_name)
    except json.JSONDecodeError:
        return None

def get_user_input():
    product = input(
        "Product category (e.g., wireless earbuds) or type 'exit' to quit: "
    ).strip()
    if product.lower() == 'exit':
        return None
    details = input("Describe your needs (color, budget, must-have features): ").strip()
    return {'target_item': product, 'item_details': details}

def run():
    session_user_id = str(uuid.uuid4())
    print(f"\U0001F4A1 New session: {session_user_id}\n")
    memory_manager.clear_short()
    while True:
        try:
            user_data = get_user_input()
            if user_data is None:
                print("\n\U0001F44B Exiting Smart Shopping Assistant. Goodbye!")
                memory_manager.clear_episodes()
                memory_manager.clear_short()
                print("\U0001F9E0 Episodic and short-term memory cleared.\n")
                break

            start_time = datetime.now()
            long_prefs = get_user_preferences(session_user_id, user_data['target_item'])

            # --- Sanitize episodic history for CrewAI ---
            episode_history_raw = memory_manager.get_episodes(session_user_id)
            episode_history = []
            for ep in episode_history_raw:
                # Remove or convert any non-serializable fields (e.g. ObjectId)
                ep.pop('_id', None)
                episode_history.append(ep)

            last_final_items = memory_manager.read_short('last_final_items')

            print(f"\n\U0001F50D Searching for {user_data['target_item']} with specs: {user_data['item_details']}")
            print(f"   • Injected long-term prefs: {long_prefs}")
            print(f"   • Last final_items in short-term: {bool(last_final_items)}")
            print(f"   • Episode history count: {len(episode_history)}\n")

            raw_output = ShopAgent().crew().kickoff(inputs={
                'target_item': user_data['target_item'],
                'item_details': user_data['item_details'],
                'short_term': {'last_final_items': last_final_items} if last_final_items else {},
                'long_term_preferences': long_prefs,
                'episode_history': episode_history
            })

            final_items = getattr(raw_output, 'result', None) or str(raw_output)
            print("\n\U0001F516 Final Recommendations:\n")
            print(final_items)

            episode = {
                'user_id': session_user_id,
                'query': user_data['target_item'],
                'item_details': user_data['item_details'],
                'final_items': final_items,
                'timestamp': datetime.now().isoformat()
            }
            memory_manager.append_episode(episode)
            memory_manager.write_short('last_final_items', final_items)

            elapsed = (datetime.now() - start_time).total_seconds()
            print(f"\n✅ Completed in {elapsed:.1f}s\n")

        except Exception as e:
            print(f"\n❌ Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    run()
