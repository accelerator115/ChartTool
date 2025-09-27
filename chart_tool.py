import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.font_manager as fm
import numpy as np
from scipy import stats
import pandas as pd
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class ChartTool:
    def __init__(self, root):
        self.root = root
        self.root.title("线性拟合图表工具")
        # 设置全屏窗口
        self.root.state('zoomed')  # Windows下全屏
        # self.root.attributes('-zoomed', True)  # Linux下全屏的备选方案
        
        # 数据存储
        self.x_data = []
        self.y_data = []
        
        # 图表设置
        self.chart_title = "数据点分布图"
        self.x_label = "X轴"
        self.y_label = "Y轴"
        
        # 设置默认字体样式
        self.default_font = ("Microsoft YaHei", 11)
        self.title_font = ("Microsoft YaHei", 14, "bold")
        
        self.setup_ui()
        
    def setup_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # 左侧数据输入区域
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 15))
        
        # 数据输入标题
        ttk.Label(left_frame, text="数据输入", font=self.title_font).pack(pady=(0, 10))
        
        # 单点数据输入
        input_frame = ttk.LabelFrame(left_frame, text="单点数据输入", padding=15)
        input_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(input_frame, text="X坐标:", font=self.default_font).grid(row=0, column=0, sticky=tk.W, pady=3)
        self.x_entry = ttk.Entry(input_frame, width=18, font=self.default_font)
        self.x_entry.grid(row=0, column=1, padx=(8, 0), pady=3)
        
        ttk.Label(input_frame, text="Y坐标:", font=self.default_font).grid(row=1, column=0, sticky=tk.W, pady=3)
        self.y_entry = ttk.Entry(input_frame, width=18, font=self.default_font)
        self.y_entry.grid(row=1, column=1, padx=(8, 0), pady=3)
        
        add_btn = ttk.Button(input_frame, text="添加数据点", command=self.add_point)
        add_btn.grid(row=2, column=0, columnspan=2, pady=(15, 0), sticky=tk.EW)
        
        # 批量数据输入
        batch_frame = ttk.LabelFrame(left_frame, text="批量数据输入", padding=15)
        batch_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        ttk.Label(batch_frame, text="格式: x1,y1;x2,y2;x3,y3...", font=self.default_font).pack(anchor=tk.W)
        ttk.Label(batch_frame, text="或每行一个数据点 (x y)", font=self.default_font).pack(anchor=tk.W)
        
        self.batch_text = tk.Text(batch_frame, height=10, width=30, font=self.default_font)
        self.batch_text.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
        
        batch_buttons = ttk.Frame(batch_frame)
        batch_buttons.pack(fill=tk.X, pady=(8, 0))
        
        ttk.Button(batch_buttons, text="解析数据", command=self.parse_batch_data).pack(side=tk.LEFT)
        ttk.Button(batch_buttons, text="从文件导入", command=self.import_from_file).pack(side=tk.RIGHT)
        
        # 数据列表
        list_frame = ttk.LabelFrame(left_frame, text="当前数据", padding=15)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建树形视图显示数据
        columns = ('序号', 'X', 'Y')
        self.data_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        
        for col in columns:
            self.data_tree.heading(col, text=col)
            self.data_tree.column(col, width=80)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.data_tree.yview)
        self.data_tree.configure(yscrollcommand=scrollbar.set)
        
        self.data_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 控制按钮
        control_frame = ttk.Frame(left_frame)
        control_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Button(control_frame, text="清除所有数据", command=self.clear_data).pack(side=tk.LEFT)
        ttk.Button(control_frame, text="删除选中", command=self.delete_selected).pack(side=tk.RIGHT)
        
        # 图表设置
        chart_settings_frame = ttk.LabelFrame(left_frame, text="图表设置", padding=15)
        chart_settings_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Label(chart_settings_frame, text="图表标题:", font=self.default_font).grid(row=0, column=0, sticky=tk.W, pady=3)
        self.title_entry = ttk.Entry(chart_settings_frame, width=25, font=self.default_font)
        self.title_entry.insert(0, self.chart_title)
        self.title_entry.bind('<KeyRelease>', self.on_title_change)
        self.title_entry.grid(row=0, column=1, padx=(8, 0), pady=3, sticky=tk.EW)
        
        ttk.Label(chart_settings_frame, text="X轴标签:", font=self.default_font).grid(row=1, column=0, sticky=tk.W, pady=3)
        self.xlabel_entry = ttk.Entry(chart_settings_frame, width=25, font=self.default_font)
        self.xlabel_entry.insert(0, self.x_label)
        self.xlabel_entry.bind('<KeyRelease>', self.on_xlabel_change)
        self.xlabel_entry.grid(row=1, column=1, padx=(8, 0), pady=3, sticky=tk.EW)
        
        ttk.Label(chart_settings_frame, text="Y轴标签:", font=self.default_font).grid(row=2, column=0, sticky=tk.W, pady=3)
        self.ylabel_entry = ttk.Entry(chart_settings_frame, width=25, font=self.default_font)
        self.ylabel_entry.insert(0, self.y_label)
        self.ylabel_entry.bind('<KeyRelease>', self.on_ylabel_change)
        self.ylabel_entry.grid(row=2, column=1, padx=(8, 0), pady=3, sticky=tk.EW)
        
        # 添加字体大小设置
        ttk.Label(chart_settings_frame, text="字体大小:", font=self.default_font).grid(row=3, column=0, sticky=tk.W, pady=3)
        self.font_size_var = tk.StringVar(value="14")  # 默认字体大小改为14
        font_size_combo = ttk.Combobox(chart_settings_frame, textvariable=self.font_size_var, 
                                     values=["10", "12", "14", "16", "18", "20", "22", "24"], width=22,
                                     font=self.default_font)
        font_size_combo.bind('<<ComboboxSelected>>', self.on_font_size_change)
        font_size_combo.grid(row=3, column=1, padx=(8, 0), pady=3, sticky=tk.EW)
        
        chart_settings_frame.columnconfigure(1, weight=1)
        
        # 重置按钮
        reset_btn = ttk.Button(chart_settings_frame, text="重置标签", command=self.reset_labels)
        reset_btn.grid(row=4, column=0, columnspan=2, pady=(15, 0), sticky=tk.EW)
        
        # 分析控制
        analysis_frame = ttk.LabelFrame(left_frame, text="分析控制", padding=15)
        analysis_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Button(analysis_frame, text="执行线性拟合", command=self.perform_fitting, 
                  style="Accent.TButton").pack(fill=tk.X, pady=(0, 8))
        
        # 保存按钮组 - 增强导出功能
        save_frame = ttk.Frame(analysis_frame)
        save_frame.pack(fill=tk.X, pady=(8, 0))
        
        ttk.Button(save_frame, text="导出图片", command=self.export_image).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        ttk.Button(save_frame, text="导出数据", command=self.export_data).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(3, 0))
        
        # 添加快速导出按钮
        quick_export_frame = ttk.Frame(analysis_frame)
        quick_export_frame.pack(fill=tk.X, pady=(8, 0))
        
        ttk.Button(quick_export_frame, text="PNG高清", command=lambda: self.quick_export('png')).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        ttk.Button(quick_export_frame, text="PDF矢量", command=lambda: self.quick_export('pdf')).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(2, 2))
        ttk.Button(quick_export_frame, text="SVG矢量", command=lambda: self.quick_export('svg')).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(2, 0))
        
        # 右侧图表区域
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 图表标题
        ttk.Label(right_frame, text="图表显示", font=self.title_font).pack(pady=(0, 15))
        
        # 创建matplotlib图形 - 增大默认尺寸
        self.fig, self.ax = plt.subplots(figsize=(12, 9))
        self.canvas = FigureCanvasTkAgg(self.fig, right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 结果显示区域
        result_frame = ttk.LabelFrame(right_frame, text="拟合结果", padding=15)
        result_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.result_text = tk.Text(result_frame, height=5, wrap=tk.WORD, font=self.default_font)
        self.result_text.pack(fill=tk.X)
        
        # 初始化图表
        self.update_chart()
        
    def add_point(self):
        try:
            x = float(self.x_entry.get())
            y = float(self.y_entry.get())
            
            self.x_data.append(x)
            self.y_data.append(y)
            
            self.update_data_list()
            self.update_chart()
            
            # 清空输入框
            self.x_entry.delete(0, tk.END)
            self.y_entry.delete(0, tk.END)
            
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字!")
    
    def parse_batch_data(self):
        text = self.batch_text.get("1.0", tk.END).strip()
        if not text:
            return
            
        try:
            # 尝试不同的解析格式
            lines = text.split('\n')
            new_x_data = []
            new_y_data = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # 尝试分号分隔的格式
                if ';' in line:
                    pairs = line.split(';')
                    for pair in pairs:
                        if ',' in pair:
                            x, y = pair.split(',')
                            new_x_data.append(float(x.strip()))
                            new_y_data.append(float(y.strip()))
                # 尝试空格或逗号分隔的格式
                elif ',' in line:
                    x, y = line.split(',', 1)
                    new_x_data.append(float(x.strip()))
                    new_y_data.append(float(y.strip()))
                elif ' ' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        new_x_data.append(float(parts[0]))
                        new_y_data.append(float(parts[1]))
            
            if new_x_data and new_y_data:
                self.x_data.extend(new_x_data)
                self.y_data.extend(new_y_data)
                self.update_data_list()
                self.update_chart()
                self.batch_text.delete("1.0", tk.END)
                messagebox.showinfo("成功", f"成功添加 {len(new_x_data)} 个数据点!")
            else:
                messagebox.showerror("错误", "未能解析到有效数据!")
                
        except Exception as e:
            messagebox.showerror("错误", f"数据解析失败: {str(e)}")
    
    def import_from_file(self):
        file_path = filedialog.askopenfilename(
            title="选择数据文件",
            filetypes=[("CSV文件", "*.csv"), ("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                # 尝试读取CSV文件
                if file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                    if len(df.columns) >= 2:
                        new_x_data = df.iloc[:, 0].tolist()
                        new_y_data = df.iloc[:, 1].tolist()
                    else:
                        messagebox.showerror("错误", "CSV文件至少需要两列数据!")
                        return
                else:
                    # 读取文本文件
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    self.batch_text.delete("1.0", tk.END)
                    self.batch_text.insert("1.0", content)
                    self.parse_batch_data()
                    return
                
                self.x_data.extend(new_x_data)
                self.y_data.extend(new_y_data)
                self.update_data_list()
                self.update_chart()
                messagebox.showinfo("成功", f"成功导入 {len(new_x_data)} 个数据点!")
                
            except Exception as e:
                messagebox.showerror("错误", f"文件导入失败: {str(e)}")
    
    def update_data_list(self):
        # 清空现有数据
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
        
        # 添加新数据
        for i, (x, y) in enumerate(zip(self.x_data, self.y_data), 1):
            self.data_tree.insert('', 'end', values=(i, f"{x:.4f}", f"{y:.4f}"))
    
    def delete_selected(self):
        selected_items = self.data_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请先选择要删除的数据点!")
            return
        
        # 获取选中项的索引
        indices_to_delete = []
        for item in selected_items:
            index = int(self.data_tree.item(item)['values'][0]) - 1
            indices_to_delete.append(index)
        
        # 按降序排序，从后往前删除
        indices_to_delete.sort(reverse=True)
        for index in indices_to_delete:
            del self.x_data[index]
            del self.y_data[index]
        
        self.update_data_list()
        self.update_chart()
    
    def clear_data(self):
        if messagebox.askyesno("确认", "确定要清除所有数据吗?"):
            self.x_data.clear()
            self.y_data.clear()
            self.update_data_list()
            self.update_chart()
            self.result_text.delete("1.0", tk.END)
    
    def update_chart_labels(self):
        """更新图表标题和坐标轴标签"""
        self.chart_title = self.title_entry.get()
        self.x_label = self.xlabel_entry.get()
        self.y_label = self.ylabel_entry.get()
        self.update_chart()
    
    def update_chart(self):
        self.ax.clear()
        
        # 获取字体大小
        font_size = int(self.font_size_var.get())
        
        if self.x_data and self.y_data:
            # 绘制数据点
            self.ax.scatter(self.x_data, self.y_data, color='blue', alpha=0.7, s=50, label='数据点')
            
            # 设置图表标题和标签
            self.ax.set_xlabel(self.x_label, fontsize=font_size)
            self.ax.set_ylabel(self.y_label, fontsize=font_size)
            self.ax.set_title(self.chart_title, fontsize=font_size+2, fontweight='bold')
            self.ax.grid(True, alpha=0.3)
            self.ax.legend(fontsize=font_size-1)
        else:
            self.ax.set_xlabel(self.x_label, fontsize=font_size)
            self.ax.set_ylabel(self.y_label, fontsize=font_size)
            self.ax.set_title("请添加数据点", fontsize=font_size+2, fontweight='bold')
            self.ax.grid(True, alpha=0.3)
        
        # 设置刻度标签字体大小
        self.ax.tick_params(axis='both', which='major', labelsize=font_size-1)
        
        self.canvas.draw()
    
    def perform_fitting(self):
        if len(self.x_data) < 2:
            messagebox.showerror("错误", "至少需要2个数据点才能进行线性拟合!")
            return
        
        try:
            # 转换为numpy数组
            x_array = np.array(self.x_data)
            y_array = np.array(self.y_data)
            
            # 执行线性回归
            slope, intercept, r_value, p_value, std_err = stats.linregress(x_array, y_array)
            
            # 生成拟合线数据
            x_fit = np.linspace(min(x_array), max(x_array), 100)
            y_fit = slope * x_fit + intercept
            
            # 获取字体大小
            font_size = int(self.font_size_var.get())
            
            # 更新图表
            self.ax.clear()
            self.ax.scatter(self.x_data, self.y_data, color='blue', alpha=0.7, s=50, label='数据点')
            self.ax.plot(x_fit, y_fit, 'r-', linewidth=2, label=f'拟合线: y = {slope:.4f}x + {intercept:.4f}')
            
            self.ax.set_xlabel(self.x_label, fontsize=font_size)
            self.ax.set_ylabel(self.y_label, fontsize=font_size)
            self.ax.set_title(f'{self.chart_title}', fontsize=font_size+2, fontweight='bold')
            self.ax.grid(True, alpha=0.3)
            self.ax.legend(fontsize=font_size-1)
            self.ax.tick_params(axis='both', which='major', labelsize=font_size-1)
            
            self.canvas.draw()
            
            # 标记已执行拟合
            self._fitting_performed = True
            self._slope = slope
            self._intercept = intercept
            self._r_value = r_value
            
            # 显示拟合结果
            result_text = f"""拟合方程: y = {slope:.6f}x + {intercept:.6f}
相关系数 R: {r_value:.6f}
决定系数 R²: {r_value**2:.6f}
P值: {p_value:.6e}
标准误差: {std_err:.6f}
数据点数量: {len(self.x_data)}"""
            
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert("1.0", result_text)
            
        except Exception as e:
            messagebox.showerror("错误", f"线性拟合失败: {str(e)}")
    
    def export_image(self):
        """增强的图片导出功能"""
        if not self.x_data:
            messagebox.showerror("错误", "没有数据可以导出!")
            return
        
        # 创建导出设置窗口 - 增大窗口尺寸
        export_window = tk.Toplevel(self.root)
        export_window.title("导出图片设置")
        export_window.geometry("500x450")  # 增大窗口尺寸
        export_window.resizable(True, True)  # 允许调整窗口大小
        
        # 创建主滚动区域
        main_canvas = tk.Canvas(export_window)
        scrollbar = ttk.Scrollbar(export_window, orient="vertical", command=main_canvas.yview)
        
        # 创建框架以包含所有设置
        settings_frame = ttk.Frame(main_canvas)
        
        # 配置画布滚动
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # 打包滚动条和画布
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 在画布上创建窗口以显示设置框架
        canvas_frame = main_canvas.create_window((0, 0), window=settings_frame, anchor="nw")
        
        # 配置画布大小随窗口调整
        def configure_canvas(event):
            main_canvas.itemconfig(canvas_frame, width=event.width)
        main_canvas.bind('<Configure>', configure_canvas)
        
        # 更新画布滚动区域
        def on_frame_configure(event):
            main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        settings_frame.bind("<Configure>", on_frame_configure)
        
        # 绑定鼠标滚轮事件
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # 文件格式选择
        format_frame = ttk.LabelFrame(settings_frame, text="文件格式", padding=15)
        format_frame.pack(fill=tk.X, padx=15, pady=10)
        
        format_var = tk.StringVar(value="png")
        formats = [("PNG图片 (推荐)", "png"), ("JPG图片", "jpg"), ("SVG矢量图", "svg"), ("PDF文件", "pdf")]
        
        for text, value in formats:
            # 使用 tk.Radiobutton 而不是 ttk.Radiobutton 以支持字体设置
            tk.Radiobutton(format_frame, text=text, variable=format_var, value=value, 
                          font=self.default_font, bg=export_window.cget('bg')).pack(anchor=tk.W, pady=2)
        
        # 质量设置
        quality_frame = ttk.LabelFrame(settings_frame, text="图片质量", padding=15)
        quality_frame.pack(fill=tk.X, padx=15, pady=10)
        
        ttk.Label(quality_frame, text="DPI (分辨率):", font=self.default_font).pack(anchor=tk.W)
        dpi_var = tk.StringVar(value="300")
        dpi_combo = ttk.Combobox(quality_frame, textvariable=dpi_var, 
                               values=["150", "300", "600", "1200"], width=15, font=self.default_font)
        dpi_combo.pack(anchor=tk.W, pady=5)
        
        # 尺寸设置
        size_frame = ttk.LabelFrame(settings_frame, text="图片尺寸", padding=15)
        size_frame.pack(fill=tk.X, padx=15, pady=10)
        
        ttk.Label(size_frame, text="宽度 (英寸):", font=self.default_font).grid(row=0, column=0, sticky=tk.W, pady=3)
        width_var = tk.StringVar(value="12")  # 增大默认尺寸
        ttk.Entry(size_frame, textvariable=width_var, width=12, font=self.default_font).grid(row=0, column=1, padx=8, pady=3)
        
        ttk.Label(size_frame, text="高度 (英寸):", font=self.default_font).grid(row=1, column=0, sticky=tk.W, pady=3)
        height_var = tk.StringVar(value="9")  # 增大默认尺寸
        ttk.Entry(size_frame, textvariable=height_var, width=12, font=self.default_font).grid(row=1, column=1, padx=8, pady=3)
        
        # 按钮
        button_frame = ttk.Frame(settings_frame)
        button_frame.pack(fill=tk.X, padx=15, pady=15)
        
        def do_export():
            try:
                file_format = format_var.get()
                dpi = int(dpi_var.get())
                width = float(width_var.get())
                height = float(height_var.get())
                
                # 选择保存位置
                file_path = filedialog.asksaveasfilename(
                    title="导出图片",
                    defaultextension=f".{file_format}",
                    filetypes=[(f"{file_format.upper()}文件", f"*.{file_format}"), ("所有文件", "*.*")]
                )
                
                if file_path:
                    # 创建新的图形用于导出
                    export_fig, export_ax = plt.subplots(figsize=(width, height))
                    
                    # 获取当前字体大小
                    font_size = int(self.font_size_var.get())
                    
                    # 重新绘制图表内容到导出图形
                    if self.x_data and self.y_data:
                        # 绘制数据点
                        export_ax.scatter(self.x_data, self.y_data, color='blue', alpha=0.7, s=50, label='数据点')
                        
                        # 如果有拟合线，也要绘制
                        if hasattr(self, '_fitting_performed') and self._fitting_performed:
                            try:
                                # 使用已保存的拟合参数
                                x_array = np.array(self.x_data)
                                x_fit = np.linspace(min(x_array), max(x_array), 100)
                                y_fit = self._slope * x_fit + self._intercept
                                
                                export_ax.plot(x_fit, y_fit, 'r-', linewidth=2, 
                                             label=f'拟合线: y = {self._slope:.4f}x + {self._intercept:.4f}')
                                export_ax.set_title(f'{self.chart_title} - 线性拟合结果', 
                                                   fontsize=font_size+2, fontweight='bold')
                            except:
                                export_ax.set_title(self.chart_title, fontsize=font_size+2, fontweight='bold')
                        else:
                            export_ax.set_title(self.chart_title, fontsize=font_size+2, fontweight='bold')
                        
                        # 设置标签和样式
                        export_ax.set_xlabel(self.x_label, fontsize=font_size)
                        export_ax.set_ylabel(self.y_label, fontsize=font_size)
                        export_ax.grid(True, alpha=0.3)
                        export_ax.legend(fontsize=font_size-1)
                        export_ax.tick_params(axis='both', which='major', labelsize=font_size-1)
                    else:
                        export_ax.set_xlabel(self.x_label, fontsize=font_size)
                        export_ax.set_ylabel(self.y_label, fontsize=font_size)
                        export_ax.set_title("无数据", fontsize=font_size+2, fontweight='bold')
                        export_ax.grid(True, alpha=0.3)
                    
                    # 调整布局
                    export_fig.tight_layout()
                    
                    # 保存图片
                    export_fig.savefig(
                        file_path, 
                        format=file_format,
                        dpi=dpi, 
                        bbox_inches='tight', 
                        facecolor='white',
                        edgecolor='none',
                        transparent=False
                    )
                    
                    # 关闭导出图形，释放内存
                    plt.close(export_fig)
                    
                    export_window.destroy()
                    messagebox.showinfo("成功", f"图片已导出到:\n{file_path}")
                    
            except Exception as e:
                messagebox.showerror("错误", f"导出失败: {str(e)}")
        
        ttk.Button(button_frame, text="导出", command=do_export).pack(side=tk.RIGHT, padx=8)
        ttk.Button(button_frame, text="取消", command=export_window.destroy).pack(side=tk.RIGHT)

    def quick_export(self, format_type):
        """快速导出指定格式"""
        if not self.x_data:
            messagebox.showerror("错误", "没有数据可以导出!")
            return
        
        # 生成默认文件名
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"chart_{timestamp}.{format_type}"
        
        file_path = filedialog.asksaveasfilename(
            title=f"快速导出{format_type.upper()}",
            initialfile=default_name,  # 修正参数名
            defaultextension=f".{format_type}",
            filetypes=[(f"{format_type.upper()}文件", f"*.{format_type}"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                # 根据格式设置不同的参数
                if format_type == 'png':
                    dpi = 300
                elif format_type == 'pdf':
                    dpi = 300
                elif format_type == 'svg':
                    dpi = 72
                
                # 创建新的图形用于导出
                export_fig, export_ax = plt.subplots(figsize=(12, 9))
                
                # 获取当前字体大小
                font_size = int(self.font_size_var.get())
                
                # 重新绘制图表内容
                if self.x_data and self.y_data:
                    # 绘制数据点
                    export_ax.scatter(self.x_data, self.y_data, color='blue', alpha=0.7, s=50, label='数据点')
                    
                    # 如果有拟合线，也要绘制
                    if hasattr(self, '_fitting_performed') and self._fitting_performed:
                        try:
                            # 使用已保存的拟合参数
                            x_array = np.array(self.x_data)
                            x_fit = np.linspace(min(x_array), max(x_array), 100)
                            y_fit = self._slope * x_fit + self._intercept
                            
                            export_ax.plot(x_fit, y_fit, 'r-', linewidth=2, 
                                         label=f'拟合线: y = {self._slope:.4f}x + {self._intercept:.4f}')
                            export_ax.set_title(f'{self.chart_title}', 
                                               fontsize=font_size+2, fontweight='bold')
                        except:
                            export_ax.set_title(self.chart_title, fontsize=font_size+2, fontweight='bold')
                    else:
                        export_ax.set_title(self.chart_title, fontsize=font_size+2, fontweight='bold')
                    
                    # 设置标签和样式
                    export_ax.set_xlabel(self.x_label, fontsize=font_size)
                    export_ax.set_ylabel(self.y_label, fontsize=font_size)
                    export_ax.grid(True, alpha=0.3)
                    export_ax.legend(fontsize=font_size-1)
                    export_ax.tick_params(axis='both', which='major', labelsize=font_size-1)
                
                # 调整布局
                export_fig.tight_layout()
                
                # 保存图片
                export_fig.savefig(
                    file_path, 
                    format=format_type,
                    dpi=dpi, 
                    bbox_inches='tight', 
                    facecolor='white',
                    edgecolor='none'
                )
                
                # 关闭导出图形，释放内存
                plt.close(export_fig)
                
                messagebox.showinfo("成功", f"{format_type.upper()}文件已导出到:\n{file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"导出失败: {str(e)}")

    def export_data(self):
        """增强的数据导出功能"""
        if not self.x_data:
            messagebox.showerror("错误", "没有数据可以导出!")
            return
        
        # 生成默认文件名
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"data_{timestamp}.csv"
        
        file_path = filedialog.asksaveasfilename(
            title="导出数据",
            initialfile=default_name,  # 修正参数名
            defaultextension=".csv",
            filetypes=[
                ("CSV文件", "*.csv"), 
                ("Excel文件", "*.xlsx"),
                ("文本文件", "*.txt"), 
                ("JSON文件", "*.json"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            try:
                df = pd.DataFrame({
                    self.x_label: self.x_data,
                    self.y_label: self.y_data
                })
                
                if file_path.endswith('.csv'):
                    df.to_csv(file_path, index=False, encoding='utf-8-sig')
                elif file_path.endswith('.xlsx'):
                    df.to_excel(file_path, index=False)
                elif file_path.endswith('.json'):
                    df.to_json(file_path, orient='records', indent=2)
                else:
                    # 保存为文本文件
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(f"{self.x_label}\t{self.y_label}\n")
                        for x, y in zip(self.x_data, self.y_data):
                            f.write(f"{x}\t{y}\n")
                
                messagebox.showinfo("成功", f"数据已导出到:\n{file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"导出失败: {str(e)}")

    # 新增实时更新方法
    def on_title_change(self, event):
        """标题实时更新"""
        self.chart_title = self.title_entry.get()
        self.update_chart()
    
    def on_xlabel_change(self, event):
        """X轴标签实时更新"""
        self.x_label = self.xlabel_entry.get()
        self.update_chart()
    
    def on_ylabel_change(self, event):
        """Y轴标签实时更新"""
        self.y_label = self.ylabel_entry.get()
        self.update_chart()
    
    def on_font_size_change(self, event):
        """字体大小变化"""
        self.update_chart()
    
    def reset_labels(self):
        """重置所有标签到默认值"""
        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, "数据点分布图")
        self.xlabel_entry.delete(0, tk.END)
        self.xlabel_entry.insert(0, "X轴")
        self.ylabel_entry.delete(0, tk.END)
        self.ylabel_entry.insert(0, "Y轴")
        self.font_size_var.set("14")  # 默认字体大小改为14
        self.update_chart_labels()

def main():
    root = tk.Tk()
    app = ChartTool(root)
    root.mainloop()

if __name__ == "__main__":
    main()