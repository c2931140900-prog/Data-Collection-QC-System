import pandas as pd
import numpy as np
import os # 引入os模块处理路径

# 动态获取项目根目录，彻底解决路径报错问题
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
data_dir = os.path.join(project_root, 'data')
reports_dir = os.path.join(project_root, 'reports')

# 如果 reports 文件夹不存在，自动创建
if not os.path.exists(reports_dir):
    os.makedirs(reports_dir)

# 读取原始数据 (使用绝对路径)
file_path = os.path.join(data_dir, 'raw_data.csv')
df = pd.read_csv(file_path)
df['Timestamp'] = pd.to_datetime(df['Timestamp'])

# 初始化采集异常日志列表
error_logs = []

# 1. 检查数据缺失
missing_hr = df['Heart_Rate'].isnull().sum()
missing_action = df['Action_Type'].isnull().sum()
if missing_hr > 0: error_logs.append(f"发现 {missing_hr} 条心率数据缺失 (NaN)")
if missing_action > 0: error_logs.append(f"发现 {missing_action} 条动作类型元数据缺失 (NaN)")

# 2. 检查佩戴状态异常 (脱落)
drop_off_records = df[df['Wear_Status'] == '脱落']
if len(drop_off_records) > 0:
    error_logs.append(f"发现 {len(drop_off_records)} 条设备脱落导致的无效数据 (人员:{drop_off_records['Person_ID'].iloc[0]}, 设备:{drop_off_records['Device_ID'].iloc[0]})")

# 3. 检查电量与断采
dead_battery = df[df['Battery_Status'] == 0]
if len(dead_battery) > 0:
    error_logs.append(f"发现 {len(dead_battery)} 条因低电量导致的采集中断风险数据")

# 4. 检查时间漂移/重复 (时间未同步)
time_duplicates = df[df.duplicated(subset=['Timestamp', 'Device_ID'])]
if len(time_duplicates) > 0:
    error_logs.append(f"发现 {len(time_duplicates)} 条因时间未同步导致的重复时间戳记录")

# --- 开始清洗 ---
# 剔除脱落数据
df_clean = df[df['Wear_Status'] != '脱落'].copy()
# 填充缺失值 (使用前向填充)
df_clean['Heart_Rate'] = df_clean['Heart_Rate'].ffill()
df_clean['Action_Type'] = df_clean['Action_Type'].fillna("未知")
# 去重
df_clean = df_clean.drop_duplicates(subset=['Timestamp', 'Device_ID'])

# 保存清洗后的数据 (使用绝对路径)
clean_save_path = os.path.join(data_dir, 'cleaned_data.csv')
df_clean.to_csv(clean_save_path, index=False, encoding="utf-8-sig")

# --- 生成采集异常反馈日志 ---
print("⚠️ 【采集异常反馈清单】 ⚠️")
for log in error_logs:
    print("- " + log)

# 保存日志到Excel (对应JD要求输出日志与报告)
excel_path = os.path.join(reports_dir, '采集异常反馈日志.xlsx')
with pd.ExcelWriter(excel_path) as writer:
    # 创建问题数据明细表
    problem_df = pd.DataFrame({
        "异常类型": ["佩戴脱落", "数据缺失", "时间漂移", "低电量"],
        "发生次数": [len(drop_off_records), missing_hr + missing_action, len(time_duplicates), len(dead_battery)],
        "处理方案": ["剔除无效数据", "前向填充/剔除", "去重并标记", "标记并通知维护"]
    })
    problem_df.to_excel(writer, sheet_name="异常汇总", index=False)

print(f"\n✅ 数据清洗完成！")
print(f"已生成清洗后的数据文件: {clean_save_path}")
print(f"已生成异常反馈日志: {excel_path}")