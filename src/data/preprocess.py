import pandas as pd
import numpy as np
import random
import os

# 设置输出路径
output_path = os.path.join("src","data", "converted_features.csv")

# 随机生成模拟数据
num_samples = 200
random.seed(42)

data = {
    "user_id": [f"U{1000 + i}" for i in range(num_samples)],
    "device": random.choices(["Mobile", "Desktop", "Tablet"], k=num_samples),
    "country": random.choices(["US", "UK", "CN", "DE", "IN"], k=num_samples),
    "session_duration": np.random.normal(loc=30, scale=10, size=num_samples).clip(1),
}

df = pd.DataFrame(data)

# 构造访问次数（假设平均每5分钟一次）
df["num_visits"] = (df["session_duration"] // 5).astype(int).clip(lower=1)

# 构造目标变量 converted（session_duration > 25 视为转化）
df["converted"] = (df["session_duration"] > 25).astype(int)

# 重新排列列顺序
df = df[[
    "user_id",
    "converted",
    "device",
    "country",
    "num_visits",
    "session_duration"
]]

# 保存为 CSV
os.makedirs("data", exist_ok=True)
df.to_csv(output_path, index=False)
print(f"✅ 虚拟数据 saved to {output_path}, shape: {df.shape}")