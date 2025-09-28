
import pandas as pd
from typing import Optional

def preprocess_data(path: str = "data/interactions.csv") -> Optional[pd.DataFrame]:
    try:
        df = pd.read_csv(path)

        # 示例：移除缺失值
        df.dropna(inplace=True)

        # 示例：转换数据类型（如有需要）
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])

        # ✅ 添加 One-Hot 编码
        df = pd.get_dummies(df, drop_first=True)

        return df
    except Exception as e:
        print(f"❌ 数据预处理失败: {e}")
        return None
