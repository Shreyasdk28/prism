#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from shop_agent.crew import ShopAgent

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information
def get_user_input():
    """Get structured input from user with enhanced prompts"""
    if len(sys.argv) > 2:
        return {
            'target_item': sys.argv[1],
            'item_details': ' '.join(sys.argv[2:])
        }
    
    print("\n🛍️  Smart Shopping Assistant")
    print("--------------------------")
    return {
        'target_item': input("Product category (e.g., wireless earbuds): ").strip(),
        'item_details': input("Describe your needs (color, budget, must-have features): ").strip()
    }

def run():
    """
    Run the crew.
    """
    try:
        start_time = datetime.now()
        user_data = get_user_input()
        # validate_input(user_data)
        
        print(f"\n🔍 Analyzing requirements for {user_data['target_item']}:")
        print(f"   - Specifications: {user_data['item_details']}")
        print("   - Searching Amazon & Flipkart...\n")
        
        # Run the crew with formatted inputs
        ShopAgent().crew().kickoff(inputs={
            'target_item': user_data['target_item'],
            'item_details': user_data['item_details']
        })
        
        print(f"\n✅ Completed in {(datetime.now() - start_time).total_seconds():.1f}s")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        ShopAgent().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        ShopAgent().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }
    try:
        ShopAgent().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")
