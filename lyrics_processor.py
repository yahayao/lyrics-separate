#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音频文件歌词标签处理程序
支持提取、处理和注入多语言双语歌词到音频文件标签和LRC歌词文件中
- 支持中英、日中双语歌词分离
- 智能识别平假名、片假名、汉字、英文
- 将混合语言的单行歌词分离为多行统一时间戳歌词
支持的格式：FLAC, MP3, OGG, MP4/M4A, LRC
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
        self.supported_formats = ['.flac', '.mp3', '.ogg', '.m4a', '.mp4', '.lrc']
        
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
        """从音频文件标签或LRC文件中提取歌词"""
        # 检查是否是LRC文件
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext == '.lrc':
            return self._extract_lrc_lyrics(file_path)
        
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
    
    def _extract_lrc_lyrics(self, file_path: str) -> Optional[str]:
        """从LRC文件提取歌词"""
        try:
            # 尝试以不同编码读取LRC文件
            encodings = ['utf-8', 'gbk', 'gb2312', 'big5', 'utf-16']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    return content
                except UnicodeDecodeError:
                    continue
                except Exception:
                    continue
            
            # 如果所有编码都失败，尝试二进制读取并自动检测编码
            try:
                with open(file_path, 'rb') as f:
                    raw_data = f.read()
                encoding = self.detect_encoding(raw_data)
                return raw_data.decode(encoding, errors='ignore')
            except Exception as e:
                print(f"LRC文件读取失败 {file_path}: {str(e)}")
                return None
                
        except Exception as e:
            print(f"LRC文件处理失败 {file_path}: {str(e)}")
            return None
    
    def _is_metadata_line(self, line: str) -> bool:
        """判断是否为元数据行（不需要分离处理的行）"""
        line = line.strip()
        
        # 检查常见的LRC元数据标签
        metadata_patterns = [
            r'^\[by:.*\]$',           # [by:作者]
            r'^\[ar:.*\]$',           # [ar:艺术家]
            r'^\[ti:.*\]$',           # [ti:标题]
            r'^\[al:.*\]$',           # [al:专辑]
            r'^\[offset:.*\]$',       # [offset:偏移]
            r'^\[re:.*\]$',           # [re:LRC制作者]
            r'^\[ve:.*\]$',           # [ve:版本]
            r'^\[length:.*\]$',       # [length:长度]
        ]
        
        for pattern in metadata_patterns:
            if re.match(pattern, line):
                return True
        
        # 检查是否包含时间戳的元数据行
        timestamp_match = re.match(r'^(\[\d{2}:\d{2}\.\d{2,3}\])', line)
        if timestamp_match:
            content = line[len(timestamp_match.group(1)):].strip()
            
            # 作词、作曲、编曲等信息行
            metadata_content_patterns = [
                r'^作词\s*[:：]',         # 作词：xxx
                r'^作曲\s*[:：]',         # 作曲：xxx  
                r'^编曲\s*[:：]',         # 编曲：xxx
                r'^制作人\s*[:：]',       # 制作人：xxx
                r'^演唱\s*[:：]',         # 演唱：xxx
                r'^歌手\s*[:：]',         # 歌手：xxx
                r'^专辑\s*[:：]',         # 专辑：xxx
                r'^发行\s*[:：]',         # 发行：xxx
                r'^词\s*[:：]',           # 词：xxx
                r'^曲\s*[:：]',           # 曲：xxx
            ]
            
            for pattern in metadata_content_patterns:
                if re.match(pattern, content):
                    return True
        
        return False

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
            
            # 检查是否为元数据行，如果是则不处理
            if self._is_metadata_line(line):
                processed_lines.append(line)
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
            # 使用基于空格分隔词组的策略来更准确地分类汉字
            char_assignments = ['unassigned'] * len(text)
            
            # 第一步：分配假名（肯定是日文）
            for i, char in enumerate(text):
                if '\u3040' <= char <= '\u309f' or '\u30a0' <= char <= '\u30ff':
                    char_assignments[i] = 'japanese'
            
            # 第二步：按空格分割的词组来分配汉字
            words = text.split(' ')
            current_pos = 0
            
            for word in words:
                if not word:  # 跳过空字符串
                    current_pos += 1  # 空格的位置
                    continue
                    
                # 分析这个词组的语言特征
                word_has_hiragana = any('\u3040' <= c <= '\u309f' for c in word)
                word_has_katakana = any('\u30a0' <= c <= '\u30ff' for c in word)
                word_has_kanji = any('\u4e00' <= c <= '\u9fff' for c in word)
                
                # 判断词组的语言类型
                if word_has_hiragana or word_has_katakana:
                    # 有假名的词组，所有汉字都是日文
                    word_type = 'japanese'
                elif word_has_kanji and not word_has_hiragana and not word_has_katakana:
                    # 纯汉字词组，判断为中文（因为日文中的汉字通常伴随假名）
                    word_type = 'chinese'
                else:
                    # 其他情况，默认中文
                    word_type = 'chinese'
                
                # 为词组中的所有汉字分配类型
                for j, char in enumerate(word):
                    char_pos = current_pos + j
                    if char_pos < len(char_assignments) and '\u4e00' <= char <= '\u9fff' and char_assignments[char_pos] == 'unassigned':
                        char_assignments[char_pos] = word_type
                
                current_pos += len(word) + 1  # +1 for the space after the word            # 第三步：分配英文字母
            for i, char in enumerate(text):
                if char.isalpha() and ord(char) < 128 and char_assignments[i] == 'unassigned':
                    char_assignments[i] = 'english'
            
            # 第四步：分配标点符号和其他字符
            for i, char in enumerate(text):
                if char_assignments[i] == 'unassigned':
                    if char == ' ':
                        # 空格根据前后字符分配
                        assigned = False
                        # 优先跟英文（保持单词完整）
                        if i > 0 and char_assignments[i-1] == 'english':
                            char_assignments[i] = 'english'
                            assigned = True
                        elif i < len(text) - 1 and char_assignments[i+1] == 'english':
                            char_assignments[i] = 'english'
                            assigned = True
                        elif i > 0 and char_assignments[i-1] == 'japanese':
                            char_assignments[i] = 'japanese'
                            assigned = True
                        elif i < len(text) - 1 and char_assignments[i+1] == 'japanese':
                            char_assignments[i] = 'japanese'
                            assigned = True
                        
                        if not assigned:
                            char_assignments[i] = 'chinese'
                            
                    elif char in '.,!?;:()[]{}？！。：；，「」"""\'\'':
                        # 标点符号根据其所属的语句内容分配
                        assigned = False
                        
                        # 特殊处理引号对
                        if char in '「」':
                            # 日文引号应该跟日文内容
                            # 检查引号内外的内容来判断归属
                            char_assignments[i] = 'japanese'
                            assigned = True
                        elif char in '""\'\'':
                            # 英文引号应该跟英文内容
                            # 检查引号内外的内容来判断归属
                            char_assignments[i] = 'english'
                            assigned = True
                        
                        # 对于句末标点（如问号、感叹号、句号），应该跟随它所结束的句子
                        elif char in '!?。！？':
                            # 查找前面最近的非空格字符
                            if i > 0:
                                j = i - 1
                                while j >= 0 and text[j] == ' ':
                                    j -= 1
                                if j >= 0:
                                    # 句末标点跟随前面的字符
                                    char_assignments[i] = char_assignments[j]
                                    assigned = True
                        
                        # 对于其他标点符号，根据上下文智能分配
                        if not assigned:
                            # 检查前面的字符类型
                            prev_assignment = None
                            if i > 0:
                                j = i - 1
                                while j >= 0 and text[j] == ' ':
                                    j -= 1
                                if j >= 0:
                                    prev_assignment = char_assignments[j]
                            
                            # 检查后面的字符类型
                            next_assignment = None
                            if i < len(text) - 1:
                                j = i + 1
                                while j < len(text) and text[j] == ' ':
                                    j += 1
                                if j < len(text):
                                    next_assignment = char_assignments[j] if char_assignments[j] != 'unassigned' else None
                            
                            # 分配策略
                            if prev_assignment:
                                char_assignments[i] = prev_assignment
                            elif next_assignment:
                                char_assignments[i] = next_assignment
                            else:
                                char_assignments[i] = 'chinese'
                    else:
                        # 其他字符默认分配给中文
                        char_assignments[i] = 'chinese'
            
            # 收集各语言的字符
            japanese_chars = []
            english_chars = []
            chinese_chars = []
            
            for i, assignment in enumerate(char_assignments):
                char = text[i]
                if assignment == 'japanese':
                    japanese_chars.append(char)
                elif assignment == 'english':
                    english_chars.append(char)
                elif assignment == 'chinese':
                    chinese_chars.append(char)
            
            # 合并各部分并清理空格
            japanese_text = re.sub(r'\s+', ' ', ''.join(japanese_chars)).strip()
            english_text = re.sub(r'\s+', ' ', ''.join(english_chars)).strip()
            chinese_text = re.sub(r'\s+', ' ', ''.join(chinese_chars)).strip()
            
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
        """将处理后的歌词注入音频文件标签或LRC文件"""
        # 检查是否是LRC文件
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext == '.lrc':
            return self._inject_lrc_lyrics(file_path, lyrics)
        
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
    
    def _inject_lrc_lyrics(self, file_path: str, lyrics: str) -> bool:
        """向LRC文件注入歌词"""
        try:
            # 使用UTF-8编码写入LRC文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(lyrics)
            return True
        except Exception as e:
            print(f"LRC歌词注入失败: {str(e)}")
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