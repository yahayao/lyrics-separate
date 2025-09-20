@echo off
chcp 65001 >nul
title 音频文件双语歌词处理工具

echo.
echo ===============================================
echo       音频文件双语歌词处理工具
echo ===============================================
echo.
echo 使用说明：
echo 1. 将音频文件拖拽到此批处理文件上
echo 2. 或者直接双击运行，然后输入文件/目录路径
echo 3. 程序会自动创建备份文件
echo.

set "python_exe=D:\Python\Python313\python.exe"
set "script_path=%~dp0lyrics_processor.py"

REM 检查Python是否可用
"%python_exe%" --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 找不到Python解释器
    echo 请确保Python已正确安装
    pause
    exit /b 1
)

REM 检查脚本是否存在
if not exist "%script_path%" (
    echo 错误: 找不到 lyrics_processor.py 脚本
    echo 请确保脚本文件在同一目录下
    pause
    exit /b 1
)

REM 如果有参数（拖拽文件），直接处理
if not "%~1"=="" (
    set "target_path=%~1"
    goto process
)

REM 交互式输入
echo 请选择操作模式：
echo 1. 处理单个文件
echo 2. 处理整个目录
echo 3. 预览模式（不修改文件）
echo 4. 批量处理（递归子目录）
echo.
set /p "mode=请输入选项 (1-4): "

if "%mode%"=="1" (
    set /p "target_path=请输入音频文件路径: "
    set "args="
    goto process
)

if "%mode%"=="2" (
    set /p "target_path=请输入目录路径: "
    set "args=--no-recursive"
    goto process
)

if "%mode%"=="3" (
    set /p "target_path=请输入文件或目录路径: "
    set "args=--preview"
    goto process
)

if "%mode%"=="4" (
    set /p "target_path=请输入目录路径: "
    set "args="
    goto process
)

echo 无效的选项，请重新运行
pause
exit /b 1

:process
REM 检查路径是否存在
if not exist "%target_path%" (
    echo 错误: 指定的路径不存在
    echo 路径: %target_path%
    pause
    exit /b 1
)

echo.
echo 开始处理: %target_path%
echo 参数: %args%
echo.

REM 运行Python脚本
"%python_exe%" "%script_path%" "%target_path%" %args%

echo.
echo ===============================================
echo 处理完成！
echo ===============================================
echo.
echo 注意事项：
echo 1. 已自动创建备份文件（.backup后缀）
echo 2. 如果处理出现问题，可以用备份文件恢复
echo 3. 可以删除备份文件以节省空间
echo.
pause