#!/usr/bin/env python
import sys, os, warnings, uuid, json
from datetime import datetime
from shop_agent.crew import ShopAgent
from shop_agent.memory import memory_manager
from shop_agent.tools.custom_tool import QdrantCustomUpsertTool 

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
     # 🔤 Ask for a consistent user identifier
    username = input("👤 Enter your username: ").strip().lower()
    session_user_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, username))
    print(f"💡 Session started for user: {username} (UUID: {session_user_id})\n")

    memory_manager.clear_short()

    episodes = []  # 🧠 Store all shopping episodes here
    qdrant_tool = QdrantCustomUpsertTool()  # 🔧 One-time init

    while True:
        try:
            user_data = get_user_input()
            if user_data is None:
                print("\n👋 Exiting Smart Shopping Assistant. Goodbye!")
                memory_manager.clear_short()
                print("🧠 Short-term memory cleared.\n")

                # ✅ Upload all episodes at once
                print("🧠 Uploading session memory to Qdrant...\n")
                for episode in episodes:
                    result = qdrant_tool._run(**episode)
                    print(f"🟢 Upsert status: {result}")

                print(f"✅ Uploaded {len(episodes)} episodes.\n")
                break

            start_time = datetime.now()

            long_prefs = get_user_preferences(session_user_id, user_data['target_item'])
            short_term = memory_manager.short_term

            print(f"\n🔍 Searching for {user_data['target_item']} with specs: {user_data['item_details']}")
            print(f"   • Injected long-term prefs: {long_prefs}")
            print(f"   • Last final_items in short-term: {bool(short_term.get('last_final_items'))}\n")

            print("🚀 Starting shopping assistant pipeline...\n")
            raw_output = ShopAgent().crew().kickoff(inputs={
                'user_id': str(session_user_id),
                'target_item': user_data['target_item'],
                'item_details': user_data['item_details'],
                'short_term': short_term,
                'long_term_preferences': long_prefs,
            })

            import re

            # If output comes in Markdown format (```json ... ```)
            def extract_json_block(text):
                if not isinstance(text, str):
                    return None
                match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
                return match.group(1) if match else text.strip()

            parsed_items = next(
                (t.raw for t in raw_output.tasks_output if t.name == "markdown_extraction_task"),
                None
            )

            # Fallback if markdown_extraction_task didn't run
            if not parsed_items and hasattr(raw_output, "final_output"):
                parsed_items = raw_output.final_output

            # Try parsing safely
            try:
                json_str = extract_json_block(parsed_items)
                product_list = json.loads(json_str) if json_str else []
            except Exception as e:
                print(f"❌ Failed to parse final output: {e}")
                product_list = []

                    
                print("\n🔖 Final Parsed Items:\n", product_list)

            # 🧠 Save episode for later
            episodes.append({
                'user_id': str(session_user_id),
                'query': f"{user_data['target_item']} - {user_data['item_details']}",
                'item_details': user_data['item_details'],
                'final_items': product_list,
                'timestamp': datetime.now().isoformat(),
                'description': f"Shopping episode for {user_data['target_item']}"
            })

            memory_manager.write_short('last_final_items', product_list)

            elapsed = (datetime.now() - start_time).total_seconds()
            print(f"\n✅ Completed in {elapsed:.1f}s\n")

        except Exception as e:
            print(f"\n❌ Error: {e}", file=sys.stderr)