def fix_universal_validator_output_redirection_check():
    """修复debug_info_integrity_validator中的output_redirection检查逻辑"""
    try:
        import sys
        import os
        
        # 确保 workspace 目录在 Python 路径中
        current_dir = os.path.dirname(__file__)
        workspace_dir = os.path.join(current_dir, '..')
        if workspace_dir not in sys.path:
            sys.path.insert(0, workspace_dir)
        
        # 读取现有的debug_info_integrity_validator文件
        with open(os.path.join(workspace_dir, 'tools', 'tool_debug_info_integrity_validator.py'), 'r', encoding='utf-8') as f:
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