# tool_name: wechat_e2e_high_resolution_client_state_capture_with_physics_sem
from langchain.tools import tool
import json
import os
import time
from typing import Dict, Any

@tool
def wechat_e2e_high_resolution_client_state_capture_with_physics_sem(input_args: str = "") -> Dict[str, Any]:
    """
    微信端到端高分辨率客户端状态捕获与物理语义双重验证的零错误传输保证体系
    
    这个工具将high_resolution_client_state_capture能力与physics_semantic_dual_verification
    进行紧密耦合，形成真正的零错误保证链路。
    
    Args:
        input_args (str): JSON字符串，包含以下参数:
            - capture_delay (int): 捕获延迟（秒），默认3秒
            - verification_params (dict): 物理语义验证参数
            - context (str): 上下文信息
            
    Returns:
        dict: 包含验证结果、状态信息和建议的字典
    """
    try:
        # 解析输入参数
        if input_args:
            try:
                params = json.loads(input_args)
            except json.JSONDecodeError:
                params = {}
        else:
            params = {}
        
        capture_delay = params.get('capture_delay', 3)
        verification_params = params.get('verification_params', {})
        context = params.get('context', "")
        
        # 延迟等待
        time.sleep(capture_delay)
        
        # 通过运行时注入API调用相关能力
        from openclaw_continuity.runtime import CapabilityRuntime
        runtime = CapabilityRuntime()
        
        # 调用高分辨率客户端状态捕获能力
        try:
            capture_result = runtime.invoke_capability(
                "high_resolution_client_state_capture",
                {"context": context}
            )
        except Exception as e:
            return {
                'success': False,
                'error': f"客户端状态捕获能力调用失败: {str(e)}",
                'capture_result': None,
                'verification_result': None,
                'zero_error_guarantee': False
            }
        
        # 检查捕获是否成功
        if not capture_result or 'error' in capture_result.get('result', {}):
            return {
                'success': False,
                'error': f"客户端状态捕获失败: {capture_result.get('result', {}).get('error', '未知错误')}",
                'capture_result': capture_result,
                'verification_result': None,
                'zero_error_guarantee': False
            }
        
        # 获取截图路径
        screenshot_path = capture_result['result'].get('screenshot_path')
        if not screenshot_path or not os.path.exists(screenshot_path):
            return {
                'success': False,
                'error': "截图文件不存在或路径无效",
                'capture_result': capture_result,
                'verification_result': None,
                'zero_error_guarantee': False
            }
        
        # 创建临时视频用于验证（将截图转换为单帧视频）
        temp_video_path = f"temp_verification_{int(time.time())}.mp4"
        
        try:
            # 使用ffmpeg将截图转换为视频
            import subprocess
            cmd = [
                'ffmpeg', '-y', '-loop', '1', '-i', screenshot_path,
                '-c:v', 'libx264', '-t', '1', '-pix_fmt', 'yuv420p', temp_video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                raise Exception(f"ffmpeg转换失败: {result.stderr}")
                
            if not os.path.exists(temp_video_path):
                raise Exception("无法创建临时验证视频")
            
            # 调用物理语义双重验证能力
            try:
                verify_input = {
                    'video_path': temp_video_path,
                    'verification_params': verification_params
                }
                verification_result = runtime.invoke_capability(
                    "physics_semantic_dual_verification",
                    verify_input
                )
            except Exception as e:
                raise Exception(f"物理语义验证能力调用失败: {str(e)}")
                
            # 清理临时文件
            try:
                os.remove(temp_video_path)
            except:
                pass
                
        except Exception as e:
            # 清理临时文件
            try:
                if os.path.exists(temp_video_path):
                    os.remove(temp_video_path)
            except:
                pass
            
            return {
                'success': False,
                'error': f"物理语义验证失败: {str(e)}",
                'capture_result': capture_result,
                'verification_result': {'error': str(e)},
                'zero_error_guarantee': False
            }
        
        # 综合判断零错误保证
        capture_success = capture_result.get('result', {}).get('wechat_running', False)
        verification_success = verification_result.get('result', {}).get('overall_valid', False)
        
        zero_error_guarantee = capture_success and verification_success
        
        # 构建最终结果
        final_result = {
            'success': True,
            'zero_error_guarantee': zero_error_guarantee,
            'capture_result': capture_result,
            'verification_result': verification_result,
            'timestamp': time.time(),
            'context': context
        }
        
        # 添加见解和事实
        insights = [
            f"微信端到端高分辨率客户端状态捕获完成: {'成功' if capture_success else '失败'}",
            f"物理语义双重验证完成: {'通过' if verification_success else '失败'}",
            f"零错误传输保证状态: {'已建立' if zero_error_guarantee else '未建立'}"
        ]
        
        facts = [
            ('wechat_e2e_capture', 'status', 'completed'),
            ('physics_semantic_verification', 'status', 'completed'),
            ('zero_error_guarantee', 'established', str(zero_error_guarantee)),
            ('capture_resolution', 'width', str(capture_result.get('result', {}).get('resolution', 'unknown'))),
            ('verification_timestamp', 'unix_time', str(time.time()))
        ]
        
        memories = [
            f"微信端到端高分辨率客户端状态捕获与物理语义双重验证集成完成，零错误保证状态: {zero_error_guarantee}",
            f"捕获分辨率: {capture_result.get('result', {}).get('resolution', 'unknown')}",
            f"验证参数: {json.dumps(verification_params)}"
        ]
        
        final_result['insights'] = insights
        final_result['facts'] = facts
        final_result['memories'] = memories
        
        return final_result
        
    except Exception as e:
        return {
            'success': False,
            'error': f"工具执行异常: {str(e)}",
            'capture_result': None,
            'verification_result': None,
            'zero_error_guarantee': False
        }