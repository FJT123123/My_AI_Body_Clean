# tool_name: video_frame_physics_compliance_end_to_end_regression_validation

from langchain.tools import tool
import os
import json
import tempfile
from pathlib import Path


@tool
def video_frame_physics_compliance_end_to_end_regression_validation(video_path=None, output_dir="./regression_validation", test_patterns=None):
    """
    端到端视频物理一致性回归验证工具
    
    该工具执行完整的回归验证流程：
    1. 如果未提供video_path，则生成包含已知物理运动模式的测试视频
    2. 对视频应用自我修复流程
    3. 验证修复前后的视频是否保持了相同的物理约束和运动语义
    4. 返回详细的验证报告
    
    Args:
        video_path (str, optional): 输入视频文件路径。如果未提供，将生成测试视频。
        output_dir (str): 输出分析结果的目录
        test_patterns (list, optional): 测试模式列表，如['uniform_motion', 'accelerated_motion', 'rotation']
    
    Returns:
        dict: 包含完整回归验证结果的字典
    """
    import os
    import json
    import tempfile
    from pathlib import Path

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 步骤1: 获取或生成测试视频
    if video_path and os.path.exists(video_path):
        original_video_path = video_path
        is_generated = False
    else:
        # 生成测试视频 - 使用现有工具
        try:
            # 调用高帧率测试视频生成工具
            temp_dir = tempfile.gettempdir()
            test_video_path = os.path.join(temp_dir, "physics_test_video.mp4")
            
            # 生成简单的测试视频
            from workspace.tools.tool_create_high_framerate_test_video import create_high_framerate_test_video
            generate_params = json.dumps({
                'framerate': 30,
                'resolution': '1280x720',
                'duration': 5,
                'output_path': test_video_path
            })
            generate_result = create_high_framerate_test_video(generate_params)
            
            if 'error' in str(generate_result):
                # 如果高帧率视频生成失败，尝试4K压力测试视频
                from workspace.tools.tool_create_4k_stress_test_video import create_4k_stress_test_video
                generate_result = create_4k_stress_test_video("")
                if 'video_path' in generate_result:
                    test_video_path = generate_result['video_path']
                else:
                    raise Exception("无法生成测试视频")
            else:
                test_video_path = generate_result.get('video_path', test_video_path)
            
            original_video_path = test_video_path
            is_generated = True
        except Exception as e:
            return {
                'success': False,
                'error': f"无法生成测试视频: {str(e)}",
                'step': 'video_generation'
            }

    # 步骤2: 验证原始视频的物理约束
    try:
        # 直接调用全局工具函数
        original_validation_result = video_frame_motion_semantic_validator(
            video_path=original_video_path,
            output_dir=os.path.join(output_dir, "original_validation")
        )
        
        # 检查验证结果结构
        if isinstance(original_validation_result, dict):
            if 'result' in original_validation_result:
                result_data = original_validation_result['result']
                if isinstance(result_data, dict) and 'overall_valid' in result_data:
                    original_valid = result_data['overall_valid']
                else:
                    original_valid = False
            else:
                original_valid = False
        else:
            original_valid = False
            
    except Exception as e:
        return {
            'success': False,
            'error': f"原始视频验证失败: {str(e)}",
            'step': 'original_validation'
        }

    # 步骤3: 应用自我修复流程
    try:
        # 使用视频处理自动修复和验证工作流
        repair_input = json.dumps({
            'error_info': 'General physics compliance validation',
            'video_path': original_video_path,
            'output_dir': os.path.join(output_dir, "repair_output")
        })
        
        repair_result = video_processing_automatic_repair_and_validation_workflow(repair_input)
        
        # 检查修复结果，获取修复后的视频路径
        repaired_video_path = original_video_path  # 默认使用原始视频
        
        # 如果修复成功且有新的视频路径，使用修复后的视频
        if isinstance(repair_result, dict):
            if 'final_video_path' in repair_result:
                repaired_video_path = repair_result['final_video_path']
            elif 'repaired_video_path' in repair_result:
                repaired_video_path = repair_result['repaired_video_path']
            elif repair_result.get('workflow_status') == 'success':
                # 修复成功但没有新路径，可能原地修复
                repaired_video_path = original_video_path
    except Exception as e:
        return {
            'success': False,
            'error': f"修复过程失败: {str(e)}",
            'step': 'repair_process'
        }

    # 步骤4: 验证修复后视频的物理约束
    try:
        # 直接调用全局工具函数
        repaired_validation_result = video_frame_motion_semantic_validator(
            video_path=repaired_video_path,
            output_dir=os.path.join(output_dir, "repaired_validation")
        )
        
        # 检查验证结果结构
        if isinstance(repaired_validation_result, dict):
            if 'result' in repaired_validation_result:
                result_data = repaired_validation_result['result']
                if isinstance(result_data, dict) and 'overall_valid' in result_data:
                    repaired_valid = result_data['overall_valid']
                else:
                    repaired_valid = False
            else:
                repaired_valid = False
        else:
            repaired_valid = False
            
    except Exception as e:
        return {
            'success': False,
            'error': f"修复后视频验证失败: {str(e)}",
            'step': 'repaired_validation'
        }

    # 步骤5: 比较验证结果
    regression_passed = original_valid == repaired_valid
    
    # 如果原始视频无效但修复后有效，也算通过
    if not original_valid and repaired_valid:
        regression_passed = True

    # 构建详细报告
    report = {
        'success': True,
        'regression_passed': regression_passed,
        'original_video': {
            'path': original_video_path,
            'is_generated': is_generated,
            'validation_result': original_validation_result.get('result', {}) if isinstance(original_validation_result, dict) else {}
        },
        'repaired_video': {
            'path': repaired_video_path,
            'same_as_original': repaired_video_path == original_video_path,
            'validation_result': repaired_validation_result.get('result', {}) if isinstance(repaired_validation_result, dict) else {}
        },
        'comparison': {
            'original_valid': original_valid,
            'repaired_valid': repaired_valid,
            'physical_constraints_preserved': regression_passed,
            'motion_consistency_preserved': (
                original_validation_result.get('result', {}).get('motion_consistency') ==
                repaired_validation_result.get('result', {}).get('motion_consistency')
            ) if isinstance(original_validation_result, dict) and isinstance(repaired_validation_result, dict) else False,
            'semantic_consistency_preserved': (
                original_validation_result.get('result', {}).get('semantic_consistency') ==
                repaired_validation_result.get('result', {}).get('semantic_consistency')
            ) if isinstance(original_validation_result, dict) and isinstance(repaired_validation_result, dict) else False
        },
        'output_directory': output_dir
    }

    # 保存报告到文件
    report_path = os.path.join(output_dir, "regression_validation_report.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    return report