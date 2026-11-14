import pandas as pd
import os
import sys

# 检查是否安装了 matplotlib，没装会提示你
try:
    import matplotlib.pyplot as plt
except ImportError:
    print("❌ 缺少 matplotlib 库，请在终端运行：pip install matplotlib")
    sys.exit()

# 动态获取绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
data_dir = os.path.join(project_root, 'data')
reports_dir = os.path.join(project_root, 'reports')

# 强制创建 reports 文件夹
os.makedirs(reports_dir, exist_ok=True)

# 解决 Windows 中文乱码
plt.rcParams['font.sans-serif'] = ['SimHei'] 
plt.rcParams['axes.unicode_minus'] = False 

# 读取数据，检查文件是否存在
file_path = os.path.join(data_dir, 'cleaned_data.csv')
if not os.path.exists(file_path):
    print(f"❌ 找不到数据文件：{file_path}")
    print("👉 请先运行 python scripts/2_quality_check.py")
    sys.exit()

print(f"✅ 成功读取数据文件: {file_path}")
df = pd.read_csv(file_path)
df['Timestamp'] = pd.to_datetime(df['Timestamp'])

# --- 画图1：心率趋势图 ---
plt.figure(figsize=(10, 5))
plt.plot(df['Timestamp'][:100], df['Heart_Rate'][:100], marker='o', linestyle='-', color='#1f77b4', markersize=4)
plt.title("前100条数据：老人心率趋势图", fontsize=14)
plt.xlabel("时间", fontsize=12)
plt.ylabel("心率 (次/分)", fontsize=12)
plt.xticks(rotation=45) 
plt.grid(True, linestyle='--', alpha=0.6) 
plt.tight_layout() 

chart1_path = os.path.join(reports_dir, '心率趋势图.png')
plt.savefig(chart1_path, dpi=300)
plt.close() 

# --- 画图2：动作类型分布图 ---
action_counts = df['Action_Type'].value_counts()
plt.figure(figsize=(6, 6))
colors = ['#66b3ff','#99ff99','#ff9999','#ffcc99']
plt.pie(action_counts, labels=action_counts.index, autopct='%1.1f%%', colors=colors, startangle=140, textprops={'fontsize': 12})
plt.title("采集数据中的动作类型分布", fontsize=14)

chart2_path = os.path.join(reports_dir, '动作类型分布图.png')
plt.savefig(chart2_path, dpi=300)
plt.close()

print("✅ 可视化图表已生成！")
print(f"👉 请去这个路径查看图片：{reports_dir}")