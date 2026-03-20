def main(input_args):
    """测试 input_args 参数"""
    return {
        "input_args_type": str(type(input_args)),
        "input_args_value": str(input_args),
        "input_args_repr": repr(input_args)
    }