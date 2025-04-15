import pandas as pd
import dask.dataframe as dd
import os
from django.conf import settings

class DataProcessor:
    def __init__(self):
        self.data_path = settings.DATA_FILE_PATH
        self.dask_df = None
        self.pandas_df = None
        self.load_data()
    
    def load_data(self):
        """加载数据文件到Dask DataFrame"""
        try:
            # 使用Dask加载大型CSV文件
            self.dask_df = dd.read_csv(self.data_path)
            # 对于小型操作，也保留一个pandas DataFrame
            self.pandas_df = pd.read_csv(self.data_path)
            return True
        except Exception as e:
            print(f"数据加载错误: {e}")
            return False
    
    def get_countries(self):
        """获取所有国家/地区列表"""
        return self.pandas_df['Country/Region'].unique().tolist()
    
    def get_commodities(self):
        """获取所有商品列表"""
        return self.pandas_df['Commodity'].unique().tolist()
    
    def get_elements(self):
        """获取所有元素列表"""
        return self.pandas_df['Element'].unique().tolist()
    
    def get_seasons(self):
        """获取所有季节列表"""
        return self.pandas_df['Season'].unique().tolist()
    
    def filter_data(self, country=None, commodity=None, element=None, season=None):
        """根据条件筛选数据"""
        filtered_df = self.pandas_df
        
        if country:
            filtered_df = filtered_df[filtered_df['Country/Region'] == country]
        if commodity:
            filtered_df = filtered_df[filtered_df['Commodity'] == commodity]
        if element:
            filtered_df = filtered_df[filtered_df['Element'] == element]
        if season:
            filtered_df = filtered_df[filtered_df['Season'] == season]
            
        return filtered_df
    
    def get_time_series(self, country, commodity, element):
        """获取特定国家、商品和元素的时间序列数据"""
        filtered_df = self.filter_data(country=country, commodity=commodity, element=element)
        # 按季节排序
        filtered_df['Season'] = pd.to_datetime(filtered_df['Season'].str.split('/').str[0].astype(int), format='%Y')
        filtered_df = filtered_df.sort_values('Season')
        
        return {
            'seasons': filtered_df['Season'].dt.year.tolist(),
            'values': filtered_df['Value'].tolist(),
            'unit': filtered_df['Element Unit'].iloc[0] if not filtered_df.empty else ''
        }
    
    def get_comparison_data(self, countries, commodity, element, season):
        """获取多个国家特定商品和元素的比较数据"""
        result = []
        
        for country in countries:
            filtered_df = self.filter_data(country=country, commodity=commodity, element=element, season=season)
            if not filtered_df.empty:
                result.append({
                    'country': country,
                    'value': filtered_df['Value'].iloc[0],
                    'unit': filtered_df['Element Unit'].iloc[0]
                })
        
        return result
    
    def get_commodity_distribution(self, country, season):
        """获取特定国家和季节的商品分布"""
        filtered_df = self.filter_data(country=country, season=season)
        commodity_data = filtered_df.groupby('Commodity').agg({'Value': 'mean'}).reset_index()
        
        return {
            'commodities': commodity_data['Commodity'].tolist(),
            'values': commodity_data['Value'].tolist()
        }

# 创建全局实例
data_processor = DataProcessor()