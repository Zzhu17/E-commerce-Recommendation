
import pandas as pd
import os
from src.models.recommender import get_recommendations
import joblib

def export_recommendations_csv(interaction_path="data/interactions.csv", method="user_cf", top_k=10, output_path="output/recommendations.csv"):
    """
    为所有用户导出推荐结果到 CSV，供 Power BI 等可视化工具使用。
    输出格式：user_id, rank, item_id, method
    """
    df = pd.read_csv(interaction_path)
    user_ids = df["user_id"].unique()

    rows = []
    for user_id in user_ids:
        try:
            recs = get_recommendations(user_id, interaction_path, method=method, top_k=top_k)
            for rank, item_id in enumerate(recs, 1):
                rows.append({
                    "user_id": user_id,
                    "rank": rank,
                    "item_id": item_id,
                    "method": method
                })
        except Exception as e:
            print(f"[⚠️] Failed for user {user_id}: {e}")

    # 保存为 CSV
    out_df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    out_df.to_csv(output_path, index=False)
    print(f"[✅] 推荐结果已保存至 {output_path}")

def export_conversion_predictions(model_path="src/models/conversion_model.pkl", feature_data_path="data/converted_features.csv", output_path="output/conversion_predictions.csv"):
    """
    使用已训练的转化模型，对特征数据进行预测，并导出结果 CSV，供 Power BI 使用。
    输出格式：原始特征列 + predicted_label + predicted_proba
    """
    # 读取模型和特征数据
    model = joblib.load(model_path)
    df = pd.read_csv(feature_data_path)

    if "converted" in df.columns:
        X = df.drop(columns=["converted"])
    else:
        X = df

    # 模型预测
    predicted_proba = model.predict_proba(X)[:, 1]
    predicted_label = model.predict(X)

    df["predicted_label"] = predicted_label
    df["predicted_proba"] = predicted_proba

    # 输出保存
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"[✅] 模型预测结果已保存至 {output_path}")
