# capability_name: path_resolution_capability

import os
import json
from pathlib import Path
from typing import Dict, Optional, Union


def run_path_resolution_cycle(
    target_path: str,
    path_type: str = "tool",
    base_dir: Optional[str] = None,
    create_missing: bool = False
) -> Dict:
    """
    统一路径解析能力，确保所有文件操作都使用正确的ROOT_DIR路径
    
    Args:
        target_path: 目标路径，可以是相对路径或完整路径
        path_type: 路径类型 ("tool", "workspace", "memory", "config", "log", "data")
        base_dir: 基础目录，默认使用ROOT_DIR
        create_missing: 是否创建缺失的目录
    
    Returns:
        Dict: 包含解析结果的结构化字典
    """
    try:
        # 确定基础目录
        # 确定基础目录
        if base_dir is None:
            # 预定义：如果是我们的项目，通常在 My_AI_Body_Clean 或 My_AI_Body
            # 尝试从环境变量获取 ROOT_DIR，或者从当前文件向上推导
            root_dir = os.environ.get("ROOT_DIR")
            if not root_dir:
                # 尝试通过此文件的位置推导 ROOT_DIR（即 workspace 的上一级）
                try:
                    root_dir = str(Path(__file__).resolve().parent.parent.parent)
                except:
                    root_dir = os.getcwd()
        else:
            root_dir = base_dir
        
        # 确保基础目录存在
        root_path = Path(root_dir)
        if not root_path.exists():
            return {
                "success": False,
                "error": f"基础目录不存在: {root_dir}",
                "resolved_path": None,
                "base_dir": root_dir,
                "target_path": target_path,
                "path_type": path_type
            }
        
        # 根据路径类型确定相对于 ROOT_DIR 的子目录
        # 注意：在 Phoenix 架构中，这些目录都在 workspace/ 下
        path_mapping = {
            "tool": "workspace/tools",
            "workspace": "workspace",
            "memory": "workspace/memory",
            "config": "workspace/config",
            "log": "workspace/logs",
            "data": "workspace/data",
            "capability": "workspace/capabilities",
            "patch": "workspace/patches",
            "daemon": "workspace/daemons"
        }
        
        if path_type not in path_mapping:
            return {
                "success": False,
                "error": f"不支持的路径类型: {path_type}",
                "resolved_path": None,
                "base_dir": root_dir,
                "target_path": target_path,
                "path_type": path_type
            }
        
        # 构建完整路径
        sub_dir = path_mapping[path_type]
        # 如果 target_path 已经包含了 sub_dir 前缀，则不再重复拼接
        clean_target = target_path.lstrip('./\\')
        if clean_target.startswith(sub_dir + "/"):
            full_path = root_path / clean_target
        else:
            full_path = root_path / sub_dir / clean_target
        
        # 规范化路径
        resolved_path = full_path.resolve()
        
        # 创建缺失的目录（如果需要）
        if create_missing:
            try:
                resolved_path.parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                return {
                    "success": False,
                    "error": f"创建目录失败: {str(e)}",
                    "resolved_path": str(resolved_path),
                    "base_dir": root_dir,
                    "target_path": target_path,
                    "path_type": path_type
                }
        
        # 验证路径是否在基础目录下（防止路径遍历）
        try:
            resolved_path.relative_to(root_path)
        except ValueError:
            return {
                "success": False,
                "error": "目标路径不在基础目录范围内，可能存在路径遍历风险",
                "resolved_path": str(resolved_path),
                "base_dir": root_dir,
                "target_path": target_path,
                "path_type": path_type
            }
        
        return {
            "success": True,
            "error": None,
            "resolved_path": str(resolved_path),
            "base_dir": str(root_path),
            "target_path": target_path,
            "path_type": path_type,
            "exists": resolved_path.exists(),
            "is_file": resolved_path.is_file(),
            "is_dir": resolved_path.is_dir()
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"路径解析过程中发生异常: {str(e)}",
            "resolved_path": None,
            "base_dir": base_dir,
            "target_path": target_path,
            "path_type": path_type
        }


def get_tool_path(
    tool_name: str,
    base_dir: Optional[str] = None,
    create_missing: bool = False
) -> Dict:
    """
    获取工具路径的专用函数
    
    Args:
        tool_name: 工具名称
        base_dir: 基础目录
        create_missing: 是否创建缺失的目录
    
    Returns:
        Dict: 包含解析结果的结构化字典
    """
    return run_path_resolution_cycle(
        target_path=tool_name,
        path_type="tool",
        base_dir=base_dir,
        create_missing=create_missing
    )


def get_workspace_path(
    workspace_path: str,
    base_dir: Optional[str] = None,
    create_missing: bool = False
) -> Dict:
    """
    获取工作空间路径的专用函数
    
    Args:
        workspace_path: 工作空间路径
        base_dir: 基础目录
        create_missing: 是否创建缺失的目录
    
    Returns:
        Dict: 包含解析结果的结构化字典
    """
    return run_path_resolution_cycle(
        target_path=workspace_path,
        path_type="workspace",
        base_dir=base_dir,
        create_missing=create_missing
    )


def get_capability_path(
    capability_name: str,
    base_dir: Optional[str] = None,
    create_missing: bool = False
) -> Dict:
    """
    获取能力模块路径的专用函数
    
    Args:
        capability_name: 能力模块名称
        base_dir: 基础目录
        create_missing: 是否创建缺失的目录
    
    Returns:
        Dict: 包含解析结果的结构化字典
    """
    return run_path_resolution_cycle(
        target_path=capability_name,
        path_type="capability",
        base_dir=base_dir,
        create_missing=create_missing
    )


def check_path_safety(
    path_to_check: str,
    base_dir: Optional[str] = None
) -> Dict:
    """
    检查路径安全性，验证路径是否在允许的范围内
    
    Args:
        path_to_check: 要检查的路径
        base_dir: 基础目录
    
    Returns:
        Dict: 包含安全检查结果的结构化字典
    """
    try:
        if base_dir is None:
            base_dir = os.environ.get("ROOT_DIR", os.getcwd())
        
        base_path = Path(base_dir)
        check_path = Path(path_to_check).resolve()
        
        # 检查目标路径是否在基础目录下
        try:
            check_path.relative_to(base_path)
            is_safe = True
            reason = "路径在允许范围内"
        except ValueError:
            is_safe = False
            reason = "路径超出允许范围，可能存在路径遍历风险"
        
        return {
            "success": True,
            "is_safe": is_safe,
            "reason": reason,
            "base_dir": str(base_path),
            "checked_path": str(check_path),
            "error": None
        }
    
    except Exception as e:
        return {
            "success": False,
            "is_safe": False,
            "reason": "路径检查过程中发生异常",
            "base_dir": base_dir,
            "checked_path": path_to_check,
            "error": str(e)
        }