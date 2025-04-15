import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from api.data_processor import data_processor

class MLModels:
    def __init__(self):
        self.random_forest = None
        self.decision_tree = None
        self.kmeans = None
        self.scaler = StandardScaler()
    
    def prepare_data(self, country, commodity, element):
        """准备机器学习所需的数据"""
        # 获取时间序列数据
        time_series = data_processor.get_time_series(country, commodity, element)
        
        # 创建特征和目标变量
        seasons = time_series['seasons']
        values = time_series['values']
        
        # 创建特征矩阵
        X = np.array(seasons).reshape(-1, 1)
        y = np.array(values)
        
        return X, y
    
    def train_random_forest(self, country, commodity, element):
        """训练随机森林模型"""
        X, y = self.prepare_data(country, commodity, element)
        
        if len(X) < 10:  # 数据太少，无法训练
            return False
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.random_forest = RandomForestRegressor(n_estimators=100, random_state=42)
        self.random_forest.fit(X_train, y_train)
        
        # 计算模型评分
        score = self.random_forest.score(X_test, y_test)
        
        return {
            'model': self.random_forest,
            'score': score,
            'feature_importance': self.random_forest.feature_importances_.tolist()
        }
    
    def predict_random_forest(self, future_years, country, commodity, element):
        """使用随机森林模型进行预测"""
        if self.random_forest is None:
            self.train_random_forest(country, commodity, element)
        
        # 获取最后一年
        X, _ = self.prepare_data(country, commodity, element)
        last_year = X[-1][0]
        
        # 创建未来年份的特征
        future_X = np.array([last_year + i for i in range(1, future_years + 1)]).reshape(-1, 1)
        
        # 预测
        predictions = self.random_forest.predict(future_X)
        
        return {
            'years': [int(last_year + i) for i in range(1, future_years + 1)],
            'predictions': predictions.tolist()
        }
    
    def train_decision_tree(self, country, commodity, element):
        """训练决策树模型"""
        X, y = self.prepare_data(country, commodity, element)
        
        if len(X) < 10:  # 数据太少，无法训练
            return False
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.decision_tree = DecisionTreeRegressor(max_depth=5, random_state=42)
        self.decision_tree.fit(X_train, y_train)
        
        # 计算模型评分
        score = self.decision_tree.score(X_test, y_test)
        
        return {
            'model': self.decision_tree,
            'score': score
        }
    
    def predict_decision_tree(self, future_years, country, commodity, element):
        """使用决策树模型进行预测"""
        if self.decision_tree is None:
            self.train_decision_tree(country, commodity, element)
        
        # 获取最后一年
        X, _ = self.prepare_data(country, commodity, element)
        last_year = X[-1][0]
        
        # 创建未来年份的特征
        future_X = np.array([last_year + i for i in range(1, future_years + 1)]).reshape(-1, 1)
        
        # 预测
        predictions = self.decision_tree.predict(future_X)
        
        return {
            'years': [int(last_year + i) for i in range(1, future_years + 1)],
            'predictions': predictions.tolist()
        }
    
    def perform_clustering(self, element, season):
        """执行聚类分析"""
        # 获取所有国家和商品的数据
        countries = data_processor.get_countries()
        commodities = data_processor.get_commodities()
        
        data_points = []
        labels = []
        
        for country in countries:
            for commodity in commodities:
                filtered_df = data_processor.filter_data(country=country, commodity=commodity, element=element, season=season)
                if not filtered_df.empty:
                    value = filtered_df['Value'].iloc[0]
                    data_points.append([value])
                    labels.append(f"{country} - {commodity}")
        
        if len(data_points) < 5:  # 数据太少，无法聚类
            return False
        
        # 标准化数据
        X = self.scaler.fit_transform(data_points)
        
        # 确定最佳聚类数
        n_clusters = min(5, len(X) // 2)  # 最多5个聚类，或者数据点数量的一半
        
        # 执行K-means聚类
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = self.kmeans.fit_predict(X)
        
        # 整理结果
        result = []
        for i, (label, cluster) in enumerate(zip(labels, clusters)):
            result.append({
                'label': label,
                'cluster': int(cluster),
                'value': data_points[i][0]
            })
        
        return {
            'clusters': result,
            'n_clusters': n_clusters,
            'cluster_centers': self.scaler.inverse_transform(self.kmeans.cluster_centers_).tolist()
        }
    
    def recommend_similar_commodities(self, country, commodity, element):
        """推荐相似的商品"""
        # 获取所有商品
        all_commodities = data_processor.get_commodities()
        
        # 获取目标商品的时间序列
        target_series = data_processor.get_time_series(country, commodity, element)
        target_values = np.array(target_series['values'])
        
        if len(target_values) == 0:
            return []
        
        # 计算与其他商品的相似度
        similarities = []
        for other_commodity in all_commodities:
            if other_commodity != commodity:
                other_series = data_processor.get_time_series(country, other_commodity, element)
                other_values = np.array(other_series['values'])
                
                # 确保两个序列长度相同
                min_length = min(len(target_values), len(other_values))
                if min_length > 0:
                    # 计算相关系数
                    correlation = np.corrcoef(target_values[:min_length], other_values[:min_length])[0, 1]
                    if not np.isnan(correlation):
                        similarities.append((other_commodity, correlation))
        
        # 按相似度排序并返回前5个
        similarities.sort(key=lambda x: abs(x[1]), reverse=True)
        return similarities[:5]

# 创建全局实例
ml_models = MLModels()