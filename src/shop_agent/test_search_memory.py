# test_negative_search_memory.py

from shop_agent.tools.vector_tools import ShoppingMemorySearchTool

search_tool = ShoppingMemorySearchTool()

print("\n=== ❌ Negative Test Cases ===\n")

# Case 1: Wrong user_id (doesn't exist)
print("\n[TEST 1] Wrong user_id:")
result_1 = search_tool._run(query="cheap earbuds", user_id="nonexistent_user_999")
print(result_1)

# Case 2: Completely irrelevant query
print("\n[TEST 2] Irrelevant query:")
result_2 = search_tool._run(query="medieval sword armor horses", user_id="cloud_test_user_01")
print(result_2)

# Case 3: Empty query string
print("\n[TEST 3] Empty query:")
result_3 = search_tool._run(query="", user_id="cloud_test_user_01")
print(result_3)

# Case 4: No user_id provided
print("\n[TEST 4] No user_id (global search fallback):")
result_4 = search_tool._run(query="wireless earbuds")
print(result_4)

# Case 5: Invalid input types
print("\n[TEST 5] Non-string input:")
try:
    result_5 = search_tool._run(query=12345, user_id=["not", "a", "string"])
    print(result_5)
except Exception as e:
    print(f"Caught error: {e}")
