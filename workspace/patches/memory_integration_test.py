# Simple test for memory integration
print("=== Testing memory_core_dynamic_weighting_integration ===")

# Check if the method exists
method_exists = hasattr(memory, 'enhanced_recall_memory_with_weighting')
print(f"Method exists: {method_exists}")

if method_exists:
    try:
        # Try to call the method
        result = memory.enhanced_recall_memory_with_weighting("test", context="test context")
        print(f"Method call successful. Result type: {type(result)}")
        print(f"Result length: {len(result) if result else 0}")
        if result and len(result) > 0:
            print(f"First result keys: {list(result[0].keys())}")
            if 'weight' in result[0]:
                print(f"Weight found: {result[0]['weight']}")
                print("✅ SUCCESS: Integration is working!")
            else:
                print("⚠️ No weight in result")
        else:
            print("✅ Method callable (empty result is OK)")
    except Exception as e:
        print(f"❌ Method call failed: {e}")
        import traceback
        traceback.print_exc()
else:
    print("❌ Method does not exist - integration failed")

print("=== Test completed ===")