import os
import pandas as pd
import joblib

# ========= 路径定义 =========
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
DATA_PATH = os.path.join(BASE_DIR, "src","data", "converted_features.csv")
MODEL_PATH = os.path.join(BASE_DIR, "src","models", "conversion_model.pkl")
OUTPUT_PATH = os.path.join(BASE_DIR, "output", "recommendations.csv")

# ========= 推荐逻辑参数 =========
TOP_N_USERS = 20  # 推荐给前 N 个最可能转化的用户
TOP_K_ITEMS = 3   # 每个用户推荐几个商品
POPULAR_ITEMS = ["I001", "I002", "I003", "I004", "I005"]  # 热门商品ID示例（你可以改成自动生成）

# ========= 主流程 =========
def generate_conversion_recommendations():
    print("✅ 加载数据和模型...")
    df = pd.read_csv(DATA_PATH)
    model = joblib.load(MODEL_PATH)

    if "user_id" not in df.columns:
        raise ValueError("❌ 缺少 user_id 列，请确保 converted_features.csv 中包含 user_id")

    if "converted" not in df.columns:
        raise ValueError("❌ 缺少 converted 列，请确保已标注用户是否转化")

    print("✅ 选取未转化用户...")
    unconverted_df = df[df["converted"] == 0].copy()
    user_ids = unconverted_df["user_id"].values

    # 删除无关列
    feature_df = unconverted_df.drop(columns=["user_id", "converted"], errors="ignore")

    print("✅ 预测转化概率...")
    probs = model.predict_proba(feature_df)[:, 1]  # 获取转化概率（类别1）

    print("✅ 生成推荐结果...")
    rec_df = pd.DataFrame({
        "user_id": user_ids,
        "conversion_score": probs
    }).sort_values("conversion_score", ascending=False).head(TOP_N_USERS)

    # 分配热门商品（示意）
    rec_df["recommended_items"] = [POPULAR_ITEMS[:TOP_K_ITEMS] for _ in range(len(rec_df))]
    rec_df["method_used"] = "conversion_score + hot_items"

    print("✅ 保存推荐结果至 output/recommendations.csv")
    rec_df.to_csv(OUTPUT_PATH, index=False)
    print("🎉 推荐已完成！")

# ========= 脚本入口 =========
if __name__ == "__main__":
    generate_conversion_recommendations()