"""
recommender.py
核心推荐逻辑模块：提供用户协同过滤推荐与热门商品推荐方法
"""

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class RecommenderSystem:
    def __init__(self, interaction_df):
        self.interaction_df = interaction_df
        self.user_item_matrix = self._build_user_item_matrix()

    def _build_user_item_matrix(self):
        return self.interaction_df.pivot_table(
            index='user_id', columns='item_id', values='value', aggfunc='sum', fill_value=0
        )

    def user_cf(self, target_user_id, top_k=10):
        matrix = self.user_item_matrix
        user_sim = cosine_similarity(matrix)
        user_index = matrix.index.tolist().index(target_user_id)
        scores = user_sim[user_index].dot(matrix.values)
        interacted = matrix.loc[target_user_id] > 0
        scores[interacted.values] = -np.inf
        top_items = np.argsort(scores)[::-1][:top_k]
        return matrix.columns[top_items].tolist()

    def global_top_items(self, top_k=10):
        return self.interaction_df['item_id'].value_counts().head(top_k).index.tolist()

    def recommend(self, user_id, top_k=10, method='user_cf'):
        if method == 'user_cf':
            return self.user_cf(user_id, top_k)
        elif method == 'popular':
            return self.global_top_items(top_k)
        else:
            raise ValueError('Unknown method')

# ✅ 供 app.py 调用的接口函数
def get_recommendations(user_id, interaction_path="data/interactions.csv", method="user_cf", top_k=10):
    df = pd.read_csv(interaction_path)
    recommender = RecommenderSystem(df)
    return recommender.recommend(user_id, method=method, top_k=top_k)
