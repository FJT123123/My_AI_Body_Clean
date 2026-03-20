# capability_name: video_parameter_contract_validator_capability

import json
import re
from typing import Any, Dict, List, Union, Optional


def unified_parameter_parser(input_data: Any) -> Dict[str, Any]:
    """
    统一参数解析器，支持多种输入格式并返回标准化参数
    """
    try:
        # 处理 None 情况
        if input_data is None:
            return {"status": "success", "parsed_params": {}, "format_diagnosis": "input_was_none"}

        # 处理字典类型（最常见情况）
        if isinstance(input_data, dict):
            # 检查是否是 run_skill 包装格式
            if 'params' in input_data and isinstance(input_data['params'], dict):
                return {
                    "status": "success",
                    "parsed_params": input_data['params'],
                    "format_diagnosis": "wrapped_in_params"
                }
            else:
                return {
                    "status": "success",
                    "parsed_params": input_data,
                    "format_diagnosis": "direct_dict"
                }

        # 处理字符串类型
        if isinstance(input_data, str):
            # 检查是否是 JSON 字符串
            if input_data.strip().startswith('{') and input_data.strip().endswith('}'):
                try:
                    parsed_json = json.loads(input_data)
                    # 再次检查是否是 run_skill 包装格式
                    if isinstance(parsed_json, dict):
                        if 'params' in parsed_json and isinstance(parsed_json['params'], dict):
                            return {
                                "status": "success",
                                "parsed_params": parsed_json['params'],
                                "format_diagnosis": "json_wrapped_in_params"
                            }
                        else:
                            return {
                                "status": "success",
                                "parsed_params": parsed_json,
                                "format_diagnosis": "json_dict"
                            }
                except json.JSONDecodeError:
                    # 如果JSON解析失败，作为原始字符串返回
                    return {
                        "status": "success",
                        "parsed_params": {"raw_string": input_data},
                        "format_diagnosis": "raw_string",
                        "warnings": ["input_was_json_string_but_failed_parse"]
                    }
            else:
                # 普通字符串
                return {
                    "status": "success",
                    "parsed_params": {"raw_string": input_data},
                    "format_diagnosis": "raw_string"
                }

        # 处理列表类型
        if isinstance(input_data, list):
            return {
                "status": "success",
                "parsed_params": {"raw_list": input_data},
                "format_diagnosis": "raw_list"
            }

        # 其他类型
        return {
            "status": "success",
            "parsed_params": {"raw_value": input_data, "type": type(input_data).__name__},
            "format_diagnosis": "unknown_type"
        }

    except Exception as e:
        return {
            "status": "error",
            "error": f"parsing_failed: {str(e)}",
            "parsed_params": {},
            "format_diagnosis": "parsing_error"
        }


def validate_parameter_contract(params: Dict[str, Any], expected_contract: Dict[str, Any]) -> Dict[str, Any]:
    """
    验证参数是否符合预定义契约
    """
    try:
        if not isinstance(params, dict):
            return {
                "status": "error",
                "validation_result": "params_must_be_dict",
                "missing_fields": [],
                "invalid_types": [],
                "errors": ["parameters must be a dictionary"]
            }

        if not isinstance(expected_contract, dict):
            return {
                "status": "error",
                "validation_result": "contract_must_be_dict",
                "missing_fields": [],
                "invalid_types": [],
                "errors": ["expected contract must be a dictionary"]
            }

        required_fields = expected_contract.get("required", [])
        optional_fields = expected_contract.get("optional", [])
        field_types = expected_contract.get("types", {})

        missing_fields = []
        invalid_types = []
        errors = []

        # 检查必需字段
        for field in required_fields:
            if field not in params:
                missing_fields.append(field)
                errors.append(f"missing required field: {field}")

        # 检查字段类型
        for field, expected_type in field_types.items():
            if field in params:
                actual_value = params[field]
                actual_type = type(actual_value).__name__

                if expected_type == "string" and not isinstance(actual_value, str):
                    invalid_types.append({
                        "field": field,
                        "expected": "string",
                        "actual": actual_type,
                        "value": actual_value
                    })
                    errors.append(f"field '{field}' expected string, got {actual_type}")

                elif expected_type == "number" and not isinstance(actual_value, (int, float)):
                    invalid_types.append({
                        "field": field,
                        "expected": "number",
                        "actual": actual_type,
                        "value": actual_value
                    })
                    errors.append(f"field '{field}' expected number, got {actual_type}")

                elif expected_type == "boolean" and not isinstance(actual_value, bool):
                    invalid_types.append({
                        "field": field,
                        "expected": "boolean",
                        "actual": actual_type,
                        "value": actual_value
                    })
                    errors.append(f"field '{field}' expected boolean, got {actual_type}")

                elif expected_type == "array" and not isinstance(actual_value, list):
                    invalid_types.append({
                        "field": field,
                        "expected": "array",
                        "actual": actual_type,
                        "value": actual_value
                    })
                    errors.append(f"field '{field}' expected array, got {actual_type}")

                elif expected_type == "object" and not isinstance(actual_value, dict):
                    invalid_types.append({
                        "field": field,
                        "expected": "object",
                        "actual": actual_type,
                        "value": actual_value
                    })
                    errors.append(f"field '{field}' expected object, got {actual_type}")

        if missing_fields or invalid_types:
            return {
                "status": "invalid",
                "validation_result": "contract_violation",
                "missing_fields": missing_fields,
                "invalid_types": invalid_types,
                "errors": errors
            }
        else:
            return {
                "status": "valid",
                "validation_result": "contract_compliant",
                "missing_fields": [],
                "invalid_types": [],
                "errors": []
            }

    except Exception as e:
        return {
            "status": "error",
            "validation_result": "validation_failed",
            "missing_fields": [],
            "invalid_types": [],
            "errors": [f"validation error: {str(e)}"]
        }


def repair_parameter_format(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    自动修复参数格式问题
    """
    try:
        if not isinstance(params, dict):
            return {
                "status": "error",
                "repair_result": "params_must_be_dict",
                "repaired_params": {}
            }

        repaired_params = {}
        repair_log = []

        for key, value in params.items():
            # 修复字符串包含JSON的情况
            if isinstance(value, str):
                stripped_value = value.strip()
                if stripped_value.startswith('{') and stripped_value.endswith('}'):
                    try:
                        parsed_json = json.loads(stripped_value)
                        repaired_params[key] = parsed_json
                        repair_log.append(f"repaired JSON string for key '{key}'")
                    except json.JSONDecodeError:
                        # 如果解析失败，保持原值
                        repaired_params[key] = value
                else:
                    # 检查是否是数字字符串
                    if value.replace('.', '').replace('-', '').isdigit():
                        try:
                            if '.' in value:
                                repaired_params[key] = float(value)
                                repair_log.append(f"converted string number to float for key '{key}'")
                            else:
                                repaired_params[key] = int(value)
                                repair_log.append(f"converted string number to int for key '{key}'")
                        except ValueError:
                            repaired_params[key] = value
                    else:
                        repaired_params[key] = value
            # 修复布尔值字符串
            elif isinstance(value, str) and value.lower() in ['true', 'false']:
                repaired_params[key] = value.lower() == 'true'
                repair_log.append(f"converted string boolean to actual boolean for key '{key}'")
            else:
                repaired_params[key] = value

        return {
            "status": "success",
            "repair_result": "format_repaired",
            "repaired_params": repaired_params,
            "repair_log": repair_log
        }

    except Exception as e:
        return {
            "status": "error",
            "repair_result": "repair_failed",
            "repaired_params": {},
            "repair_log": [f"repair error: {str(e)}"]
        }


def generate_parameter_error_info(params: Any, contract: Dict[str, Any]) -> Dict[str, Any]:
    """
    生成详细的参数错误信息
    """
    try:
        # 如果参数不是字典，直接返回错误信息
        if not isinstance(params, dict):
            return {
                "error_type": "parameter_format_error",
                "error_message": "Parameters must be a dictionary",
                "diagnosis": "params_not_dict",
                "suggested_fix": "Ensure parameters are passed as a dictionary object",
                "recommended_validation": "validate_parameter_contract"
            }

        # 验证参数契约
        validation_result = validate_parameter_contract(params, contract)

        if validation_result["status"] == "valid":
            return {
                "error_type": "no_error",
                "error_message": "Parameters are valid",
                "diagnosis": "parameters_compliant",
                "suggested_fix": "No fixes needed",
                "recommended_validation": "contract_valid"
            }

        # 如果有验证错误，生成详细错误信息
        errors = validation_result.get("errors", [])
        missing_fields = validation_result.get("missing_fields", [])
        invalid_types = validation_result.get("invalid_types", [])

        error_info = {
            "error_type": "parameter_contract_violation",
            "error_message": "Parameter contract not satisfied",
            "diagnosis": "contract_violation",
            "validation_details": validation_result,
            "suggested_fix": "Check required fields and ensure correct data types",
            "recommended_validation": "validate_parameter_contract"
        }

        if missing_fields:
            error_info["missing_fields"] = missing_fields
            error_info["fix_suggestion"] = f"Add missing required fields: {', '.join(missing_fields)}"

        if invalid_types:
            error_info["invalid_types"] = invalid_types
            type_fixes = []
            for invalid_type in invalid_types:
                type_fixes.append(f"Field '{invalid_type['field']}' should be {invalid_type['expected']} but got {invalid_type['actual']}")
            error_info["type_fix_suggestions"] = type_fixes

        return error_info

    except Exception as e:
        return {
            "error_type": "error_generation_failed",
            "error_message": f"Failed to generate error info: {str(e)}",
            "diagnosis": "error_info_generation_failed",
            "suggested_fix": "Check parameter format and contract structure",
            "recommended_validation": "manual_inspection_needed"
        }


def run_parameter_validation_cycle(input_data: Any, expected_contract: Dict[str, Any]) -> Dict[str, Any]:
    """
    运行完整的参数验证周期
    """
    try:
        # 1. 解析输入数据
        parse_result = unified_parameter_parser(input_data)
        
        if parse_result["status"] == "error":
            return {
                "cycle_status": "parsing_error",
                "parse_result": parse_result,
                "validation_result": None,
                "repair_result": None,
                "error_info": None
            }

        # 2. 验证参数契约
        params = parse_result["parsed_params"]
        validation_result = validate_parameter_contract(params, expected_contract)

        # 3. 如果验证失败，尝试修复
        repair_result = None
        if validation_result["status"] == "invalid":
            repair_result = repair_parameter_format(params)

        # 4. 生成错误信息
        error_info = generate_parameter_error_info(params, expected_contract)

        return {
            "cycle_status": "completed",
            "parse_result": parse_result,
            "validation_result": validation_result,
            "repair_result": repair_result,
            "error_info": error_info,
            "final_params": repair_result["repaired_params"] if repair_result and repair_result["status"] == "success" else params
        }

    except Exception as e:
        return {
            "cycle_status": "error",
            "error": f"validation_cycle_failed: {str(e)}",
            "parse_result": None,
            "validation_result": None,
            "repair_result": None,
            "error_info": None
        }