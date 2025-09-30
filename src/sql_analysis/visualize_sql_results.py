# src/sql_analysis/visualize_sql_results.py

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
import os

# ✅ 用 SQLAlchemy 建立连接
user = "root"
password = "Zzp990812"  # ❗修改为你的 MySQL 密码
host = "localhost"
port = 3306
database = "ecommerce_db"

engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}")

# ✅ 准备查询语句
queries = {
    'Device Conversion Rate': '''
        SELECT device, ROUND(SUM(converted) / COUNT(*), 4) AS conversion_rate
        FROM converted_features
        GROUP BY device
    ''',
    'Country Conversion Rate': '''
        SELECT country, ROUND(SUM(converted) / COUNT(*), 4) AS conversion_rate
        FROM converted_features
        GROUP BY country
    ''',
    'Visit Segment Conversion Rate': '''
        SELECT 
            CASE 
                WHEN num_visits <= 2 THEN 'Low (1-2)'
                WHEN num_visits <= 4 THEN 'Medium (3-4)'
                ELSE 'High (5+)' 
            END AS segment,
            ROUND(SUM(converted) / COUNT(*), 4) AS conversion_rate
        FROM converted_features
        GROUP BY segment
    ''',
    'Session Duration Conversion Rate': '''
        SELECT 
            CASE 
                WHEN session_duration < 15 THEN '<15min'
                WHEN session_duration BETWEEN 15 AND 30 THEN '15-30min'
                ELSE '30+min'
            END AS segment,
            ROUND(SUM(converted) / COUNT(*), 4) AS conversion_rate
        FROM converted_features
        GROUP BY segment
    '''
}

# ✅ 输出路径
output_dir = "output/sql_charts"
os.makedirs(output_dir, exist_ok=True)

# ✅ 执行查询 + 可视化
for title, query in queries.items():
    df = pd.read_sql(query, engine)
    plt.figure(figsize=(8, 5))
    sns.barplot(data=df, x='conversion_rate', y=df.columns[0], palette='coolwarm')
    plt.title(title)
    plt.xlabel("Conversion Rate")
    plt.tight_layout()

    # 保存图片
    fname = os.path.join(output_dir, f"{title.lower().replace(' ', '_').replace('(', '').replace(')', '')}.png")
    plt.savefig(fname)
    print(f"✅ Saved: {fname}")