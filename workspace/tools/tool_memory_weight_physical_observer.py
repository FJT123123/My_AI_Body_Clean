# tool_name: memory_weight_physical_observer

from langchain.tools import tool
import json
import os
import time
import psutil
import tempfile
from pathlib import Path

@tool
def memory_weight_physical_observer(input_params):
    """
    记忆权重物理观测器：在真实存取路径中观测权重算法的物理效应
    
    Args:
        input_params (str): JSON字符串，包含以下字段：
            - test_data_size: 测试数据大小（KB）
            - observation_metrics: 观测指标列表
            
    Returns:
        dict: 观测结果，包含真实的物理效应数据
    """
    try:
        # 解析输入参数
        if isinstance(input_params, str):
            config = json.loads(input_params)
        else:
            config = input_params
            
        test_data_size = config.get('test_data_size', 1024)  # KB
        observation_metrics = config.get('observation_metrics', ['latency', 'memory_usage'])
        
        # 创建临时目录用于真实文件操作
        with tempfile.TemporaryDirectory() as temp_dir:
            obs_path = Path(temp_dir) / "memory_observation.dat"
            
            # 获取初始系统状态
            initial_memory = psutil.virtual_memory().used
            start_time = time.time()
            
            # 执行真实的文件写入操作（物理存储）
            data_bytes = test_data_size * 1024
            with open(obs_path, 'wb') as f:
                f.write(os.urandom(data_bytes))
                
            write_time = time.time()
            
            # 执行真实的文件读取操作
            with open(obs_path, 'rb') as f:
                _ = f.read()
                
            read_time = time.time()
            
            # 获取最终系统状态
            final_memory = psutil.virtual_memory().used
            
            # 计算真实物理效应
            write_duration = write_time - start_time
            read_duration = read_time - write_time
            memory_delta = final_memory - initial_memory
            
            # 构建观测结果
            observation_result = {
                'physical_effects': {
                    'write_operation': {
                        'duration_ms': write_duration * 1000,
                        'data_size_kb': test_data_size,
                        'throughput_mbps': (test_data_size * 8) / (write_duration * 1000) if write_duration > 0 else 0
                    },
                    'read_operation': {
                        'duration_ms': read_duration * 1000,
                        'data_size_kb': test_data_size,
                        'throughput_mbps': (test_data_size * 8) / (read_duration * 1000) if read_duration > 0 else 0
                    }
                },
                'system_metrics': {
                    'memory_usage_delta_bytes': memory_delta,
                    'total_observation_time_ms': (read_time - start_time) * 1000
                },
                'physical_observability_score': min(1.0, (write_duration + read_duration) / 0.1) if (write_duration + read_duration) > 0 else 0.0
            }
            
            return observation_result
        
    except Exception as e:
        return {
            'error': f'观测过程中发生错误: {str(e)}',
            'physical_effects': {},
            'system_metrics': {},
            'physical_observability_score': 0.0
        }