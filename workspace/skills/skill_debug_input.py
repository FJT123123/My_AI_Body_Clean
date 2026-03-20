def main(input_args):
    """调试技能，返回接收到的输入参数"""
    return {
        "success": True,
        "input_args_type": str(type(input_args)),
        "input_args_value": str(input_args),
        "input_args_repr": repr(input_args)
    }