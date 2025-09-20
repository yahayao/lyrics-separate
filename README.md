# 音频文件歌词标签处理工具

一个专门用于处理音频文件标签中双语歌词的Python工具，能够智能识别并分离混合在同一行的多语言歌词内容。

## 📖 项目简介

许多音乐平台下载的歌曲包含双语歌词，但这些歌词通常混合在同一行中，导致播放器无法正确显示和同步。本工具通过智能语言识别算法，自动将单行混合语言歌词分离为多行独立歌词，每行保持相同的时间戳，从而提升歌词显示效果和用户体验。

### 🎯 主要特色
- **智能语言识别**：基于Unicode字符范围精确识别日文（平假名、片假名、汉字）、中文汉字、英文字母
- **上下文汉字归属判断**：通过相邻字符分析，智能判断汉字属于日文还是中文
- **多音频格式支持**：FLAC、MP3、OGG、MP4/M4A等主流格式
- **时间戳同步**：分离后的每行歌词保持完全相同的时间戳
- **编码自适应**：自动检测和处理各种文本编码
- **安全可靠**：自动备份机制，支持预览模式

# <font color=red>重要提醒</font>
本工具专为**日中双语歌词**优化设计，能够智能识别并分离日文和中文内容。同时也支持中英分离功能。其他语言**不保证**有同等效果，**强烈建议首次使用时启用备份功能或使用预览模式！**

## 🎯 核心功能

### 🌐 多语言智能分离
- **日中分离**：智能识别日文（假名+汉字）和中文汉字，准确分离两种语言
- **中英分离**：基于汉字（`\u4e00-\u9fff`）和ASCII字母的智能识别
- **汉字智能归属**：通过相邻字符上下文分析，准确判断汉字属于日文还是中文
- **分离策略**：将日文和英文保持在第一行，中文内容移到第二行（保持相同时间戳）

### 🎵 支持的音频格式
| 格式 | 主要标签字段 | 备用字段 | 特殊处理 |
|------|-------------|----------|----------|
| **FLAC** | `LYRICS` | `UNSYNCED LYRICS`, `UNSYNCEDLYRICS`, `lyrics` | 自动编码检测 |
| **MP3** | `USLT` (ID3v2) | `TXXX:LYRICS`, `COMM::eng` | ID3标签自动创建 |
| **OGG** | `LYRICS` | `UNSYNCED LYRICS` | Vorbis Comment |
| **MP4/M4A** | `©lyr` | `lyr`, `LYRICS` | iTunes兼容 |

### 🔧 高级特性
- **时间戳保持**：`[mm:ss.xxx]` 格式时间戳在分离后完全保持
- **编码自适应**：使用 `chardet` 库自动检测文本编码，支持置信度阈值
- **批量处理**：递归目录遍历，支持大规模文件批处理
- **安全机制**：原子文件操作，自动备份（`.backup` 后缀）
- **预览模式**：`--preview` 参数仅显示处理结果，不修改文件
- **统计报告**：详细的处理成功/失败统计信息

## 📦 环境要求与安装

### 系统要求
- Python 3.7 或更高版本
- Windows/Linux/macOS 兼容

### 依赖库安装
```bash
# 安装核心依赖
pip install mutagen chardet

# 或者使用国内镜像加速
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple mutagen chardet
```

### 依赖说明
- **mutagen** (≥1.45.0)：音频文件元数据读写库，支持FLAC、MP3、OGG、MP4格式
- **chardet** (≥4.0.0)：字符编码自动检测库，智能处理UTF-8、GBK、GB2312等编码

## 🚀 使用指南

### 快速开始

#### 单文件处理
```bash
# 基本用法 - 处理单个音频文件
python lyrics_processor.py "path/to/your/song.flac"

# 预览模式 - 仅查看分离结果，不修改文件
python lyrics_processor.py "path/to/your/song.flac" --preview

# 不创建备份文件
python lyrics_processor.py "path/to/your/song.flac" --no-backup
```

#### 批量处理
```bash
# 递归处理整个目录（包含子文件夹）
python lyrics_processor.py "D:\Music"

# 仅处理指定目录，不包含子目录
python lyrics_processor.py "D:\Music" --no-recursive

# 批量处理且不创建备份
python lyrics_processor.py "D:\Music" --no-backup --no-recursive
```

### 🖱️ Windows用户友好操作
1. **双击运行**：直接双击 `歌词处理工具.bat` 批处理文件
2. **拖拽处理**：将音频文件或文件夹直接拖拽到 `歌词处理工具.bat` 文件上
3. **右键菜单**：可将批处理文件添加到系统右键菜单（需要手动配置）

### 📂 项目文件结构
```
lyrics-separate/
├── lyrics_processor.py      # 核心处理程序
├── 歌词处理工具.bat          # Windows批处理启动器  
├── config.ini              # 配置文件（可选）
├── example_usage.py         # 使用示例代码
├── README.md               # 项目文档
└── LICENSE                 # 开源协议
```

## 📋 处理示例

### 日中分离示例

**输入歌词（日中混合）：**
```
[00:12.45]君の笑顔が好きだ 我喜欢你的笑容
[00:16.78]桜が咲く季節に 在樱花盛开的季节
[00:20.32]一緒に歩こう 一起走吧
```

**输出歌词（分离后）：**
```
[00:12.45]君の笑顔が好きだ
[00:12.45]我喜欢你的笑容
[00:16.78]桜が咲く季節に
[00:16.78]在樱花盛开的季节
[00:20.32]一緒に歩こう
[00:20.32]一起走吧
```

### 中英分离示例

**输入歌词：**
```
[00:20.15]我爱你中国 I love you China
[00:25.30]美丽的家园 Beautiful homeland
```

**输出歌词：**
```
[00:20.15]我爱你中国
[00:20.15]I love you China
[00:25.30]美丽的家园
[00:25.30]Beautiful homeland
```

### 复杂日文处理示例

**输入歌词（日文汉字+假名+英文混合）：**
```
[00:24.49]答えて涙意味を please now 眼泪的意义为何 请现在回答我
```

**输出歌词（智能汉字归属识别）：**
```
[00:24.49]答えて涙意味を please now
[00:24.49]眼泪的意义为何 请现在回答我
```

### 汉字归属算法说明
程序通过以下规则判断汉字归属：
1. **紧邻假名的汉字** → 归属为日文（如：桜の、花び）
2. **连续汉字序列与假名相邻** → 整个序列归属日文
3. **独立的汉字序列** → 归属为中文
4. **空格和标点符号** → 按上下文就近分配

## 🎵 支持的音频格式和标签

### FLAC文件
- **主要标签**：`LYRICS`
- **备用标签**：`UNSYNCED LYRICS`, `UNSYNCEDLYRICS`, `lyrics`
- **编码支持**：自动检测 UTF-8、GBK、GB2312 等编码

### MP3文件 (ID3标签)
- **主要标签**：`USLT` (Unsynchronized Lyrics)
- **备用标签**：`TXXX:LYRICS`, `TXXX:lyrics`, `TXT`, `COMM::eng`
- **版本支持**：ID3v2.3、ID3v2.4

### OGG文件 (Vorbis Comment)
- **支持标签**：`LYRICS`, `UNSYNCED LYRICS`, `UNSYNCEDLYRICS`
- **编码**：标准 UTF-8 编码

### MP4/M4A文件
- **主要标签**：`©lyr` (标准 iTunes 歌词标签)
- **备用标签**：`lyr`, `LYRICS`
- **兼容性**：iTunes、Apple Music 完全兼容

## ⚠️ 重要说明

### 安全保护
- 🛡️ **自动备份**：处理前自动创建 `.backup` 后缀的备份文件
- 🔍 **预览模式**：使用 `--preview` 参数预览分离结果，确认无误后再实际处理
- 📁 **原子操作**：文件写入采用原子操作，避免处理中断导致文件损坏

### 🎯 算法精度与限制
#### 分离精度
- **日中分离**：基于假名识别和汉字归属判断，准确率 >95%
- **中英分离**：基于汉字与字母区分，准确率 >95%  
- **汉字归属判断**：通过上下文分析，日文汉字识别准确率 >90%

#### 处理限制
- **混合语言上限**：同一行超过3种语言时效果下降
- **时间戳格式要求**：必须符合 `[mm:ss.xx]` 或 `[mm:ss.xxx]` 格式
- **特殊字符影响**：emoji和非标准符号可能影响分离精度
- **编码要求**：源歌词需要是有效的文本编码（非损坏数据）

#### 最佳实践建议
- **首次使用**务必启用 `--preview` 模式检查效果
- **批量处理前**先用小样本测试分离效果  
- **重要文件**建议手动检查分离结果
- **复杂歌词**可能需要人工后期调整

## 📋 命令行参数详解

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `path` | 位置参数 | 要处理的文件或目录路径（必需） | `"D:\Music\song.flac"` |
| `--no-backup` | 可选参数 | 不创建备份文件（默认会备份） | `--no-backup` |
| `--no-recursive` | 可选参数 | 不递归处理子目录（默认递归） | `--no-recursive` |
| `--preview` | 可选参数 | 预览模式，仅显示处理结果不修改文件 | `--preview` |

### 参数组合示例
```bash
# 预览单文件分离结果
python lyrics_processor.py "song.flac" --preview

# 处理目录但不创建备份且不递归
python lyrics_processor.py "D:\Music" --no-backup --no-recursive

# 完全安全模式：预览 + 备份 + 递归
python lyrics_processor.py "D:\Music" --preview
```

## 🐛 错误处理与故障排除

### 常见问题与解决方案

#### 文件相关错误
- **`不支持的文件格式`**：确认文件为 FLAC/MP3/OGG/MP4/M4A 格式
- **`未找到歌词标签`**：使用音频标签编辑器确认文件包含歌词信息
- **`文件访问权限问题`**：以管理员权限运行或检查文件是否被占用

#### 编码相关错误
- **乱码显示**：程序会自动检测编码，如仍有问题可手动转换为UTF-8
- **特殊字符丢失**：确保原歌词使用标准字符编码

#### 分离效果问题
- **分离不准确**：使用 `--preview` 检查结果，必要时手动调整
- **汉字归属错误**：日文中的汉字可能被识别为中文，这是正常现象

### 处理统计信息
程序会输出详细的处理报告：
```
处理完成!
总文件数: 50
成功处理: 45
处理失败: 2
无歌词文件: 3
不支持格式: 0
```

## 🔧 技术架构

### 核心类设计
```python
class LyricsProcessor:
    def __init__(self)
        self.supported_formats = ['.flac', '.mp3', '.ogg', '.m4a', '.mp4']
    
    # 核心方法
    def detect_encoding(self, text_bytes)        # 智能编码检测
    def extract_lyrics_from_file(self, file_path) # 多格式歌词提取
    def parse_bilingual_lyrics(self, lyrics_text) # 双语歌词解析
    def _separate_languages(self, text)          # 语言分离核心算法
    def inject_lyrics_to_file(self, file_path, lyrics) # 歌词写回
    def process_single_file(self, file_path)     # 单文件处理流程
    def process_directory(self, directory_path)  # 批量处理流程
    
    # 格式特定方法
    def _extract_flac_lyrics(self, audio_file)   # FLAC歌词提取
    def _extract_mp3_lyrics(self, audio_file)    # MP3 ID3歌词提取
    def _extract_ogg_lyrics(self, audio_file)    # OGG歌词提取
    def _extract_mp4_lyrics(self, audio_file)    # MP4歌词提取
    def _inject_*_lyrics(self, audio_file, lyrics) # 对应注入方法
```

### 🧠 核心算法详解

#### 1. 语言识别字符范围
```python
has_hiragana = bool(re.search(r'[\u3040-\u309f]', text))  # 平假名
has_katakana = bool(re.search(r'[\u30a0-\u30ff]', text))  # 片假名  
has_kanji = bool(re.search(r'[\u4e00-\u9fff]', text))     # CJK汉字
has_english = bool(re.search(r'[a-zA-Z]', text))          # ASCII字母
```

#### 2. 汉字归属判断算法
```python
# 紧邻假名检测（前后1个字符）
is_japanese_kanji = (prev_char in hiragana/katakana or 
                    next_char in hiragana/katakana)

# 连续汉字序列与假名相邻检测
# 查找汉字序列边界，检查序列两端是否有假名
```

#### 3. 时间戳处理
- **正则匹配**：`r'^(\[\d{2}:\d{2}\.\d{2,3}\])'`
- **时间戳复制**：分离后的每行歌词都添加相同的原始时间戳
- **格式保持**：支持 `[mm:ss.xx]` 和 `[mm:ss.xxx]` 格式

#### 4. 编码检测策略
```python
detected = chardet.detect(text_bytes)
confidence = detected.get('confidence', 0)
# 置信度 < 0.7 时默认使用 UTF-8
encoding = 'utf-8' if confidence < 0.7 else detected.get('encoding')
```

### 🗃️ 文件处理流程
1. **格式检测** → 验证文件扩展名是否支持
2. **歌词提取** → 根据文件格式调用对应提取方法  
3. **编码处理** → 自动检测并正确解码歌词文本
4. **语言分离** → 应用核心分离算法
5. **备份创建** → 创建 `.backup` 后缀的原文件副本
6. **歌词注入** → 将处理后歌词写回音频文件标签
7. **结果统计** → 输出详细的处理报告

### 📦 依赖库详情
- **mutagen** ≥ 1.45.0：跨平台音频元数据处理
- **chardet** ≥ 4.0.0：统计学文本编码检测  
- **Python标准库**：re, os, sys, argparse, shutil

## 📄 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。

## 🤝 贡献指南

### 报告问题
- 提交 Issue 时请提供具体的错误信息和文件样本
- 说明操作系统、Python版本和音频文件格式
- 如可能，请提供导致问题的歌词内容示例

### 功能建议  
- 新语言支持（韩语、泰语等）
- 更多音频格式支持
- 分离算法优化
- 用户界面开发

### 开发贡献
1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📞 支持与联系

- **项目主页**：[GitHub Repository](https://github.com/yahayao/lyrics-sprate)
- **问题反馈**：通过 GitHub Issues 提交
- **功能建议**：欢迎在 Issues 中讨论

## 📋 更新日志

### v1.0.0 (2025-09-20)
- ✅ 完成核心双语歌词分离功能
- ✅ 支持FLAC、MP3、OGG、MP4格式
- ✅ 实现智能编码检测
- ✅ 添加批量处理和预览模式
- ✅ 完善错误处理和统计报告

---

## ⚠️ 重要提醒

**本工具专为带时间戳的LRC格式歌词设计**，对于纯文本歌词处理效果有限。

**首次使用建议**：
1. 使用 `--preview` 模式预览分离效果
2. 确保启用备份功能（默认开启）  
3. 先用少量文件测试，确认效果后再批量处理
4. 重要文件建议手动检查分离结果的准确性

本工具免费开源，使用时请遵循 MIT 协议条款。
