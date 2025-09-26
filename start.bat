@echo off
chcp 65001 >nul
echo 启动线性拟合图表工具（大界面版本 - 支持标题编辑、坐标轴编辑、文件导出）...
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请确保已安装Python 3.7或更高版本
    pause
    exit /b 1
)

REM 尝试安装依赖包
echo 正在检查并安装依赖包...
pip install matplotlib numpy scipy pandas pillow openpyxl

REM 检查tkinter GUI支持
echo 正在检查图形界面支持...
python -c "import tkinter; print('GUI支持正常')" 2>nul
if errorlevel 1 (
    echo 警告: tkinter未安装，可能影响图表编辑功能
)

REM 检查字体
echo 正在检查系统字体...
python -c "import matplotlib.pyplot as plt; plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']; print('字体设置完成')" 2>nul

REM 设置环境变量优化界面
set CHART_TOOL_LARGE_UI=1
set CHART_TOOL_FONT_SIZE=14

REM 启动程序
echo.
echo 启动程序（大界面模式）...
echo 界面优化：
echo - 窗口尺寸: 1400x900 (更宽敞)
echo - 默认字体: 14号 (更清晰)
echo - 支持编辑图表标题
echo - 支持编辑X轴和Y轴标签  
echo - 支持导出PNG、PDF、SVG等高清格式
echo - 包含示例数据文件: sample_data.csv
echo.
python chart_tool.py --large-ui --font-size=14

pause