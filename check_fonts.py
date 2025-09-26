import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import sys

def check_fonts():
    """检查系统可用的中文字体"""
    print("正在检查系统字体...")
    print("=" * 50)
    
    # 获取所有字体
    fonts = [f.name for f in fm.fontManager.ttflist]
    
    # 常用中文字体
    chinese_fonts = [
        'SimHei', 'Microsoft YaHei', 'SimSun', 'KaiTi', 
        'FangSong', 'YouYuan', 'LiSu', 'STXihei', 
        'STKaiti', 'STSong', 'STFangsong'
    ]
    
    print("系统中可用的中文字体:")
    available_fonts = []
    for font in chinese_fonts:
        if font in fonts:
            available_fonts.append(font)
            print(f"✓ {font}")
        else:
            print(f"✗ {font}")
    
    print("\n" + "=" * 50)
    
    if available_fonts:
        print(f"找到 {len(available_fonts)} 个可用的中文字体")
        recommended_font = available_fonts[0]
        print(f"推荐使用: {recommended_font}")
        
        # 测试字体显示
        plt.rcParams['font.sans-serif'] = [recommended_font]
        plt.rcParams['axes.unicode_minus'] = False
        
        plt.figure(figsize=(8, 6))
        plt.plot([1, 2, 3, 4], [1, 4, 2, 3], 'o-')
        plt.title('字体测试 - 中文显示')
        plt.xlabel('X轴标签')
        plt.ylabel('Y轴标签')
        plt.grid(True)
        
        try:
            plt.savefig('font_test.png', dpi=150, bbox_inches='tight')
            print(f"字体测试图片已保存为: font_test.png")
            print("如果图片中的中文正常显示，说明字体配置成功！")
        except Exception as e:
            print(f"保存测试图片时出错: {e}")
        finally:
            plt.close()
            
    else:
        print("未找到常用中文字体，程序可能无法正常显示中文")
        print("建议:")
        print("1. 在Windows系统中安装Microsoft YaHei字体")
        print("2. 或者使用英文界面")
    
    print("\n按任意键继续...")
    input()

if __name__ == "__main__":
    try:
        check_fonts()
    except Exception as e:
        print(f"字体检查过程中出错: {e}")
        print("建议直接运行主程序，程序会尝试自动配置字体")
        input("按任意键继续...")