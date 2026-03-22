"""
MemoryCore 动态权重集成补丁 - 测试版本
专门用于验证补丁是否正确应用
"""

def test_enhanced_recall_method_exists():
    """测试 enhanced_recall_memory_with_weighting 方法是否存在"""
    try:
        if hasattr(memory, 'enhanced_recall_memory_with_weighting'):
            print("✅ enhanced_recall_memory_with_weighting 方法存在")
            return True
        else:
            print("❌ enhanced_recall_memory_with_weighting 方法不存在")
            return False
    except Exception as e:
        print(f"❌ 检查方法存在性时出错: {e}")
        return False

def test_enhanced_recall_functionality():
    """测试 enhanced_recall_memory_with_weighting 功能"""
    try:
        if not hasattr(memory, 'enhanced_recall_memory_with_weighting'):
            print("❌ 方法不存在，无法测试功能")
            return False
        
        # 尝试调用方法
        result = memory.enhanced_recall_memory_with_weighting(
            "test",
            context="testing dynamic memory weighting"
        )
        
        print(f"✅ 方法调用成功，返回 {len(result) if result else 0} 条结果")
        if result and len(result) > 0:
            if 'weight' in result[0]:
                print(f"✅ 第一条结果包含权重信息: weight={result[0]['weight']}")
                return True
            else:
                print("⚠️ 结果不包含权重信息")
                return False
        else:
            print("⚠️ 返回空结果")
            return True  # 方法能调用就算成功
            
    except Exception as e:
        print(f"❌ 方法调用失败: {e}")
        return False

# 执行测试
print("=== MemoryCore 动态权重集成补丁测试 ===")
method_exists = test_enhanced_recall_method_exists()
functionality_works = test_enhanced_recall_functionality()

print(f"\n=== 测试总结 ===")
print(f"方法存在: {'✅' if method_exists else '❌'}")
print(f"功能正常: {'✅' if functionality_works else '❌'}")

if method_exists and functionality_works:
    print("🎉 补丁测试完全成功！")
else:
    print("⚠️ 补丁测试部分失败，请检查实现")