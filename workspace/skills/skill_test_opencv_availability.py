def main(input_args):
    """
    测试OpenCV是否已正确安装并可以导入使用
    """
    try:
        import cv2
        version = cv2.__version__
        return {
            'result': {'success': True, 'opencv_version': version, 'message': f'OpenCV {version} is available and working'},
            'insights': [f'OpenCV {version} is successfully installed and can be imported'],
            'facts': [f'OpenCV version {version} is available'],
            'memories': []
        }
    except ImportError as e:
        return {
            'result': {'success': False, 'error': str(e), 'message': 'OpenCV is not available'},
            'insights': ['OpenCV is not installed or cannot be imported'],
            'facts': [],
            'memories': []
        }