import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os  # 引入os模块处理路径

# 动态获取项目根目录，彻底解决路径报错问题
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
data_dir = os.path.join(project_root, 'data')

# 如果data文件夹不存在，自动创建
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# 设置随机种子保证结果可复现
np.random.seed(42)
random.seed(42)

# 生成1000条基础数据
n = 1000
base_time = datetime(2026, 4, 1, 8, 0, 0)

# 1. 模拟元数据与硬件状态 (完全贴合JD描述)
data = {
    "Timestamp": [base_time + timedelta(seconds=i*10) for i in range(n)], # 每10秒采集一次
    "Person_ID": [f"P_{random.randint(1, 5):03d}" for _ in range(n)], # 人员编号 P_001~P_005
    "Device_ID": [f"DEV_{random.randint(1, 3):02d}" for _ in range(n)], # 设备编号 DEV_01~DEV_03
    "Action_Type": np.random.choice(["静止", "步行", "跌倒"], size=n, p=[0.5, 0.45, 0.05]), # 动作类型
    "Scene_Info": np.random.choice(["卧室", "客厅", "户外"], size=n), # 场景信息
    "Battery_Status": np.random.randint(10, 100, size=n), # 电量
    "Storage_Left_GB": np.random.uniform(1.0, 32.0, size=n).round(2), # 存储剩余空间
    "Wear_Status": ["正常"] * n, # 佩戴位置状态
    "Time_Sync": ["已同步"] * n, # 时间同步状态
    "Heart_Rate": np.random.randint(60, 100, size=n), # 心率
    "Acc_X": np.random.normal(0, 1, size=n).round(2), # 加速度X
    "Acc_Y": np.random.normal(0, 1, size=n).round(2), # 加速度Y
    "Acc_Z": np.random.normal(0, 1, size=n).round(2), # 加速度Z
}
df = pd.DataFrame(data)

# 2. 故意制造“异常”与“脏数据” (模拟真实场景)
# 异常1：设备没电断采 (电量突然掉到0)
df.loc[300:310, 'Battery_Status'] = 0
# 异常2：佩戴脱落 (心率变0，加速度变0)
df.loc[500:520, 'Wear_Status'] = "脱落"
df.loc[500:520, 'Heart_Rate'] = 0
df.loc[500:520, ['Acc_X', 'Acc_Y', 'Acc_Z']] = 0
# 异常3：时间未同步导致时间漂移/重复 (时间戳重复)
df.loc[700:710, 'Time_Sync'] = "未同步"
df.loc[705:710, 'Timestamp'] = df.loc[704, 'Timestamp'] 
# 异常4：数据缺失 (NaN)
df.loc[800:810, 'Action_Type'] = np.nan
df.loc[850:855, 'Heart_Rate'] = np.nan

# 保存原始数据 (使用拼接后的绝对路径)
save_path = os.path.join(data_dir, 'raw_data.csv')
df.to_csv(save_path, index=False, encoding="utf-8-sig")
print(f"✅ 原始脏数据已生成，保存至: {save_path}")