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
        self.root.title("多曲线图表工具")
        # 设置全屏窗口
        self.root.state('zoomed')  # Windows下全屏
        # self.root.attributes('-zoomed', True)  # Linux下全屏的备选方案
        
        # 多曲线数据存储
        self.curves = {}  # 存储多条曲线: {曲线名称: {'x': [], 'y': [], 'color': 'color_name', 'visible': True}}
        self.current_curve = None  # 当前选中的曲线
        self.colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
        
        # 添加一条默认曲线
        self.add_new_curve("曲线1")
        
        # 图表设置
        self.chart_title = "多曲线数据图"
        self.x_label = "X轴"
        self.y_label = "Y轴"
        
        # 设置默认字体样式
        self.default_font = ("Microsoft YaHei", 11)
        self.title_font = ("Microsoft YaHei", 14, "bold")
        
        self.setup_ui()
        
    def add_new_curve(self, name):
        """添加一条新曲线"""
        if name in self.curves:
            # 如果名称已存在，则生成一个新名称
            i = 1
            while f"{name}_{i}" in self.curves:
                i += 1
            name = f"{name}_{i}"
            
        # 选择颜色 - 循环使用颜色列表
        color_index = len(self.curves) % len(self.colors)
        
        self.curves[name] = {
            'x': [],
            'y': [],
            'color': self.colors[color_index],
            'visible': True,
            'fit_params': None  # 用于存储拟合参数
        }
        self.current_curve = name
        return name
    
    def setup_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # 左侧容器及滚动区域
        left_container = ttk.Frame(main_frame)
        left_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 15))
        
        # 创建画布和滚动条
        left_canvas = tk.Canvas(left_container, highlightthickness=0)
        left_scrollbar = ttk.Scrollbar(left_container, orient=tk.VERTICAL, command=left_canvas.yview)
        
        # 左侧数据输入区域（将放入画布中）
        left_frame = ttk.Frame(left_canvas)
        
        # 配置画布滚动
        left_canvas.configure(yscrollcommand=left_scrollbar.set)
        left_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        left_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 在画布上创建窗口以显示left_frame
        canvas_frame = left_canvas.create_window((0, 0), window=left_frame, anchor="nw", width=left_canvas.winfo_width())
        
        # 绑定事件以更新画布滚动区域
        def on_left_frame_configure(event):
            left_canvas.configure(scrollregion=left_canvas.bbox("all"))
            left_canvas.itemconfig(canvas_frame, width=left_canvas.winfo_width())
        left_frame.bind("<Configure>", on_left_frame_configure)
        
        # 绑定鼠标滚轮事件
        def _on_mousewheel(event):
            left_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        left_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # 数据输入标题
        ttk.Label(left_frame, text="数据输入", font=self.title_font).pack(pady=(0, 10))
        
        # 曲线管理面板
        curve_frame = ttk.LabelFrame(left_frame, text="曲线管理", padding=15)
        curve_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 曲线选择下拉框
        curve_select_frame = ttk.Frame(curve_frame)
        curve_select_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(curve_select_frame, text="当前曲线:", font=self.default_font).pack(side=tk.LEFT)
        self.curve_var = tk.StringVar(value=self.current_curve)
        self.curve_combo = ttk.Combobox(curve_select_frame, textvariable=self.curve_var, values=list(self.curves.keys()), 
                                      width=15, font=self.default_font)
        self.curve_combo.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        self.curve_combo.bind('<<ComboboxSelected>>', self.on_curve_selected)
        
        # 曲线管理按钮
        curve_buttons = ttk.Frame(curve_frame)
        curve_buttons.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(curve_buttons, text="添加新曲线", command=self.create_new_curve).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        ttk.Button(curve_buttons, text="删除当前曲线", command=self.delete_current_curve).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=3)
        ttk.Button(curve_buttons, text="重命名", command=self.rename_curve).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(3, 0))
        
        # 曲线可见性控制
        visibility_frame = ttk.Frame(curve_frame)
        visibility_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.visible_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(visibility_frame, text="显示当前曲线", variable=self.visible_var, 
                      command=self.toggle_curve_visibility).pack(side=tk.LEFT)
        
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
        
        # 添加拟合类型选择
        fit_type_frame = ttk.Frame(analysis_frame)
        fit_type_frame.pack(fill=tk.X, pady=(0, 8))
        
        ttk.Label(fit_type_frame, text="拟合类型:", font=self.default_font).pack(side=tk.LEFT)
        self.fit_type_var = tk.StringVar(value="linear")
        fit_type_combo = ttk.Combobox(fit_type_frame, textvariable=self.fit_type_var,
                                     values=["linear", "polynomial", "exponential", "logarithmic", "power"],
                                     width=12, font=self.default_font)
        fit_type_combo.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        
        # 多项式阶数
        self.poly_order_var = tk.StringVar(value="2")
        self.poly_order_frame = ttk.Frame(analysis_frame)
        ttk.Label(self.poly_order_frame, text="多项式阶数:", font=self.default_font).pack(side=tk.LEFT)
        poly_order_combo = ttk.Combobox(self.poly_order_frame, textvariable=self.poly_order_var,
                                       values=["2", "3", "4", "5", "6"], width=5, font=self.default_font)
        poly_order_combo.pack(side=tk.LEFT, padx=(5, 0))
        # 初始状态隐藏
        
        # 拟合参数(可选)
        self.fit_params_frame = ttk.Frame(analysis_frame)
        ttk.Label(self.fit_params_frame, text="初始参数:", font=self.default_font).pack(side=tk.LEFT)
        self.fit_params_entry = ttk.Entry(self.fit_params_frame, width=15, font=self.default_font)
        self.fit_params_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        # 初始状态隐藏
        
        # 拟合类型帮助按钮
        ttk.Button(fit_type_frame, text="?", width=2, 
                 command=self.show_fit_type_help).pack(side=tk.RIGHT, padx=(5, 0))
                 
        # 拟合类型变化时显示或隐藏相关控件
        def on_fit_type_change(event):
            if self.fit_type_var.get() == "polynomial":
                self.poly_order_frame.pack(fill=tk.X, pady=(5, 0))
                self.fit_params_frame.pack_forget()
            elif self.fit_type_var.get() in ["exponential", "logarithmic", "power"]:
                self.poly_order_frame.pack_forget()
                self.fit_params_frame.pack(fill=tk.X, pady=(5, 0))
            else:  # linear
                self.poly_order_frame.pack_forget()
                self.fit_params_frame.pack_forget()
        
        fit_type_combo.bind('<<ComboboxSelected>>', on_fit_type_change)
        
        ttk.Button(analysis_frame, text="执行曲线拟合", command=self.perform_fitting, 
                  style="Accent.TButton").pack(fill=tk.X, pady=(8, 8))
        
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
        if not self.current_curve:
            messagebox.showerror("错误", "请先选择或创建一条曲线!")
            return
            
        try:
            x = float(self.x_entry.get())
            y = float(self.y_entry.get())
            
            # 添加到当前选中的曲线
            self.curves[self.current_curve]['x'].append(x)
            self.curves[self.current_curve]['y'].append(y)
            
            self.update_data_list()
            self.update_chart()
            
            # 清空输入框
            self.x_entry.delete(0, tk.END)
            self.y_entry.delete(0, tk.END)
            
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字!")
    
    def parse_batch_data(self):
        if not self.current_curve:
            messagebox.showerror("错误", "请先选择一条曲线!")
            return
            
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
                # 添加到当前选中的曲线
                self.curves[self.current_curve]['x'].extend(new_x_data)
                self.curves[self.current_curve]['y'].extend(new_y_data)
                
                # 如果有拟合参数，清除它们 (因为数据已更改)
                if 'fit_params' in self.curves[self.current_curve]:
                    self.curves[self.current_curve]['fit_params'] = None
                    
                self.update_data_list()
                self.update_chart()
                self.batch_text.delete("1.0", tk.END)
                messagebox.showinfo("成功", f"成功添加 {len(new_x_data)} 个数据点到曲线 '{self.current_curve}'!")
            else:
                messagebox.showerror("错误", "未能解析到有效数据!")
                
        except Exception as e:
            messagebox.showerror("错误", f"数据解析失败: {str(e)}")
    
    def import_from_file(self):
        if not self.current_curve:
            messagebox.showerror("错误", "请先选择一条曲线!")
            return
            
        file_path = filedialog.askopenfilename(
            title="选择数据文件",
            filetypes=[("CSV文件", "*.csv"), ("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                # 尝试读取CSV文件
                if file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                    
                    # 检查是否有多列数据 (可能是多条曲线)
                    if len(df.columns) >= 2:
                        if len(df.columns) > 2:
                            # 显示多列导入选项对话框
                            self.show_multicolumn_import_dialog(df, file_path)
                            return
                            
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
                
                # 添加到当前选中的曲线
                self.curves[self.current_curve]['x'].extend(new_x_data)
                self.curves[self.current_curve]['y'].extend(new_y_data)
                
                # 如果有拟合参数，清除它们 (因为数据已更改)
                if 'fit_params' in self.curves[self.current_curve]:
                    self.curves[self.current_curve]['fit_params'] = None
                    
                self.update_data_list()
                self.update_chart()
                messagebox.showinfo("成功", f"成功导入 {len(new_x_data)} 个数据点到曲线 '{self.current_curve}'!")
                
            except Exception as e:
                messagebox.showerror("错误", f"文件导入失败: {str(e)}")
    
    def show_multicolumn_import_dialog(self, df, file_path):
        """处理多列数据导入"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"多列数据导入 - {os.path.basename(file_path)}")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()  # 模态对话框
        
        # 说明标签
        ttk.Label(dialog, text="检测到多列数据，请选择导入方式：", 
                font=self.default_font).pack(pady=(15, 10), padx=15, anchor=tk.W)
        
        # 框架以包含选项
        option_frame = ttk.Frame(dialog)
        option_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # 选项1: 使用第一列作为X，选择一列作为Y
        option1_frame = ttk.LabelFrame(option_frame, text="选项1: 使用第一列作为X轴数据", padding=10)
        option1_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(option1_frame, text="选择Y轴数据列:", 
                font=self.default_font).grid(row=0, column=0, sticky=tk.W, pady=5)
                
        y_column_var = tk.StringVar(value=df.columns[1])
        y_combo = ttk.Combobox(option1_frame, textvariable=y_column_var, 
                              values=df.columns.tolist()[1:], width=20, font=self.default_font)
        y_combo.grid(row=0, column=1, padx=10, pady=5)
        
        # 曲线名称
        ttk.Label(option1_frame, text="曲线名称:", 
                font=self.default_font).grid(row=1, column=0, sticky=tk.W, pady=5)
                
        curve_name_var = tk.StringVar(value=self.current_curve)
        curve_name_entry = ttk.Entry(option1_frame, textvariable=curve_name_var, 
                                   width=20, font=self.default_font)
        curve_name_entry.grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Button(option1_frame, text="导入单列", 
                 command=lambda: self.import_single_column(
                     df, df.columns[0], y_column_var.get(), curve_name_var.get(), dialog)
                ).grid(row=2, column=0, columnspan=2, pady=10)
        
        # 选项2: 导入所有Y列数据作为单独的曲线
        option2_frame = ttk.LabelFrame(option_frame, text="选项2: 导入多条曲线", padding=10)
        option2_frame.pack(fill=tk.X)
        
        ttk.Label(option2_frame, text="将第一列作为X轴，其余列分别创建曲线", 
                font=self.default_font).pack(anchor=tk.W, pady=5)
        
        ttk.Button(option2_frame, text="导入所有列为多条曲线", 
                 command=lambda: self.import_multiple_columns(df, dialog)
                ).pack(pady=10)
        
        # 取消按钮
        ttk.Button(dialog, text="取消", command=dialog.destroy).pack(pady=15)
    
    def import_single_column(self, df, x_column, y_column, curve_name, dialog):
        """导入单列数据作为一条曲线"""
        # 检查曲线名称
        if curve_name != self.current_curve and curve_name in self.curves:
            if not messagebox.askyesno("确认", f"曲线名称 '{curve_name}' 已存在。是否添加数据到该曲线?", 
                                     parent=dialog):
                return
        
        try:
            # 如果是新曲线，创建它
            if curve_name != self.current_curve and curve_name not in self.curves:
                self.add_new_curve(curve_name)
                self.curve_combo['values'] = list(self.curves.keys())
                self.curve_var.set(curve_name)
                self.current_curve = curve_name
            elif curve_name != self.current_curve:
                self.current_curve = curve_name
                self.curve_var.set(curve_name)
            
            # 获取数据
            x_data = df[x_column].tolist()
            y_data = df[y_column].tolist()
            
            # 添加数据到曲线
            self.curves[curve_name]['x'].extend(x_data)
            self.curves[curve_name]['y'].extend(y_data)
            
            # 如果有拟合参数，清除它们
            if 'fit_params' in self.curves[curve_name]:
                self.curves[curve_name]['fit_params'] = None
            
            self.update_data_list()
            self.update_chart()
            
            dialog.destroy()
            messagebox.showinfo("成功", f"成功导入 {len(x_data)} 个数据点到曲线 '{curve_name}'!")
            
        except Exception as e:
            messagebox.showerror("错误", f"导入失败: {str(e)}", parent=dialog)
    
    def import_multiple_columns(self, df, dialog):
        """导入多列数据作为多条曲线"""
        try:
            x_column = df.columns[0]
            x_data = df[x_column].tolist()
            
            imported_count = 0
            
            for i, col in enumerate(df.columns[1:], 1):
                # 为每列创建一个曲线
                curve_name = f"{col}"
                
                # 如果曲线已存在，添加后缀
                if curve_name in self.curves:
                    curve_name = f"{col}_{i}"
                
                # 创建新曲线并添加数据
                self.add_new_curve(curve_name)
                self.curves[curve_name]['x'] = x_data.copy()
                self.curves[curve_name]['y'] = df[col].tolist()
                
                imported_count += 1
            
            # 更新曲线选择下拉菜单
            self.curve_combo['values'] = list(self.curves.keys())
            
            # 如果导入了新曲线，选择第一个导入的曲线
            if imported_count > 0:
                new_curve = f"{df.columns[1]}"
                if new_curve not in self.curves:
                    new_curve = f"{df.columns[1]}_1"
                self.current_curve = new_curve
                self.curve_var.set(new_curve)
            
            self.update_data_list()
            self.update_chart()
            
            dialog.destroy()
            messagebox.showinfo("成功", f"成功导入 {imported_count} 条曲线数据!")
            
        except Exception as e:
            messagebox.showerror("错误", f"多曲线导入失败: {str(e)}", parent=dialog)
    
    def on_curve_selected(self, event=None):
        """当用户从下拉菜单选择曲线时"""
        selected = self.curve_var.get()
        if selected and selected in self.curves:
            self.current_curve = selected
            # 更新可见性复选框状态
            self.visible_var.set(self.curves[selected]['visible'])
            # 更新数据列表
            self.update_data_list()
    
    def create_new_curve(self):
        """创建新曲线对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("创建新曲线")
        dialog.geometry("300x120")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()  # 模态对话框
        
        ttk.Label(dialog, text="曲线名称:", font=self.default_font).pack(pady=(15, 5))
        
        name_var = tk.StringVar(value=f"曲线{len(self.curves) + 1}")
        name_entry = ttk.Entry(dialog, textvariable=name_var, width=20, font=self.default_font)
        name_entry.pack(pady=5, padx=20, fill=tk.X)
        name_entry.select_range(0, tk.END)
        name_entry.focus_set()
        
        def confirm():
            name = name_var.get().strip()
            if not name:
                messagebox.showerror("错误", "曲线名称不能为空!", parent=dialog)
                return
                
            # 添加新曲线
            new_name = self.add_new_curve(name)
            
            # 更新下拉菜单选项
            self.curve_combo['values'] = list(self.curves.keys())
            self.curve_var.set(new_name)
            self.update_data_list()
            
            dialog.destroy()
            
        ttk.Button(dialog, text="确定", command=confirm).pack(pady=(5, 15))
        
        # 绑定回车键
        dialog.bind('<Return>', lambda event: confirm())
    
    def delete_current_curve(self):
        """删除当前选中的曲线"""
        if not self.current_curve:
            return
            
        if len(self.curves) <= 1:
            messagebox.showwarning("警告", "至少需要保留一条曲线!")
            return
            
        if messagebox.askyesno("确认", f"确定要删除曲线 '{self.current_curve}' 吗?"):
            # 删除当前曲线
            del self.curves[self.current_curve]
            
            # 选择另一条曲线作为当前曲线
            self.current_curve = next(iter(self.curves))
            
            # 更新下拉菜单
            self.curve_combo['values'] = list(self.curves.keys())
            self.curve_var.set(self.current_curve)
            
            self.update_data_list()
            self.update_chart()
    
    def rename_curve(self):
        """重命名当前曲线"""
        if not self.current_curve:
            return
            
        dialog = tk.Toplevel(self.root)
        dialog.title("重命名曲线")
        dialog.geometry("300x120")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()  # 模态对话框
        
        ttk.Label(dialog, text="新名称:", font=self.default_font).pack(pady=(15, 5))
        
        name_var = tk.StringVar(value=self.current_curve)
        name_entry = ttk.Entry(dialog, textvariable=name_var, width=20, font=self.default_font)
        name_entry.pack(pady=5, padx=20, fill=tk.X)
        name_entry.select_range(0, tk.END)
        name_entry.focus_set()
        
        def confirm():
            new_name = name_var.get().strip()
            if not new_name:
                messagebox.showerror("错误", "曲线名称不能为空!", parent=dialog)
                return
                
            if new_name == self.current_curve:
                dialog.destroy()
                return
                
            if new_name in self.curves:
                messagebox.showerror("错误", f"名称 '{new_name}' 已被使用!", parent=dialog)
                return
                
            # 重命名曲线 - 复制数据到新名称并删除旧记录
            self.curves[new_name] = self.curves[self.current_curve]
            del self.curves[self.current_curve]
            self.current_curve = new_name
            
            # 更新下拉菜单
            self.curve_combo['values'] = list(self.curves.keys())
            self.curve_var.set(new_name)
            
            dialog.destroy()
            
        ttk.Button(dialog, text="确定", command=confirm).pack(pady=(5, 15))
        
        # 绑定回车键
        dialog.bind('<Return>', lambda event: confirm())
    
    def toggle_curve_visibility(self):
        """切换当前曲线的可见性"""
        if not self.current_curve:
            return
            
        self.curves[self.current_curve]['visible'] = self.visible_var.get()
        self.update_chart()
    
    def update_data_list(self):
        # 清空现有数据
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
        
        if not self.current_curve:
            return
            
        # 添加当前曲线的数据
        x_data = self.curves[self.current_curve]['x']
        y_data = self.curves[self.current_curve]['y']
        
        for i, (x, y) in enumerate(zip(x_data, y_data), 1):
            self.data_tree.insert('', 'end', values=(i, f"{x:.4f}", f"{y:.4f}"))
    
    def delete_selected(self):
        if not self.current_curve:
            return
            
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
        
        x_data = self.curves[self.current_curve]['x']
        y_data = self.curves[self.current_curve]['y']
        
        for index in indices_to_delete:
            if 0 <= index < len(x_data):
                del x_data[index]
                del y_data[index]
        
        self.update_data_list()
        self.update_chart()
    
    def clear_data(self):
        if not self.current_curve:
            return
            
        if messagebox.askyesno("确认", f"确定要清除曲线 '{self.current_curve}' 的所有数据吗?"):
            self.curves[self.current_curve]['x'] = []
            self.curves[self.current_curve]['y'] = []
            self.curves[self.current_curve]['fit_params'] = None
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
        
        # 检查是否有可见的曲线
        has_visible_data = False
        
        # 设置标题和标签
        self.ax.set_xlabel(self.x_label, fontsize=font_size)
        self.ax.set_ylabel(self.y_label, fontsize=font_size)
        self.ax.set_title(self.chart_title, fontsize=font_size+2, fontweight='bold')
        self.ax.grid(True, alpha=0.3)
        
        # 绘制每条可见的曲线
        for name, curve in self.curves.items():
            if curve['visible'] and curve['x'] and curve['y']:
                has_visible_data = True
                
                # 绘制数据点
                self.ax.scatter(curve['x'], curve['y'], color=curve['color'], 
                             alpha=0.7, s=50, label=f'{name} - 数据点')
                
                # 如果有拟合参数，绘制拟合线
                if curve['fit_params'] is not None:
                    fit_params = curve['fit_params']
                    fit_type = fit_params.get('type', 'linear')
                    
                    x_array = np.array(curve['x'])
                    x_fit = np.linspace(min(x_array), max(x_array), 200)  # 增加点数使曲线更平滑
                    
                    # 使用存储的拟合函数(如果有)或者根据拟合类型计算y值
                    if 'fit_func' in curve and callable(curve['fit_func']):
                        y_fit = curve['fit_func'](x_fit)
                    else:
                        # 向后兼容旧的线性拟合参数
                        if 'slope' in fit_params and 'intercept' in fit_params:
                            slope = fit_params['slope']
                            intercept = fit_params['intercept']
                            y_fit = slope * x_fit + intercept
                        else:
                            continue
                    
                    # 使用与数据点相同的颜色
                    fit_color = curve['color']
                    
                    # 根据拟合类型生成标签
                    if 'equation' in fit_params:
                        fit_label = f'{name} - 拟合: {fit_params["equation"]}'
                    else:
                        # 向后兼容
                        fit_label = f'{name} - 拟合: y = {fit_params.get("slope", 0):.4f}x + {fit_params.get("intercept", 0):.4f}'
                    
                    # 绘制拟合曲线
                    self.ax.plot(x_fit, y_fit, color=fit_color, linestyle='-', linewidth=2, label=fit_label)
        
        if not has_visible_data:
            self.ax.set_title("请添加数据点", fontsize=font_size+2, fontweight='bold')
        
        # 设置刻度标签字体大小
        self.ax.tick_params(axis='both', which='major', labelsize=font_size-1)
        
        # 添加图例 - 仅当有曲线时
        if has_visible_data:
            self.ax.legend(fontsize=font_size-1)
        
        self.canvas.draw()
    
    def perform_fitting(self):
        """执行各种曲线拟合"""
        if not self.current_curve:
            messagebox.showerror("错误", "请先选择一条曲线!")
            return
            
        curve = self.curves[self.current_curve]
        if len(curve['x']) < 2:
            messagebox.showerror("错误", "所选曲线至少需要2个数据点才能进行拟合!")
            return
            
        # 获取拟合类型
        fit_type = self.fit_type_var.get()
        
        try:
            # 转换为numpy数组
            x_array = np.array(curve['x'])
            y_array = np.array(curve['y'])
            
            # 根据拟合类型执行不同的拟合
            if fit_type == "linear":
                # 线性拟合
                slope, intercept, r_value, p_value, std_err = stats.linregress(x_array, y_array)
                
                # 生成拟合参数和方程
                params = {
                    'type': 'linear',
                    'slope': slope,
                    'intercept': intercept,
                    'r_value': r_value,
                    'p_value': p_value,
                    'std_err': std_err,
                    'equation': f"y = {slope:.6f}x + {intercept:.6f}"
                }
                
                # 用于生成拟合曲线的函数
                def fit_func(x):
                    return slope * x + intercept
                
                result_text = f"""曲线: {self.current_curve} (线性拟合)
拟合方程: {params['equation']}
相关系数 R: {r_value:.6f}
决定系数 R²: {r_value**2:.6f}
P值: {p_value:.6e}
标准误差: {std_err:.6f}
数据点数量: {len(curve['x'])}"""
                
            elif fit_type == "polynomial":
                # 多项式拟合
                try:
                    order = int(self.poly_order_var.get())
                except:
                    order = 2
                
                if order < 1:
                    order = 1
                elif order > 10:
                    order = 10
                
                # 执行多项式拟合
                coeffs = np.polyfit(x_array, y_array, order)
                p = np.poly1d(coeffs)
                
                # 计算R²
                y_fit = p(x_array)
                r_squared = 1 - np.sum((y_array - y_fit) ** 2) / np.sum((y_array - np.mean(y_array)) ** 2)
                
                # 生成多项式方程字符串表示
                equation = "y = "
                for i, coef in enumerate(coeffs):
                    power = order - i
                    if power > 1:
                        equation += f"{coef:.6f}x^{power} + "
                    elif power == 1:
                        equation += f"{coef:.6f}x + "
                    else:
                        equation += f"{coef:.6f}"
                
                # 生成拟合参数
                params = {
                    'type': 'polynomial',
                    'order': order,
                    'coeffs': coeffs.tolist(),  # 将numpy数组转换为列表以便存储
                    'r_squared': r_squared,
                    'equation': equation
                }
                
                # 用于生成拟合曲线的函数
                def fit_func(x):
                    return p(x)
                
                result_text = f"""曲线: {self.current_curve} (多项式拟合，阶数: {order})
拟合方程: {equation}
决定系数 R²: {r_squared:.6f}
数据点数量: {len(curve['x'])}"""
                
            elif fit_type == "exponential":
                # 指数拟合 y = a * exp(b * x)
                # 对数变换: ln(y) = ln(a) + b * x
                
                # 检查y值是否为正数
                if np.any(y_array <= 0):
                    messagebox.showerror("错误", "指数拟合要求所有Y值必须为正数!")
                    return
                
                # 执行对数线性回归
                log_y = np.log(y_array)
                slope, intercept, r_value, p_value, std_err = stats.linregress(x_array, log_y)
                
                # 转换回原始参数
                a = np.exp(intercept)
                b = slope
                
                # 生成拟合参数
                params = {
                    'type': 'exponential',
                    'a': a,
                    'b': b,
                    'r_value': r_value,
                    'equation': f"y = {a:.6f} * exp({b:.6f} * x)"
                }
                
                # 用于生成拟合曲线的函数
                def fit_func(x):
                    return a * np.exp(b * x)
                
                result_text = f"""曲线: {self.current_curve} (指数拟合)
拟合方程: {params['equation']}
相关系数 R: {r_value:.6f} (对数变换后)
决定系数 R²: {r_value**2:.6f} (对数变换后)
数据点数量: {len(curve['x'])}"""
                
            elif fit_type == "logarithmic":
                # 对数拟合 y = a + b * ln(x)
                
                # 检查x值是否为正数
                if np.any(x_array <= 0):
                    messagebox.showerror("错误", "对数拟合要求所有X值必须为正数!")
                    return
                
                # 计算对数x
                log_x = np.log(x_array)
                
                # 执行线性回归
                slope, intercept, r_value, p_value, std_err = stats.linregress(log_x, y_array)
                
                # 生成拟合参数
                params = {
                    'type': 'logarithmic',
                    'a': intercept,
                    'b': slope,
                    'r_value': r_value,
                    'equation': f"y = {intercept:.6f} + {slope:.6f} * ln(x)"
                }
                
                # 用于生成拟合曲线的函数
                def fit_func(x):
                    # 避免对数计算中的负数或零
                    x_safe = np.maximum(x, 1e-10)
                    return intercept + slope * np.log(x_safe)
                
                result_text = f"""曲线: {self.current_curve} (对数拟合)
拟合方程: {params['equation']}
相关系数 R: {r_value:.6f}
决定系数 R²: {r_value**2:.6f}
数据点数量: {len(curve['x'])}"""
                
            elif fit_type == "power":
                # 幂函数拟合 y = a * x^b
                # 双对数变换: log(y) = log(a) + b * log(x)
                
                # 检查x和y值是否为正数
                if np.any(x_array <= 0) or np.any(y_array <= 0):
                    messagebox.showerror("错误", "幂函数拟合要求所有X值和Y值必须为正数!")
                    return
                
                # 计算对数x和对数y
                log_x = np.log(x_array)
                log_y = np.log(y_array)
                
                # 执行线性回归
                slope, intercept, r_value, p_value, std_err = stats.linregress(log_x, log_y)
                
                # 转换回原始参数
                a = np.exp(intercept)
                b = slope
                
                # 生成拟合参数
                params = {
                    'type': 'power',
                    'a': a,
                    'b': b,
                    'r_value': r_value,
                    'equation': f"y = {a:.6f} * x^{b:.6f}"
                }
                
                # 用于生成拟合曲线的函数
                def fit_func(x):
                    # 避免计算中的负数或零
                    x_safe = np.maximum(x, 1e-10)
                    return a * np.power(x_safe, b)
                
                result_text = f"""曲线: {self.current_curve} (幂函数拟合)
拟合方程: {params['equation']}
相关系数 R: {r_value:.6f} (双对数变换后)
决定系数 R²: {r_value**2:.6f} (双对数变换后)
数据点数量: {len(curve['x'])}"""
                
            else:
                messagebox.showerror("错误", f"不支持的拟合类型: {fit_type}")
                return
            
            # 保存拟合参数和函数到曲线数据
            curve['fit_params'] = params
            curve['fit_func'] = fit_func
            
            # 更新图表
            self.update_chart()
            
            # 显示拟合结果
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert("1.0", result_text)
            
        except Exception as e:
            messagebox.showerror("错误", f"曲线拟合失败: {str(e)}")
            
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
        # 检查是否有任何可见的曲线数据
        has_data = False
        for curve in self.curves.values():
            if curve['visible'] and curve['x'] and curve['y']:
                has_data = True
                break
                
        if not has_data:
            messagebox.showerror("错误", "没有可见的曲线数据可以导出!")
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
                    
                    # 设置标题和标签
                    export_ax.set_xlabel(self.x_label, fontsize=font_size)
                    export_ax.set_ylabel(self.y_label, fontsize=font_size)
                    export_ax.set_title(self.chart_title, fontsize=font_size+2, fontweight='bold')
                    export_ax.grid(True, alpha=0.3)
                    
                    # 检查是否有可见的曲线数据
                    has_visible_data = False
                    
                    # 绘制每条可见的曲线
                    for name, curve in self.curves.items():
                        if curve['visible'] and curve['x'] and curve['y']:
                            has_visible_data = True
                            
                            # 绘制数据点
                            export_ax.scatter(curve['x'], curve['y'], color=curve['color'], 
                                         alpha=0.7, s=50, label=f'{name} - 数据点')
                            
                            # 如果有拟合参数，绘制拟合线
                            if curve['fit_params'] is not None:
                                fit_params = curve['fit_params']
                                fit_type = fit_params.get('type', 'linear')
                                
                                x_array = np.array(curve['x'])
                                x_fit = np.linspace(min(x_array), max(x_array), 200)  # 增加点数使曲线更平滑
                                
                                # 使用存储的拟合函数(如果有)或者根据拟合类型计算y值
                                if 'fit_func' in curve and callable(curve['fit_func']):
                                    y_fit = curve['fit_func'](x_fit)
                                else:
                                    # 向后兼容旧的线性拟合参数
                                    if 'slope' in fit_params and 'intercept' in fit_params:
                                        slope = fit_params['slope']
                                        intercept = fit_params['intercept']
                                        y_fit = slope * x_fit + intercept
                                    else:
                                        continue
                                
                                # 使用与数据点相同的颜色
                                fit_color = curve['color']
                                
                                # 根据拟合类型生成标签
                                if 'equation' in fit_params:
                                    fit_label = f'{name} - 拟合: {fit_params["equation"]}'
                                else:
                                    # 向后兼容
                                    fit_label = f'{name} - 拟合线: y = {fit_params.get("slope", 0):.4f}x + {fit_params.get("intercept", 0):.4f}'
                                
                                # 绘制拟合曲线
                                export_ax.plot(x_fit, y_fit, color=fit_color, linestyle='-', linewidth=2, label=fit_label)
                    
                    if not has_visible_data:
                        export_ax.set_title("无数据", fontsize=font_size+2, fontweight='bold')
                    else:
                        export_ax.legend(fontsize=font_size-1)
                    
                    export_ax.tick_params(axis='both', which='major', labelsize=font_size-1)
                    
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
        # 检查是否有任何可见的曲线数据
        has_data = False
        for curve in self.curves.values():
            if curve['visible'] and curve['x'] and curve['y']:
                has_data = True
                break
                
        if not has_data:
            messagebox.showerror("错误", "没有可见的曲线数据可以导出!")
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
                
                # 设置标题和标签
                export_ax.set_xlabel(self.x_label, fontsize=font_size)
                export_ax.set_ylabel(self.y_label, fontsize=font_size)
                export_ax.set_title(self.chart_title, fontsize=font_size+2, fontweight='bold')
                export_ax.grid(True, alpha=0.3)
                
                # 检查是否有可见的曲线数据
                has_visible_data = False
                
                # 绘制每条可见的曲线
                for name, curve in self.curves.items():
                    if curve['visible'] and curve['x'] and curve['y']:
                        has_visible_data = True
                        
                        # 绘制数据点
                        export_ax.scatter(curve['x'], curve['y'], color=curve['color'], 
                                     alpha=0.7, s=50, label=f'{name} - 数据点')
                        
                        # 如果有拟合参数，绘制拟合线
                        if curve['fit_params'] is not None:
                            fit_params = curve['fit_params']
                            fit_type = fit_params.get('type', 'linear')
                            
                            x_array = np.array(curve['x'])
                            x_fit = np.linspace(min(x_array), max(x_array), 200)  # 增加点数使曲线更平滑
                            
                            # 使用存储的拟合函数(如果有)或者根据拟合类型计算y值
                            if 'fit_func' in curve and callable(curve['fit_func']):
                                y_fit = curve['fit_func'](x_fit)
                            else:
                                # 向后兼容旧的线性拟合参数
                                if 'slope' in fit_params and 'intercept' in fit_params:
                                    slope = fit_params['slope']
                                    intercept = fit_params['intercept']
                                    y_fit = slope * x_fit + intercept
                                else:
                                    continue
                            
                            # 使用与数据点相同的颜色
                            fit_color = curve['color']
                            
                            # 根据拟合类型生成标签
                            if 'equation' in fit_params:
                                fit_label = f'{name} - 拟合: {fit_params["equation"]}'
                            else:
                                # 向后兼容
                                fit_label = f'{name} - 拟合线: y = {fit_params.get("slope", 0):.4f}x + {fit_params.get("intercept", 0):.4f}'
                            
                            # 绘制拟合曲线
                            export_ax.plot(x_fit, y_fit, color=fit_color, linestyle='-', linewidth=2, label=fit_label)
                
                if not has_visible_data:
                    export_ax.set_title("无数据", fontsize=font_size+2, fontweight='bold')
                else:
                    # 添加图例
                    export_ax.legend(fontsize=font_size-1)
                
                # 设置刻度标签字体大小
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
        """增强的数据导出功能，支持导出多条曲线"""
        # 检查是否有任何曲线数据
        has_data = False
        for curve in self.curves.values():
            if curve['x'] and curve['y']:
                has_data = True
                break
                
        if not has_data:
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
                # 创建带有所有曲线数据的DataFrame
                data_dict = {}
                
                for name, curve in self.curves.items():
                    if curve['x'] and curve['y']:
                        data_dict[f"{name}_X"] = curve['x']
                        data_dict[f"{name}_Y"] = curve['y']
                
                df = pd.DataFrame(data_dict)
                
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
        
    def show_fit_type_help(self):
        """显示拟合类型的帮助信息"""
        help_window = tk.Toplevel(self.root)
        help_window.title("曲线拟合类型帮助")
        help_window.geometry("600x500")
        help_window.resizable(True, True)
        
        # 创建文本框显示帮助信息
        help_text = tk.Text(help_window, wrap=tk.WORD, font=self.default_font, padx=15, pady=15)
        help_text.pack(fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(help_text, orient=tk.VERTICAL, command=help_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        help_text.configure(yscrollcommand=scrollbar.set)
        
        # 帮助信息内容
        help_content = """曲线拟合类型说明：

1. 线性拟合 (Linear)
   方程形式: y = ax + b
   适用情况: 数据呈现线性趋势时，如匀速运动的位移-时间关系。
   优点: 简单直观，易于理解。
   限制: 只能拟合直线关系。

2. 多项式拟合 (Polynomial)
   方程形式: y = a₀ + a₁x + a₂x² + ... + aₙxⁿ
   适用情况: 数据关系复杂，呈现多次波动趋势。
   优点: 灵活性高，可以拟合复杂曲线。
   限制: 阶数过高可能导致过拟合，建议根据数据特性选择适当阶数。
   说明: 阶数为1相当于线性拟合，阶数越高曲线越灵活。

3. 指数拟合 (Exponential)
   方程形式: y = a·eᵇˣ
   适用情况: 增长/衰减速率与当前值成正比，如放射性衰变、人口增长等。
   优点: 适合描述指数增长或衰减过程。
   限制: 要求所有y值必须为正数。

4. 对数拟合 (Logarithmic)
   方程形式: y = a + b·ln(x)
   适用情况: 随x增大，y增长速度逐渐减缓，如学习曲线等。
   优点: 适合描述初始增长迅速后逐渐趋于平缓的过程。
   限制: 要求所有x值必须为正数。

5. 幂函数拟合 (Power)
   方程形式: y = a·xᵇ
   适用情况: 在对数-对数坐标系中呈线性关系的数据，如面积与半径、物理定律等。
   优点: 适合描述某些物理和生物学关系。
   限制: 要求所有x值和y值必须为正数。

选择合适的拟合类型建议:
• 首先观察数据点分布趋势
• 尝试不同拟合类型并比较决定系数(R²)
• 结合实际物理或业务含义选择最合理的模型
• 避免过度拟合 - 最复杂的模型不一定是最好的

决定系数(R²)解释:
R²值介于0到1之间，越接近1表示模型拟合效果越好。但要注意，仅追求高R²值可能导致过拟合。
"""
        
        help_text.insert("1.0", help_content)
        help_text.config(state=tk.DISABLED)  # 设为只读
        
        # 关闭按钮
        ttk.Button(help_window, text="关闭", command=help_window.destroy).pack(pady=15)

def main():
    root = tk.Tk()
    app = ChartTool(root)
    root.mainloop()

if __name__ == "__main__":
    main()