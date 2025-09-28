import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def compute_rfm(orders: pd.DataFrame) -> pd.DataFrame:
    now = orders['order_time'].max() + pd.Timedelta(days=1)
    df = orders.groupby('user_id').agg({
        'order_time': lambda x: (now - x.max()).days,
        'order_id': 'count',
        'price': 'sum'
    }).reset_index()
    df.columns = ['user_id', 'recency', 'frequency', 'monetary']
    return df

def cluster_users(rfm: pd.DataFrame, n_clusters=4) -> pd.DataFrame:
    features = ['recency', 'frequency', 'monetary']
    scaler = StandardScaler()
    X = scaler.fit_transform(rfm[features])
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    rfm['cluster'] = kmeans.fit_predict(X)
    return rfm
