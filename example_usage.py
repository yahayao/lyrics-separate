#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的使用示例脚本
演示如何使用 LyricsProcessor 类
"""

from lyrics_processor import LyricsProcessor
import os


def demo_single_file():
    """演示处理单个文件"""
    print("=== 单文件处理示例 ===")
    
    processor = LyricsProcessor()
    
    # 在当前目录寻找一个音频文件进行演示
    for file in os.listdir('.'):
        if any(file.lower().endswith(ext) for ext in processor.supported_formats):
            print(f"找到示例文件: {file}")
            
            # 提取原始歌词
            original_lyrics = processor.extract_lyrics_from_file(file)
            if original_lyrics:
                print("\n原始歌词片段:")
                print(original_lyrics[:200] + "..." if len(original_lyrics) > 200 else original_lyrics)
                
                # 处理歌词
                processed_lines = processor.parse_bilingual_lyrics(original_lyrics)
                processed_lyrics = '\n'.join(processed_lines)
                
                print("\n处理后歌词片段:")
                print(processed_lyrics[:200] + "..." if len(processed_lyrics) > 200 else processed_lyrics)
                
                # 检查是否有变化
                if processed_lyrics != original_lyrics:
                    print("\n✓ 检测到双语歌词，可以进行分离处理")
                else:
                    print("\n- 歌词无需处理")
            else:
                print("未找到歌词标签")
            
            break
    else:
        print("未找到支持的音频文件")


def demo_batch_preview():
    """演示批量预览功能"""
    print("\n=== 批量预览示例 ===")
    
    processor = LyricsProcessor()
    
    # 统计信息
    total_files = 0
    has_lyrics = 0
    needs_processing = 0
    
    # 扫描当前目录
    for file in os.listdir('.'):
        if any(file.lower().endswith(ext) for ext in processor.supported_formats):
            total_files += 1
            
            lyrics = processor.extract_lyrics_from_file(file)
            if lyrics:
                has_lyrics += 1
                
                # 检查是否需要处理
                processed_lines = processor.parse_bilingual_lyrics(lyrics)
                processed_lyrics = '\n'.join(processed_lines)
                
                if processed_lyrics != lyrics:
                    needs_processing += 1
                    print(f"✓ {file} - 需要处理")
                else:
                    print(f"- {file} - 无需处理")
            else:
                print(f"? {file} - 无歌词标签")
    
    print(f"\n统计结果:")
    print(f"音频文件总数: {total_files}")
    print(f"有歌词文件: {has_lyrics}")
    print(f"需要处理的文件: {needs_processing}")


def demo_language_separation():
    """演示语言分离功能"""
    print("\n=== 语言分离功能演示 ===")
    
    processor = LyricsProcessor()
    
    # 测试用的双语歌词示例
    test_cases = [
        "[00:15.23]今日もいい天気だね It's a beautiful day today",
        "[00:18.45]君と歩く道で Walking down the road with you",
        "[00:22.67]心が踊るよ My heart is dancing",
        "这是一首美丽的歌 This is a beautiful song",
        "Hello world 你好世界",
        "纯中文歌词行",
        "Pure English lyrics line",
        "[01:23.45]混合了中文English文字的复杂sentence"
    ]
    
    for test_line in test_cases:
        print(f"\n输入: {test_line}")
        
        # 处理单行
        processed_lines = processor.parse_bilingual_lyrics(test_line)
        
        if len(processed_lines) == 1:
            print(f"输出: {processed_lines[0]} (无需分离)")
        else:
            for i, line in enumerate(processed_lines, 1):
                print(f"输出{i}: {line}")


if __name__ == "__main__":
    print("音频文件双语歌词处理工具 - 使用示例\n")
    
    try:
        demo_single_file()
        demo_batch_preview()
        demo_language_separation()
        
        print("\n=== 使用提示 ===")
        print("1. 使用 --preview 参数预览处理结果")
        print("2. 程序会自动创建备份文件（除非使用 --no-backup）")
        print("3. 支持批量处理整个目录（使用 --no-recursive 仅处理当前目录）")
        print("4. 遇到问题可以查看 README.md 获取详细说明")
        
    except Exception as e:
        print(f"演示过程中出现错误: {str(e)}")
        print("请检查是否正确安装了依赖包: pip install mutagen chardet")