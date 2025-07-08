#!/usr/bin/env python
import sys, os, warnings, uuid, json
from datetime import datetime
from shop_agent.crew import ShopAgent
from shop_agent.memory import memory_manager

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def get_user_preferences(user_id: str, item_name: str):
    path = "knowledge/user_preferences.json"
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
    print(f"💡 New session: {session_user_id}\n")

    # **Clear short-term memory once at session start**
    memory_manager.clear_short()

    while True:
        try:
            user_data = get_user_input()
            if user_data is None:
                print("\n👋 Exiting Smart Shopping Assistant. Goodbye!")
                memory_manager.clear_episodes()
                memory_manager.clear_short()  # clear all before exit
                print("🧠 Episodic and short-term memory cleared.\n")
                break

            start_time = datetime.now()

            # Load & inject memories
            long_prefs = get_user_preferences(session_user_id, user_data['target_item'])
            episode_history = memory_manager.get_episodes(session_user_id)
            short_term = memory_manager.short_term  # now holds last_final_items if present

            print(f"\n🔍 Searching for {user_data['target_item']} with specs: {user_data['item_details']}")
            print(f"   • Injected long-term prefs: {long_prefs}")
            print(f"   • Last final_items in short-term: {bool(short_term.get('last_final_items'))}")
            print(f"   • Episode history count: {len(episode_history)}\n")

            # Kick off the pipeline
            raw_output = ShopAgent().crew().kickoff(inputs={
                'target_item': user_data['target_item'],
                'item_details': user_data['item_details'],
                'short_term': short_term,
                'long_term_preferences': long_prefs,
                'episode_history': episode_history
            })

            final_items = getattr(raw_output, 'result', None) or str(raw_output)
            print("\n🔖 Final Recommendations:\n")
            print(final_items)

            # Snapshot episode
            episode = {
                'user_id': session_user_id,
                'query': user_data['target_item'],
                'item_details': user_data['item_details'],
                'final_items': final_items,
                'timestamp': datetime.now().isoformat()
            }
            memory_manager.append_episode(episode)

            # **Store this iteration’s final_items in short-term for next query**
            memory_manager.write_short('last_final_items', final_items)

            # --- MongoDB Output Push Section ---
            # Read output files if they exist
            results_json, final_decision_md = None, None
            try:
                with open("output/results.json") as f:
                    results_json = f.read()
            except Exception:
                results_json = None
            try:
                with open("output/final_decision.md") as f:
                    final_decision_md = f.read()
            except Exception:
                final_decision_md = None

            # Push to MongoDB using the output_push_agent if outputs exist
            if results_json or final_decision_md:
                print("\n📦 Pushing outputs to MongoDB ...")
                ShopAgent().output_push_agent().run(
                    target_item=user_data['target_item'],
                    results_json=results_json,
                    final_decision_md=final_decision_md
                )

            elapsed = (datetime.now() - start_time).total_seconds()
            print(f"\n✅ Completed in {elapsed:.1f}s\n")

        except Exception as e:
            print(f"\n❌ Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    run()