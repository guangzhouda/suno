@echo off
chcp 65001 >nul
echo.
echo ========================================
echo    AI创作平台 v2.0 启动脚本
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.10+
    pause
    exit /b 1
)

echo [1/4] 检查虚拟环境...
if not exist ".venv" (
    echo [提示] 虚拟环境不存在，正在创建...
    python -m venv .venv
    if errorlevel 1 (
        echo [错误] 创建虚拟环境失败
        pause
        exit /b 1
    )
    echo [成功] 虚拟环境创建完成
)

echo [2/4] 激活虚拟环境...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [错误] 激活虚拟环境失败
    pause
    exit /b 1
)

echo [3/4] 检查依赖...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo [提示] 正在安装依赖包...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 安装依赖失败
        pause
        exit /b 1
    )
    echo [成功] 依赖安装完成
)

echo [4/4] 检查配置文件...
if not exist "config.json" (
    echo.
    echo [警告] 未找到配置文件 config.json
    echo [提示] 请复制 config.example.json 为 config.json 并填写API密钥
    echo.
    echo 是否使用环境变量中的 SUNO_API_KEY? (Y/N)
    set /p use_env=
    if /i "%use_env%"=="Y" (
        echo [提示] 将使用环境变量配置
    ) else (
        echo [提示] 请先配置 config.json 文件
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo    正在启动AI创作平台...
echo ========================================
echo.
echo [信息] Web界面: http://localhost:8000
echo [信息] API文档: http://localhost:8000/docs
echo [信息] 健康检查: http://localhost:8000/api/health
echo.
echo [提示] 按 Ctrl+C 可停止服务器
echo.

REM 启动应用
python ai_platform.py

pause
