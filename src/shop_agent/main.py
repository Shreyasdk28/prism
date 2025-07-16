#!/usr/bin/env python
import sys, os, warnings, uuid, json
from datetime import datetime
from shop_agent.crew import ShopAgent
from shop_agent.memory import memory_manager
from shop_agent.tools.custom_tool import QdrantCustomUpsertTool 
from shop_agent.memory import memory_manager

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def parse_user_details(details: str):
    """Parse user details into structured preferences"""
    parts = [part.strip() for part in details.split(',')]
    preferences = {}
    
    for part in parts:
        part_lower = part.lower().strip()
        original_part = part.strip()
        
        # Extract budget (look for numbers)
        if any(char.isdigit() for char in part_lower):
            # Extract all numbers from the string
            import re
            numbers = re.findall(r'\d+', part_lower)
            if numbers:
                # Take the largest number as budget (assuming it's the price)
                budget = max([int(num) for num in numbers])
                preferences['budget'] = budget
                print(f"DEBUG: Found budget: {budget} from '{original_part}'")
        
        # Common colors
        colors = ['black', 'white', 'red', 'blue', 'green', 'pink', 'grey', 'gray', 'silver', 'gold', 'brown', 'yellow', 'purple', 'orange']
        for color in colors:
            if color in part_lower:
                preferences['color'] = color
                print(f"DEBUG: Found color: {color} from '{original_part}'")
                break
        
        # Features
        if 'noise' in part_lower and 'cancel' in part_lower:
            if 'features' not in preferences:
                preferences['features'] = []
            preferences['features'].append('noise_cancellation')
            print(f"DEBUG: Found feature: noise_cancellation from '{original_part}'")
        elif 'wireless' in part_lower or 'bluetooth' in part_lower:
            if 'features' not in preferences:
                preferences['features'] = []
            preferences['features'].append('wireless')
            print(f"DEBUG: Found feature: wireless from '{original_part}'")
        elif 'waterproof' in part_lower or 'water resistant' in part_lower:
            if 'features' not in preferences:
                preferences['features'] = []
            preferences['features'].append('waterproof')
            print(f"DEBUG: Found feature: waterproof from '{original_part}'")
        elif len(part_lower) > 2 and not any(char.isdigit() for char in part_lower) and not any(color in part_lower for color in colors):
            # General feature if it's not a color or number
            if 'features' not in preferences:
                preferences['features'] = []
            preferences['features'].append(original_part)
            print(f"DEBUG: Found general feature: {original_part}")
    
    # Add the raw input for reference
    preferences['raw_input'] = details
    
    return preferences

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
                # print("🧠 Uploading session memory to Qdrant...\n")
                # for episode in episodes:
                #     result = qdrant_tool._run(**episode)
                #     print(f"🟢 Upsert status: {result}")

                # print(f"✅ Uploaded {len(episodes)} episodes.\n")
                break
            
            start_time = datetime.now()

            parsed_preferences = parse_user_details(user_data['item_details'])
            print(f"📝 Parsed user preferences: {parsed_preferences}")

            long_term_prefs = memory_manager.get_user_preferences(user_data['target_item'])
            short_term = memory_manager.short_term

            print(f"\n🔍 Searching for {user_data['target_item']} with specs: {user_data['item_details']}")
            print(f"   • Injected long-term prefs: {long_term_prefs}")
            print(f"   • Last final_items in short-term: {bool(short_term.get('last_final_items'))}\n")

            # print("🚀 Starting shopping assistant pipeline...\n")
            raw_output = ShopAgent().crew().kickoff(inputs={
                'user_id': str(session_user_id),
                'target_item': user_data['target_item'],
                'item_details': user_data['item_details'],
                'user_preferences': parsed_preferences,
                'short_term': short_term,
                'long_term_preferences': long_term_prefs or {},
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
            final_items = getattr(raw_output, 'result', None) or str(raw_output)
            print("\n🔖 Final Recommendations:\n")
            print(final_items)
            
            episode_data={
                'user_id': str(session_user_id),
                'query': f"{user_data['target_item']}",
                'item_details': user_data['item_details'],
                'final_items': product_list,
                'timestamp': datetime.now().isoformat(),
                'description': f"Shopping episode for {user_data['target_item']}"
            }

            episodes.append(episode_data)

             # 📡 Upload to Qdrant after each episode
            result = qdrant_tool._run(**episode_data)
            print(f"🟢 Episodic memory uploaded for: {user_data['target_item']}")


            # Update long-term preferences
            if long_term_prefs:
                # Merge with existing preferences
                merged_prefs = {**long_term_prefs, **parsed_preferences}
                
                # Handle features separately to avoid duplicates
                if 'features' in long_term_prefs and 'features' in parsed_preferences:
                    existing_features = long_term_prefs.get('features', [])
                    new_features = parsed_preferences.get('features', [])
                    # Combine and remove duplicates
                    merged_features = list(set(existing_features + new_features))
                    merged_prefs['features'] = merged_features
            else:
                merged_prefs = parsed_preferences

            save_success = memory_manager.save_user_preferences(user_data['target_item'], merged_prefs)

            if save_success:
                print("✅ Preferences successfully saved to database!")
                
                # Verify save by reading back
                verification = memory_manager.get_user_preferences(user_data['target_item'])
                print(f"🔍 Verification - Retrieved preferences: {verification}")
            else:
                print("❌ Failed to save preferences to database")

            memory_manager.write_short('last_final_items', product_list)

            elapsed = (datetime.now() - start_time).total_seconds()
            print(f"\n✅ Completed in {elapsed:.1f}s\n")

        except Exception as e:
            print(f"\n❌ Error: {e}", file=sys.stderr)