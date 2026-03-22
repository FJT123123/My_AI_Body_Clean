# tool_name: tool_output_stream_diagnostic

import json
import os
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from langchain.tools import tool

@tool
def tool_output_stream_diagnostic(input_args: str = "") -> Dict[str, Any]:
    """
    Tool output stream integrity diagnostic framework for capturing, tracing, and validating tool interaction data flows.
    
    Args:
        input_args (str): JSON string containing parameters:
            - action: The action to perform ('capture_stream', 'validate_integrity', 'trace_flow', 'generate_report')
            - tool_name: Name of the tool being monitored
            - input_data: Input data to the tool
            - output_data: Output data from the tool
            - trace_id: Unique identifier for the trace
            - context: Additional context information
    
    Returns:
        Dict[str, Any]: Result dictionary with integrity diagnostics
    """
    try:
        # Parse input arguments
        if input_args:
            if isinstance(input_args, str):
                params = json.loads(input_args)
            else:
                params = input_args
        else:
            params = {}
        
        action = params.get('action', 'capture_stream')
        tool_name = params.get('tool_name', '')
        input_data = params.get('input_data', None)
        output_data = params.get('output_data', None)
        trace_id = params.get('trace_id', f"trace_{int(time.time() * 1000)}")
        context = params.get('context', {})
        
        # Validate required parameters based on action
        if action == 'capture_stream' and not tool_name:
            return {
                'result': {'error': '缺少 tool_name 参数'},
                'insights': ['参数校验失败：必须提供tool_name'],
                'facts': [],
                'memories': []
            }
            
        if action in ['validate_integrity', 'trace_flow'] and not trace_id:
            return {
                'result': {'error': '缺少 trace_id 参数'},
                'insights': ['参数校验失败：必须提供trace_id'],
                'facts': [],
                'memories': []
            }
        
        # Initialize result structure
        result = {
            'trace_id': trace_id,
            'timestamp': datetime.now().isoformat(),
            'tool_name': tool_name,
            'action': action,
            'status': 'success',
            'diagnostics': {}
        }
        
        # Create diagnostics directory if it doesn't exist
        diagnostics_dir = os.path.join(os.path.dirname(__file__), '..', 'tool_diagnostics')
        os.makedirs(diagnostics_dir, exist_ok=True)
        
        # Perform the requested action
        if action == 'capture_stream':
            result['diagnostics'] = _capture_tool_stream(tool_name, input_data, output_data, trace_id, context, diagnostics_dir)
        elif action == 'validate_integrity':
            result['diagnostics'] = _validate_stream_integrity(trace_id, diagnostics_dir)
        elif action == 'trace_flow':
            result['diagnostics'] = _trace_data_flow(trace_id, diagnostics_dir)
        elif action == 'generate_report':
            result['diagnostics'] = _generate_integrity_report(diagnostics_dir)
        else:
            result['status'] = 'error'
            result['error'] = f'未知的操作类型: {action}'
        
        # Store the trace information
        _store_trace_info(result, diagnostics_dir)
        
        return {
            'result': result,
            'insights': [f"成功执行工具输出流完整性诊断操作: {action}"],
            'facts': [f"工具交互数据流已记录，追踪ID: {trace_id}"],
            'memories': [f"工具输出流完整性诊断框架已成功应用于{tool_name}"]
        }
        
    except Exception as e:
        return {
            'result': {'error': f'工具输出流完整性诊断框架执行失败: {str(e)}'},
            'insights': ['执行过程中发生异常，请检查输入参数格式'],
            'facts': [],
            'memories': []
        }

def _capture_tool_stream(tool_name: str, input_data: Any, output_data: Any, trace_id: str, context: Dict, diagnostics_dir: str) -> Dict[str, Any]:
    """Capture a tool interaction stream"""
    # Calculate data fingerprints
    input_fingerprint = _calculate_fingerprint(input_data)
    output_fingerprint = _calculate_fingerprint(output_data)
    
    # Capture metadata
    capture_time = datetime.now().isoformat()
    
    # Create trace record
    trace_record = {
        'tool_name': tool_name,
        'input_fingerprint': input_fingerprint,
        'output_fingerprint': output_fingerprint,
        'input_size': len(str(input_data)) if input_data is not None else 0,
        'output_size': len(str(output_data)) if output_data is not None else 0,
        'capture_time': capture_time,
        'context': context,
        'data_flow_path': []
    }
    
    # Save trace record
    trace_file = os.path.join(diagnostics_dir, f"{trace_id}.json")
    with open(trace_file, 'w', encoding='utf-8') as f:
        json.dump(trace_record, f, ensure_ascii=False, indent=2)
    
    return {
        'operation': 'capture_stream',
        'trace_id': trace_id,
        'input_fingerprint': input_fingerprint,
        'output_fingerprint': output_fingerprint,
        'capture_time': capture_time,
        'trace_file': trace_file
    }

def _validate_stream_integrity(trace_id: str, diagnostics_dir: str) -> Dict[str, Any]:
    """Validate the integrity of a captured stream"""
    trace_file = os.path.join(diagnostics_dir, f"{trace_id}.json")
    
    if not os.path.exists(trace_file):
        return {
            'operation': 'validate_integrity',
            'trace_id': trace_id,
            'status': 'error',
            'message': '未找到指定的追踪记录'
        }
    
    with open(trace_file, 'r', encoding='utf-8') as f:
        trace_data = json.load(f)
    
    # Perform integrity checks
    integrity_checks = {
        'file_exists': True,
        'input_fingerprint_valid': bool(trace_data.get('input_fingerprint')),
        'output_fingerprint_valid': bool(trace_data.get('output_fingerprint')),
        'timestamps_valid': bool(trace_data.get('capture_time')),
        'tool_name_present': bool(trace_data.get('tool_name'))
    }
    
    # Overall integrity status
    overall_status = all(integrity_checks.values())
    
    return {
        'operation': 'validate_integrity',
        'trace_id': trace_id,
        'status': 'valid' if overall_status else 'invalid',
        'checks': integrity_checks,
        'overall_integrity': overall_status
    }

def _trace_data_flow(trace_id: str, diagnostics_dir: str) -> Dict[str, Any]:
    """Trace the data flow for a specific trace ID"""
    trace_file = os.path.join(diagnostics_dir, f"{trace_id}.json")
    
    if not os.path.exists(trace_file):
        return {
            'operation': 'trace_flow',
            'trace_id': trace_id,
            'status': 'error',
            'message': '未找到指定的追踪记录'
        }
    
    with open(trace_file, 'r', encoding='utf-8') as f:
        trace_data = json.load(f)
    
    # Extract data flow information
    data_flow = {
        'source': 'input',
        'destination': 'output',
        'tool_name': trace_data.get('tool_name'),
        'input_size': trace_data.get('input_size', 0),
        'output_size': trace_data.get('output_size', 0),
        'transformation_time': trace_data.get('capture_time'),
        'context': trace_data.get('context', {})
    }
    
    return {
        'operation': 'trace_flow',
        'trace_id': trace_id,
        'data_flow': data_flow
    }

def _generate_integrity_report(diagnostics_dir: str) -> Dict[str, Any]:
    """Generate a comprehensive integrity report"""
    # Count total traces
    trace_files = [f for f in os.listdir(diagnostics_dir) if f.endswith('.json')]
    total_traces = len(trace_files)
    
    # Analyze trace validity
    valid_traces = 0
    tool_distribution = {}
    
    for trace_file in trace_files:
        trace_path = os.path.join(diagnostics_dir, trace_file)
        with open(trace_path, 'r', encoding='utf-8') as f:
            trace_data = json.load(f)
        
        # Check if trace is valid
        is_valid = (
            bool(trace_data.get('input_fingerprint')) and
            bool(trace_data.get('output_fingerprint')) and
            bool(trace_data.get('tool_name'))
        )
        
        if is_valid:
            valid_traces += 1
        
        # Count tool distribution
        tool_name = trace_data.get('tool_name', 'unknown')
        tool_distribution[tool_name] = tool_distribution.get(tool_name, 0) + 1
    
    # Calculate statistics
    validity_rate = valid_traces / total_traces if total_traces > 0 else 0
    
    return {
        'operation': 'generate_report',
        'total_traces': total_traces,
        'valid_traces': valid_traces,
        'validity_rate': validity_rate,
        'tool_distribution': tool_distribution,
        'report_time': datetime.now().isoformat()
    }

def _calculate_fingerprint(data: Any) -> str:
    """Calculate a fingerprint for the given data"""
    import hashlib
    
    if data is None:
        return "none"
    
    # Convert to string representation
    if isinstance(data, dict):
        data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
    else:
        data_str = str(data)
    
    # Calculate SHA-256 hash
    return hashlib.sha256(data_str.encode('utf-8')).hexdigest()[:16]

def _store_trace_info(result: Dict, diagnostics_dir: str) -> None:
    """Store trace information for future reference"""
    # This is already handled in the individual functions
    pass