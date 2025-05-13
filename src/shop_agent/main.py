#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from shop_agent.crew import ShopAgent

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# It will loop until the user types 'exit' at the product category prompt.

def get_user_input():
    """Get structured input from user with enhanced prompts"""
    product = input("Product category (e.g., wireless earbuds) or type 'exit' to quit: ").strip()
    if product.lower() == 'exit':
        return None
    details = input("Describe your needs (color, budget, must-have features): ").strip()
    return {'target_item': product, 'item_details': details}


def run():
    """
    Run the crew in a loop until user exits.
    """
    while True:
        try:
            user_data = get_user_input()
            if user_data is None:
                print("\n👋 Exiting Smart Shopping Assistant. Goodbye!")
                break

            start_time = datetime.now()
            print(f"\n🔍 Analyzing requirements for {user_data['target_item']}:")
            print(f"   - Specifications: {user_data['item_details']}")
            print("   - Searching...\n")

            ShopAgent().crew().kickoff(inputs={
                'target_item': user_data['target_item'],
                'item_details': user_data['item_details']
            })

            elapsed = (datetime.now() - start_time).total_seconds()
            print(f"\n✅ Completed in {elapsed:.1f}s\n")

        except Exception as e:
            print(f"\n❌ Error: {e}", file=sys.stderr)
            # Continue loop on error


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


if __name__ == "__main__":
    run()
