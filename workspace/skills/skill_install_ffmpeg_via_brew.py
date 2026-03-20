"""
自动生成的技能模块
需求: 执行brew install ffmpeg命令并验证安装结果
生成时间: 2026-03-19 14:56:05
"""

# skill_name: install_ffmpeg_via_brew
import subprocess
import os
import sys

def main(args=None):
    """
    执行brew install ffmpeg命令并验证安装结果
    """
    if args is None:
        args = {}
    
    # 检查是否已安装ffmpeg
    is_installed_before = False
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            is_installed_before = True
    except FileNotFoundError:
        is_installed_before = False
    except subprocess.TimeoutExpired:
        is_installed_before = False
    
    # 执行brew install ffmpeg命令
    install_result = {
        'command': 'brew install ffmpeg',
        'returncode': None,
        'stdout': '',
        'stderr': '',
        'success': False
    }
    
    if sys.platform == "darwin":  # macOS平台才执行brew
        try:
            result = subprocess.run(['brew', 'install', 'ffmpeg'], 
                                  capture_output=True, text=True, timeout=300)  # 5分钟超时
            install_result['returncode'] = result.returncode
            install_result['stdout'] = result.stdout
            install_result['stderr'] = result.stderr
            install_result['success'] = (result.returncode == 0)
        except subprocess.TimeoutExpired:
            install_result['success'] = False
            install_result['error'] = '命令执行超时'
        except FileNotFoundError:
            install_result['success'] = False
            install_result['error'] = 'brew命令未找到'
    else:
        install_result['success'] = False
        install_result['error'] = '非macOS系统，不支持brew命令'
    
    # 验证安装结果
    verification_result = {
        'command': 'ffmpeg -version',
        'returncode': None,
        'stdout': '',
        'stderr': '',
        'success': False,
        'version': None
    }
    
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=10)
        verification_result['returncode'] = result.returncode
        verification_result['stdout'] = result.stdout
        verification_result['stderr'] = result.stderr
        verification_result['success'] = (result.returncode == 0)
        
        if result.returncode == 0:
            # 提取版本信息
            lines = result.stdout.split('\n')
            for line in lines:
                if 'ffmpeg version' in line:
                    version_info = line.strip()
                    verification_result['version'] = version_info
                    break
    except FileNotFoundError:
        verification_result['success'] = False
        verification_result['error'] = 'ffmpeg命令未找到，安装可能失败'
    except subprocess.TimeoutExpired:
        verification_result['success'] = False
        verification_result['error'] = '版本检查命令超时'
    
    # 检查是否确实安装了新版本（如果之前未安装）
    was_new_install = False
    if not is_installed_before and verification_result['success']:
        was_new_install = True
    
    # 构建结果
    result_summary = {
        'was_already_installed': is_installed_before,
        'was_newly_installed': was_new_install,
        'install_attempt': install_result,
        'verification_result': verification_result,
        'overall_success': verification_result['success']
    }
    
    insights = []
    if is_installed_before:
        insights.append('ffmpeg在执行前已经安装')
    else:
        insights.append('ffmpeg在执行前未安装')
    
    if was_new_install:
        insights.append('成功新安装了ffmpeg')
    
    if verification_result['success']:
        if verification_result['version']:
            insights.append(f'ffmpeg安装验证成功，版本信息：{verification_result["version"]}')
        else:
            insights.append('ffmpeg安装验证成功，但未能提取版本信息')
    else:
        insights.append('ffmpeg安装验证失败')
    
    return {
        'result': result_summary,
        'insights': insights,
        'capabilities': ['audio_video_processing'] if verification_result['success'] else []
    }