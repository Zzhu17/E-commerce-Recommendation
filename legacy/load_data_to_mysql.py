import pandas as pd
import mysql.connector
from mysql.connector import errorcode

conn = None
cursor = None
# ✅ 读取 CSV 数据
df = pd.read_csv("src/data/converted_features.csv")

# ✅ 建立数据库连接
config = {
    "user": "root",
    "password": "Zzp990812",  # ❗修改为你的 MySQL 密码
    "host": "localhost",
    "database": "ecommerce_db"
}

try:
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    print("✅ 成功连接到 MySQL 数据库")

    # ✅ 删除旧表（如果存在）
    cursor.execute("DROP TABLE IF EXISTS converted_features")

    # ✅ 创建新表（字段名与 CSV 保持一致）
    create_table_query = """
    CREATE TABLE converted_features (
        user_id VARCHAR(255),
        converted BOOLEAN,
        device VARCHAR(50),
        country VARCHAR(50),
        num_visits INT,
        session_duration FLOAT
    )
    """
    cursor.execute(create_table_query)
    print("✅ 成功创建新表")

    # ✅ 插入数据
    insert_query = """
    INSERT INTO converted_features (user_id, converted, device, country, num_visits, session_duration)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    for _, row in df.iterrows():
        cursor.execute(insert_query, (
            row['user_id'],
            int(row['converted']),
            row['device'],
            row['country'],
            int(row['num_visits']),
            float(row['session_duration'])
        ))

    conn.commit()
    print("✅ 成功导入数据，共计:", len(df), "条")

except mysql.connector.Error as err:
    print("❌ 数据库错误：", err)

finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
        print("✅ 数据库连接已关闭")