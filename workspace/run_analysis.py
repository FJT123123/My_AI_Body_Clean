#!/usr/bin/env python3

import os
import sys
sys.path.append('/Users/zhufeng/My_AI_Body_副本')

# 现在导入并运行分析函数
import analyze_codec_semantics

if __name__ == "__main__":
    result = analyze_codec_semantics.analyze_codec_physical_semantics(
        "./extracted_frames_for_codec_analysis", 
        "./codec_semantics_results"
    )
    print("Analysis completed!")
    print(f"Analyzed {result.get('frame_count', 0)} frames")
    if 'motion_analysis' in result:
        print(f"Motion analysis entries: {len(result['motion_analysis'])}")