import pandas as pd

def load_user_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df

def load_orders(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=['order_time'])
    return df

def load_clicks(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=['timestamp'])
    return df

def load_ads(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=['impression_time', 'click_time'])
    return df

def load_all(data_paths: dict) -> dict:
    return {
        'users': load_user_data(data_paths['users']),
        'orders': load_orders(data_paths['orders']),
        'clicks': load_clicks(data_paths['clicks']),
        'ads': load_ads(data_paths['ads']),
    }
