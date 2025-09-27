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
    '--add-data=sample_data.csv;.',  # 添加示例数据文件
    '--icon=NONE',  # 默认图标
    '--clean',  # 清理临时文件
])

print("打包完成！EXE文件位于 dist 目录中。")