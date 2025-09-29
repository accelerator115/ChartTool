import PyInstaller.__main__
import os

# 获取当前脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))

# 要打包的Python脚本路径
script_path = os.path.join(script_dir, 'chart_tool.py')

# PyInstaller参数
PyInstaller.__main__.run([
    script_path,
    '--name=ChartTool',
    '--onefile',  # 生成单个可执行文件
    '--windowed',  # 不显示命令行窗口
    '--icon=D:\\Desktop\\work\\ChartTool\\icon.ico',  # 使用f-string正确格式化图标路径
    '--clean',  # 清理临时文件
])

print("打包完成！EXE文件位于 dist 目录中。")