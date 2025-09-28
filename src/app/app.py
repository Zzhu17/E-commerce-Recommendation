from fastapi import FastAPI
from typing import Optional
from contextlib import asynccontextmanager
import pandas as pd
import joblib

from src.models.recommender import get_recommendations
from sklearn.ensemble import RandomForestClassifier

# 类型注解
model: Optional[RandomForestClassifier] = None
user_ids = []

# ✅ lifespan 替代 on_event，用于加载模型
@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, user_ids
    print("🚀 初始化模型与推荐系统...")

    # 加载转化模型
    model = joblib.load("src/models/conversion_model.pkl")

    # 预加载用户 ID 列表
    interactions = pd.read_csv("data/interactions.csv")
    user_ids = interactions["user_id"].unique().tolist()

    yield

# ✅ 初始化 FastAPI
app = FastAPI(lifespan=lifespan)

@app.get("/")
def index():
    return {"msg": "📦 推荐系统接口已就绪"}

# ✅ 用户推荐接口
@app.get("/recommend")
def recommend(user_id: int, method: str = "user_cf"):
    try:
        recs = get_recommendations(user_id, method=method)
        return {"user_id": user_id, "recommendations": recs}
    except Exception as e:
        return {"error": str(e)}