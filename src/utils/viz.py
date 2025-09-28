import matplotlib.pyplot as plt
import seaborn as sns

def plot_cluster_distribution(rfm_df):
    sns.countplot(data=rfm_df, x='cluster')
    plt.title("User Cluster Distribution")
    plt.xlabel("Cluster")
    plt.ylabel("Count")
    plt.show()

def plot_feature_importance(model, feature_names, top_n=10):
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
        indices = importances.argsort()[::-1][:top_n]
        plt.figure(figsize=(8, 5))
        sns.barplot(x=importances[indices], y=[feature_names[i] for i in indices])
        plt.title("Feature Importances")
        plt.show()
    else:
        print("模型没有 feature_importances_ 属性")
