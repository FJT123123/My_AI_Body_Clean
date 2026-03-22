def fix_universal_validator_output_redirection_check():
    """修复debug_info_integrity_validator中的output_redirection检查逻辑"""
    try:
        import sys
        import os
        
        # 绝对路径寻址逻辑
        workspace_dir = "/Users/zhufeng/My_AI_Body_Clean/workspace"
        
        if workspace_dir not in sys.path:
            sys.path.insert(0, workspace_dir)
        
        # 定义验证器文件的绝对路径
        validator_path = os.path.join(workspace_dir, "tools", "tool_debug_info_integrity_validator.py")
        
        if not os.path.exists(validator_path):
             print(f"⚠️  尝试从备选路径加载验证器...")
             # 尝试从 globals().get('WORKSPACE_DIR') 获取 (来自 openclaw_continuity.py)
             alt_ws = globals().get('WORKSPACE_DIR')
             if alt_ws:
                 validator_path = os.path.join(alt_ws, "tools", "tool_debug_info_integrity_validator.py")
        
        if not os.path.exists(validator_path):
             print(f"❌ 关键错误: 无法找到验证器文件: {validator_path}")
             return False

        with open(validator_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修复检查逻辑
        old_logic = '''            if prevention_result.get('result', {}).get('prevention_applied', False):
                results['insights'].append("UNIVERSAL DEBUG INFO INTEGRITY GUARANTEE: 成功应用输出重定向防护，防止信息逃逸")
            else:
                results['success'] = False
                results['insights'].append("UNIVERSAL DEBUG INFO INTEGRITY GUARANTEE: 输出重定向防护失败，存在信息逃逸风险")'''
        
        new_logic = '''            compensation_applied = prevention_result.get('result', {}).get('compensation_applied', False)
            success = prevention_result.get('result', {}).get('success', False)
            if success and (compensation_applied or prevention_result.get('result', {}).get('weight_before', 1.0) >= minimum_weight_threshold):
                results['insights'].append("UNIVERSAL DEBUG INFO INTEGRITY GUARANTEE: 成功应用输出重定向防护，防止信息逃逸")
            else:
                results['success'] = False
                results['insights'].append("UNIVERSAL DEBUG INFO INTEGRITY GUARANTEE: 输出重定向防护失败，存在信息逃逸风险")'''
        
        if old_logic in content:
            new_content = content.replace(old_logic, new_logic)
            with open(os.path.join(workspace_dir, 'tools', 'tool_debug_info_integrity_validator.py'), 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("Universal validator output redirection check fixed!")
            return True
        else:
            print("Old logic not found, patch may already be applied")
            return False
            
    except Exception as e:
        print(f"Failed to fix universal validator: {e}")
        return False

# 应用修复
fix_universal_validator_output_redirection_check()