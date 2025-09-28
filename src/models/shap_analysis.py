import os
import json
import joblib
import shap
import pandas as pd
import matplotlib.pyplot as plt

# ========== 路径配置 ==========
MODEL_PATH = "src/models/conversion_model.pkl"
FEATURE_PATH = "src/data/converted_features.csv"
FEATURE_COLS_PATH = "src/models/artifacts/feature_cols.json"
OUTPUT_DIR = "output/shap"

# ========== 创建输出目录 ==========
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ========== 加载模型 ==========
print("✅ 正在加载模型...")
model = joblib.load(MODEL_PATH)

print("✅ 正在加载特征数据...")
df = pd.read_csv(FEATURE_PATH)

# ✅ 加载训练时的特征列
with open(FEATURE_COLS_PATH, "r") as f:
    feature_cols = json.load(f)
X = df[feature_cols]

# ========== 初始化 explainer 并计算 SHAP 值 ==========
print("✅ 正在计算 SHAP 值 (使用 shap.Explainer) ...")
explainer = shap.Explainer(model, X)
shap_values_all = explainer(X, check_additivity=False)  # ← 禁用加和检查以避免报错

# 如果是分类模型，shap_values 是 (n_samples, n_features, n_classes)
# 我们只取正类的解释值 (class = 1)
if len(shap_values_all.shape) == 3:
    shap_values = shap_values_all[:, :, 1]
else:
    shap_values = shap_values_all

# ========== 生成 summary_plot 图像 ==========
print("✅ 正在生成 summary_plot 图像 ...")
shap.plots.beeswarm(shap_values, show=False)
plt.savefig(os.path.join(OUTPUT_DIR, "summary_plot.png"), bbox_inches='tight')
plt.close()

# ========== 生成 importance_bar_plot 图像 ==========
print("✅ 正在生成 importance_bar_plot 图像 ...")
shap.plots.bar(shap_values, show=False)
plt.savefig(os.path.join(OUTPUT_DIR, "importance_bar_plot.png"), bbox_inches='tight')
plt.close()

print("🎉 SHAP 图像已保存至 output/shap/")