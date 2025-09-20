#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音频文件歌词标签处理程序
支持提取、处理和注入多语言双语歌词到音频文件标签中
- 支持中英、日英双语歌词分离
- 智能识别平假名、片假名、汉字、英文
- 将混合语言的单行歌词分离为多行统一时间戳歌词
支持的格式：FLAC, MP3, OGG, MP4/M4A
"""

import os
import re
import sys
import chardet
from typing import List, Tuple, Optional, Dict, Any
from mutagen import File as MutagenFile
from mutagen.flac import FLAC, VCFLACDict
from mutagen.mp3 import MP3
from mutagen.id3 import ID3NoHeaderError, USLT, TIT2
from mutagen.oggvorbis import OggVorbis
from mutagen.mp4 import MP4


class LyricsProcessor:
    """歌词处理器类"""
    
    def __init__(self):
        self.supported_formats = ['.flac', '.mp3', '.ogg', '.m4a', '.mp4']
        
    def detect_encoding(self, text_bytes: bytes) -> str:
        """检测文本编码"""
        if not text_bytes:
            return 'utf-8'
            
        # 尝试检测编码
        detected = chardet.detect(text_bytes)
        confidence = detected.get('confidence', 0)
        encoding = detected.get('encoding', 'utf-8')
        
        # 如果置信度太低，默认使用utf-8
        if confidence < 0.7:
            encoding = 'utf-8'
            
        return encoding or 'utf-8'
    
    def extract_lyrics_from_file(self, file_path: str) -> Optional[str]:
        """从音频文件标签中提取歌词"""
        try:
            audio_file = MutagenFile(file_path)
            if audio_file is None:
                print(f"不支持的文件格式: {file_path}")
                return None
            
            lyrics = None
            
            # FLAC文件处理
            if isinstance(audio_file, FLAC):
                lyrics = self._extract_flac_lyrics(audio_file)
            
            # MP3文件处理
            elif isinstance(audio_file, MP3):
                lyrics = self._extract_mp3_lyrics(audio_file)
            
            # OGG文件处理
            elif isinstance(audio_file, OggVorbis):
                lyrics = self._extract_ogg_lyrics(audio_file)
            
            # MP4文件处理
            elif isinstance(audio_file, MP4):
                lyrics = self._extract_mp4_lyrics(audio_file)
            
            return lyrics
            
        except Exception as e:
            print(f"提取歌词失败 {file_path}: {str(e)}")
            return None
    
    def _extract_flac_lyrics(self, audio_file: FLAC) -> Optional[str]:
        """从FLAC文件提取歌词"""
        # 常见的歌词标签字段
        lyrics_fields = ['LYRICS', 'UNSYNCED LYRICS', 'UNSYNCEDLYRICS', 'lyrics']
        
        for field in lyrics_fields:
            if field in audio_file:
                lyrics_data = audio_file[field][0]
                if isinstance(lyrics_data, bytes):
                    encoding = self.detect_encoding(lyrics_data)
                    try:
                        return lyrics_data.decode(encoding)
                    except UnicodeDecodeError:
                        try:
                            return lyrics_data.decode('utf-8', errors='ignore')
                        except:
                            continue
                else:
                    return str(lyrics_data)
        
        return None
    
    def _extract_mp3_lyrics(self, audio_file: MP3) -> Optional[str]:
        """从MP3文件提取歌词"""
        # ID3标签中的歌词字段
        if hasattr(audio_file, 'tags') and audio_file.tags:
            # 查找USLT帧（非同步歌词）
            for key, value in audio_file.tags.items():
                if key.startswith('USLT'):
                    if hasattr(value, 'text'):
                        return value.text
                    else:
                        return str(value)
                        
            # 查找其他可能的歌词字段
            lyrics_keys = ['TXXX:LYRICS', 'TXXX:lyrics', 'TXT', 'COMM::eng']
            for key in lyrics_keys:
                if key in audio_file.tags:
                    value = audio_file.tags[key]
                    if hasattr(value, 'text'):
                        return value.text[0] if value.text else None
                    else:
                        return str(value)
        
        return None
    
    def _extract_ogg_lyrics(self, audio_file: OggVorbis) -> Optional[str]:
        """从OGG文件提取歌词"""
        lyrics_fields = ['LYRICS', 'UNSYNCED LYRICS', 'UNSYNCEDLYRICS']
        
        for field in lyrics_fields:
            if field in audio_file:
                return audio_file[field][0]
        
        return None
    
    def _extract_mp4_lyrics(self, audio_file: MP4) -> Optional[str]:
        """从MP4文件提取歌词"""
        # MP4标签中的歌词字段
        lyrics_fields = ['\xa9lyr', 'lyr', 'LYRICS']
        
        for field in lyrics_fields:
            if field in audio_file:
                lyrics_data = audio_file[field][0]
                if isinstance(lyrics_data, bytes):
                    encoding = self.detect_encoding(lyrics_data)
                    try:
                        return lyrics_data.decode(encoding)
                    except UnicodeDecodeError:
                        try:
                            return lyrics_data.decode('utf-8', errors='ignore')
                        except:
                            continue
                else:
                    return str(lyrics_data)
        
        return None
    
    def parse_bilingual_lyrics(self, lyrics_text: str) -> List[str]:
        """解析双语歌词，将单行双语歌词分离成两行"""
        if not lyrics_text:
            return []
        
        lines = lyrics_text.split('\n')
        processed_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                processed_lines.append('')
                continue
                
            # 检查是否包含时间戳
            timestamp_match = re.match(r'^(\[\d{2}:\d{2}\.\d{2,3}\])', line)
            if timestamp_match:
                timestamp = timestamp_match.group(1)
                content = line[len(timestamp):].strip()
                
                # 尝试分离中英文（简单的启发式方法）
                separated_lines = self._separate_languages(content)
                
                if len(separated_lines) > 1:
                    # 如果成功分离，为每一行添加相同的时间戳
                    for separated_line in separated_lines:
                        if separated_line.strip():
                            processed_lines.append(f"{timestamp}{separated_line}")
                else:
                    # 如果无法分离，保持原样
                    processed_lines.append(line)
            else:
                # 没有时间戳的行，尝试分离语言
                separated_lines = self._separate_languages(line)
                if len(separated_lines) > 1:
                    processed_lines.extend(separated_lines)
                else:
                    processed_lines.append(line)
        
        return processed_lines
    
    def _separate_languages(self, text: str) -> List[str]:
        """分离多语言文本（日文单独一行，英文+中文为另一行）"""
        if not text.strip():
            return [text]
        
        # 检测各种语言字符
        has_hiragana = bool(re.search(r'[\u3040-\u309f]', text))  # 平假名
        has_katakana = bool(re.search(r'[\u30a0-\u30ff]', text))  # 片假名
        has_kanji = bool(re.search(r'[\u4e00-\u9fff]', text))     # 汉字
        has_english = bool(re.search(r'[a-zA-Z]', text))          # 英文字母
        
        # 判断是否包含日文（有假名就认为是日文）
        is_japanese_context = has_hiragana or has_katakana
        
        # 如果包含日文（假名），进行分离
        if is_japanese_context:
            # 在日语上下文中，分离出三种类型：日文、英文、中文
            japanese_parts = []  # 日文（假名 + 相关汉字）
            english_parts = []   # 英文
            chinese_parts = []   # 中文（非日语汉字）
            
            i = 0
            while i < len(text):
                char = text[i]
                
                if '\u3040' <= char <= '\u309f' or '\u30a0' <= char <= '\u30ff':
                    # 假名：肯定是日文
                    japanese_parts.append(char)
                elif '\u4e00' <= char <= '\u9fff':
                    # 汉字：需要判断是日文汉字还是中文汉字
                    is_japanese_kanji = False
                    
                    # 首先检查紧邻位置（前后1个字符，忽略空格）
                    # 紧邻假名的汉字肯定是日文
                    if i > 0:
                        prev_char = text[i-1]
                        if prev_char != ' ' and ('\u3040' <= prev_char <= '\u309f' or '\u30a0' <= prev_char <= '\u30ff'):
                            is_japanese_kanji = True
                    
                    if not is_japanese_kanji and i < len(text) - 1:
                        next_char = text[i+1]
                        if next_char != ' ' and ('\u3040' <= next_char <= '\u309f' or '\u30a0' <= next_char <= '\u30ff'):
                            is_japanese_kanji = True
                    
                    # 如果不是紧邻假名，检查是否在连续汉字序列中，且序列与假名相邻
                    if not is_japanese_kanji:
                        # 查找当前汉字所在的连续汉字序列
                        start = i
                        while start > 0 and ('\u4e00' <= text[start-1] <= '\u9fff' or text[start-1] == ' '):
                            if text[start-1] != ' ':  # 只有遇到汉字才移动
                                start -= 1
                            else:
                                break  # 遇到空格就停止
                        
                        end = i
                        while end < len(text)-1 and ('\u4e00' <= text[end+1] <= '\u9fff' or text[end+1] == ' '):
                            if text[end+1] != ' ':  # 只有遇到汉字才移动
                                end += 1
                            else:
                                break  # 遇到空格就停止
                        
                        # 检查汉字序列的紧邻位置是否有假名
                        if start > 0:
                            prev_char = text[start-1]
                            if ('\u3040' <= prev_char <= '\u309f' or '\u30a0' <= prev_char <= '\u30ff'):
                                is_japanese_kanji = True
                        
                        if not is_japanese_kanji and end < len(text)-1:
                            next_char = text[end+1]
                            if ('\u3040' <= next_char <= '\u309f' or '\u30a0' <= next_char <= '\u30ff'):
                                is_japanese_kanji = True
                    
                    # 根据判断结果分类汉字
                    if is_japanese_kanji:
                        japanese_parts.append(char)
                    else:
                        chinese_parts.append(char)
                elif char.isalpha() and ord(char) < 128:
                    # ASCII英文字母
                    english_parts.append(char)
                elif char == ' ':
                    # 空格需要根据上下文分配
                    # 检查前后字符来决定空格属于哪个部分
                    assigned = False
                    
                    # 优先分配给英文（保持英文单词完整）
                    if i > 0 and i < len(text) - 1:
                        prev_char = text[i-1]
                        next_char = text[i+1]
                        if (prev_char.isalpha() and ord(prev_char) < 128) or (next_char.isalpha() and ord(next_char) < 128):
                            english_parts.append(char)
                            assigned = True
                    
                    # 如果不能分配给英文，检查是否应该分配给日文
                    if not assigned:
                        if i > 0:
                            prev_char = text[i-1]
                            if '\u3040' <= prev_char <= '\u309f' or '\u30a0' <= prev_char <= '\u30ff':
                                japanese_parts.append(char)
                                assigned = True
                        
                        if not assigned and i < len(text) - 1:
                            next_char = text[i+1]
                            if '\u3040' <= next_char <= '\u309f' or '\u30a0' <= next_char <= '\u30ff':
                                japanese_parts.append(char)
                                assigned = True
                    
                    # 最后分配给中文
                    if not assigned:
                        chinese_parts.append(char)
                else:
                    # 其他标点符号等，按照就近原则分配
                    if char in '\'"':
                        # 英文引号和撇号跟英文
                        english_parts.append(char)
                    elif char in '.,!?;:()[]{}':
                        # 其他标点跟中文
                        chinese_parts.append(char)  
                    else:
                        # 其他符号跟英文
                        english_parts.append(char)
                
                i += 1
            
            # 合并各部分
            japanese_text = ''.join(japanese_parts).strip()
            english_text = ''.join(english_parts).strip()
            chinese_text = ''.join(chinese_parts).strip()
            
            # 清理多余空格
            japanese_text = re.sub(r'\s+', ' ', japanese_text).strip()
            english_text = re.sub(r'\s+', ' ', english_text).strip()
            chinese_text = re.sub(r'\s+', ' ', chinese_text).strip()
            
            # 根据内容决定分离策略
            if len(chinese_text) > 0 and (len(japanese_text) > 0 or len(english_text) > 0):
                # 有中文需要分离：日英保持在第一行，中文在第二行
                first_line_parts = []
                if len(japanese_text) > 0:
                    first_line_parts.append(japanese_text)
                if len(english_text) > 0:
                    first_line_parts.append(english_text)
                
                first_line = ' '.join(first_line_parts).strip()
                return [first_line, chinese_text]
            # 如果只有日英，无中文：不分离，保持原文
            # 因为要求是只将中文移到第二行，日英保持原位置
        
        # 如果是纯中英文（无日文），也进行分离
        elif has_english and has_kanji and not is_japanese_context:
            chinese_chars = []
            english_chars = []
            
            for char in text:
                if (char.isalpha() and ord(char) < 128) or char.isdigit():  # ASCII英文字母或数字
                    english_chars.append(char)
                elif '\u4e00' <= char <= '\u9fff':      # 中文汉字
                    chinese_chars.append(char)
                elif char in ' \t\n\r.,!?;:\'"()[]{}':  # 标点符号
                    # 英文相关标点跟英文，中文相关标点跟中文
                    if char in ' \'".,!?()[]':  # 常见英文标点跟英文
                        english_chars.append(char)
                    else:  # 其他标点（如冒号、分号等）跟中文
                        chinese_chars.append(char)
                else:
                    # 其他字符跟中文
                    chinese_chars.append(char)
            
            chinese_text = ''.join(chinese_chars).strip()
            english_text = ''.join(english_chars).strip()
            
            # 清理多余空格
            english_text = re.sub(r'\s+', ' ', english_text).strip()
            
            if len(chinese_text) > 0 and len(english_text) > 1:
                return [english_text, chinese_text]
        
        # 无法分离，返回原文
        return [text]
    
    def inject_lyrics_to_file(self, file_path: str, lyrics: str) -> bool:
        """将处理后的歌词注入音频文件标签"""
        try:
            audio_file = MutagenFile(file_path)
            if audio_file is None:
                print(f"不支持的文件格式: {file_path}")
                return False
            
            # 根据文件类型选择注入方法
            if isinstance(audio_file, FLAC):
                return self._inject_flac_lyrics(audio_file, lyrics, file_path)
            elif isinstance(audio_file, MP3):
                return self._inject_mp3_lyrics(audio_file, lyrics, file_path)
            elif isinstance(audio_file, OggVorbis):
                return self._inject_ogg_lyrics(audio_file, lyrics, file_path)
            elif isinstance(audio_file, MP4):
                return self._inject_mp4_lyrics(audio_file, lyrics, file_path)
            
            return False
            
        except Exception as e:
            print(f"注入歌词失败 {file_path}: {str(e)}")
            return False
    
    def _inject_flac_lyrics(self, audio_file: FLAC, lyrics: str, file_path: str) -> bool:
        """向FLAC文件注入歌词"""
        try:
            audio_file['LYRICS'] = lyrics
            audio_file.save()
            return True
        except Exception as e:
            print(f"FLAC歌词注入失败: {str(e)}")
            return False
    
    def _inject_mp3_lyrics(self, audio_file: MP3, lyrics: str, file_path: str) -> bool:
        """向MP3文件注入歌词"""
        try:
            # 确保有ID3标签
            if audio_file.tags is None:
                audio_file.add_tags()
            
            # 添加USLT帧（非同步歌词）
            audio_file.tags.add(USLT(encoding=3, lang='eng', desc='', text=lyrics))
            audio_file.save()
            return True
        except Exception as e:
            print(f"MP3歌词注入失败: {str(e)}")
            return False
    
    def _inject_ogg_lyrics(self, audio_file: OggVorbis, lyrics: str, file_path: str) -> bool:
        """向OGG文件注入歌词"""
        try:
            audio_file['LYRICS'] = lyrics
            audio_file.save()
            return True
        except Exception as e:
            print(f"OGG歌词注入失败: {str(e)}")
            return False
    
    def _inject_mp4_lyrics(self, audio_file: MP4, lyrics: str, file_path: str) -> bool:
        """向MP4文件注入歌词"""
        try:
            audio_file['\xa9lyr'] = lyrics
            audio_file.save()
            return True
        except Exception as e:
            print(f"MP4歌词注入失败: {str(e)}")
            return False
    
    def process_single_file(self, file_path: str, backup: bool = True) -> bool:
        """处理单个音频文件"""
        print(f"\n处理文件: {os.path.basename(file_path)}")
        
        # 检查文件格式
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in self.supported_formats:
            print(f"不支持的文件格式: {file_ext}")
            return False
        
        # 提取原始歌词
        original_lyrics = self.extract_lyrics_from_file(file_path)
        if not original_lyrics:
            print("未找到歌词标签")
            return False
        
        print("原始歌词:")
        print(original_lyrics[:200] + "..." if len(original_lyrics) > 200 else original_lyrics)
        
        # 处理双语歌词
        processed_lyrics_lines = self.parse_bilingual_lyrics(original_lyrics)
        processed_lyrics = '\n'.join(processed_lyrics_lines)
        
        # 检查是否有变化
        if processed_lyrics == original_lyrics:
            print("歌词无需处理")
            return True
        
        print("\n处理后歌词:")
        print(processed_lyrics[:200] + "..." if len(processed_lyrics) > 200 else processed_lyrics)
        
        # 备份原文件（如果需要）
        if backup:
            backup_path = file_path + '.backup'
            if not os.path.exists(backup_path):
                import shutil
                shutil.copy2(file_path, backup_path)
                print(f"已创建备份: {os.path.basename(backup_path)}")
        
        # 注入处理后的歌词
        success = self.inject_lyrics_to_file(file_path, processed_lyrics)
        if success:
            print("✓ 歌词处理完成")
        else:
            print("✗ 歌词注入失败")
        
        return success
    
    def process_directory(self, directory_path: str, recursive: bool = True, backup: bool = True) -> Dict[str, Any]:
        """批量处理目录中的音频文件"""
        results = {
            'processed': 0,
            'success': 0,
            'failed': 0,
            'no_lyrics': 0,
            'unsupported': 0
        }
        
        print(f"开始处理目录: {directory_path}")
        print(f"递归处理: {'是' if recursive else '否'}")
        print(f"创建备份: {'是' if backup else '否'}")
        
        # 收集所有音频文件
        audio_files = []
        
        if recursive:
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_ext = os.path.splitext(file)[1].lower()
                    if file_ext in self.supported_formats:
                        audio_files.append(file_path)
        else:
            for file in os.listdir(directory_path):
                file_path = os.path.join(directory_path, file)
                if os.path.isfile(file_path):
                    file_ext = os.path.splitext(file)[1].lower()
                    if file_ext in self.supported_formats:
                        audio_files.append(file_path)
        
        print(f"找到 {len(audio_files)} 个音频文件")
        
        # 处理每个文件
        for i, file_path in enumerate(audio_files, 1):
            print(f"\n[{i}/{len(audio_files)}]", end=' ')
            
            try:
                results['processed'] += 1
                
                # 检查文件格式
                file_ext = os.path.splitext(file_path)[1].lower()
                if file_ext not in self.supported_formats:
                    results['unsupported'] += 1
                    continue
                
                # 提取歌词
                original_lyrics = self.extract_lyrics_from_file(file_path)
                if not original_lyrics:
                    results['no_lyrics'] += 1
                    print(f"跳过 {os.path.basename(file_path)} - 未找到歌词")
                    continue
                
                # 处理歌词
                processed_lyrics_lines = self.parse_bilingual_lyrics(original_lyrics)
                processed_lyrics = '\n'.join(processed_lyrics_lines)
                
                # 检查是否有变化
                if processed_lyrics == original_lyrics:
                    results['success'] += 1
                    print(f"跳过 {os.path.basename(file_path)} - 无需处理")
                    continue
                
                # 备份和注入
                if backup:
                    backup_path = file_path + '.backup'
                    if not os.path.exists(backup_path):
                        import shutil
                        shutil.copy2(file_path, backup_path)
                
                success = self.inject_lyrics_to_file(file_path, processed_lyrics)
                if success:
                    results['success'] += 1
                    print(f"✓ {os.path.basename(file_path)}")
                else:
                    results['failed'] += 1
                    print(f"✗ {os.path.basename(file_path)}")
                    
            except Exception as e:
                results['failed'] += 1
                print(f"✗ {os.path.basename(file_path)} - 错误: {str(e)}")
        
        # 输出处理结果统计
        print(f"\n处理完成!")
        print(f"总文件数: {results['processed']}")
        print(f"成功处理: {results['success']}")
        print(f"处理失败: {results['failed']}")
        print(f"无歌词文件: {results['no_lyrics']}")
        print(f"不支持格式: {results['unsupported']}")
        
        return results


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='音频文件双语歌词处理工具')
    parser.add_argument('path', help='要处理的文件或目录路径')
    parser.add_argument('--no-backup', action='store_true', help='不创建备份文件')
    parser.add_argument('--no-recursive', action='store_true', help='不递归处理子目录')
    parser.add_argument('--preview', action='store_true', help='仅预览，不实际修改文件')
    
    args = parser.parse_args()
    
    processor = LyricsProcessor()
    
    if not os.path.exists(args.path):
        print(f"错误: 路径不存在 - {args.path}")
        return 1
    
    backup = not args.no_backup
    recursive = not args.no_recursive
    
    if os.path.isfile(args.path):
        # 处理单个文件
        if args.preview:
            print("预览模式 - 仅显示处理结果，不修改文件")
            original_lyrics = processor.extract_lyrics_from_file(args.path)
            if original_lyrics:
                processed_lyrics_lines = processor.parse_bilingual_lyrics(original_lyrics)
                processed_lyrics = '\n'.join(processed_lyrics_lines)
                print("原始歌词:")
                print(original_lyrics)
                print("\n处理后歌词:")
                print(processed_lyrics)
            else:
                print("未找到歌词")
        else:
            processor.process_single_file(args.path, backup)
    else:
        # 处理目录
        if args.preview:
            print("预览模式暂不支持目录处理")
            return 1
        processor.process_directory(args.path, recursive, backup)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())