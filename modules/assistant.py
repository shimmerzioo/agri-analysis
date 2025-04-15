import os
import requests
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class DoubanAssistant:
    """豆包API助手类"""
    
    def __init__(self):
        self.api_key = os.getenv('DOUBAN_API_KEY')
        self.api_secret = os.getenv('DOUBAN_API_SECRET')
        self.api_url = "https://api.doubao.com/chat/completions"
        # 加载并分析数据
        self.data_summary = None
    
    def analyze_data(self, df):
        """分析数据集，获取关键信息"""
        if df is None or df.empty:
            return None
            
        # 获取所有唯一的国家、商品和指标
        countries = sorted(df['country'].unique().tolist())
        commodities = sorted(df['commodity'].unique().tolist())
        elements = sorted(df['element'].unique().tolist())
        units = {}
        
        # 获取每个指标对应的单位
        for element in elements:
            element_data = df[df['element'] == element]
            if len(element_data) > 0 and 'unit' in element_data.columns:
                units[element] = element_data['unit'].iloc[0]
            else:
                units[element] = "未知"
        
        # 保存数据摘要
        self.data_summary = {
            'countries': countries,
            'commodities': commodities,
            'elements': elements,
            'units': units
        }
        
        return self.data_summary
    
    def get_headers(self):
        """获取API请求头"""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def create_system_prompt(self):
        """创建系统提示词"""
        base_prompt = (
            "你是一个专业的农业数据分析助手，擅长解答关于全球农产品数据、市场趋势、政策分析等问题。"
            "请提供准确、专业的回答，并尽可能引用可靠的数据来源。"
            "如果涉及到数据比较，请尽量给出具体的数字和百分比。"
            "如果用户询问的问题超出你的知识范围，请诚实地告知并建议用户查询更专业的资源。"
        )
        
        # 如果有数据摘要，添加到提示中
        if self.data_summary:
            data_info = "\n\n可用的数据包括以下内容：\n"
            data_info += f"- 国家/地区: {', '.join(self.data_summary['countries'][:10])}等\n"
            data_info += f"- 商品: {', '.join(self.data_summary['commodities'])}\n"
            data_info += "- 指标: "
            for element in self.data_summary['elements']:
                unit = self.data_summary['units'].get(element, "")
                data_info += f"{element} ({unit}), "
            data_info = data_info[:-2]  # 移除最后的逗号和空格
            
            return base_prompt + data_info
        
        return base_prompt
    
    def ask(self, user_message, temperature=0.7, max_tokens=800):
        """向豆包API发送请求并获取回复"""
        payload = {
            "model": "doubao-lite",  # 使用豆包提供的模型
            "messages": [
                {
                    "role": "system",
                    "content": self.create_system_prompt()
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(
                self.api_url, 
                headers=self.get_headers(), 
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            reply = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            return {
                'success': True,
                'reply': reply
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_insights(self, user_message, reply, df=None):
        """根据用户问题和回复生成数据洞察"""
        # 如果没有提供数据，则返回None
        if df is None:
            return None
            
        # 如果还没有分析数据，先进行分析
        if self.data_summary is None:
            self.analyze_data(df)
            
        insights = None
        
        # 提取用户问题中的关键信息
        countries = []
        commodities = []
        elements = []
        
        # 检查用户问题中是否包含国家名称
        if self.data_summary and 'countries' in self.data_summary:
            for country in self.data_summary['countries']:
                if country.lower() in user_message.lower():
                    countries.append(country)
        
        # 检查用户问题中是否包含商品名称
        if self.data_summary and 'commodities' in self.data_summary:
            for commodity in self.data_summary['commodities']:
                if commodity.lower() in user_message.lower():
                    commodities.append(commodity)
        
        # 检查用户问题中是否包含指标名称
        if self.data_summary and 'elements' in self.data_summary:
            for element in self.data_summary['elements']:
                if element.lower() in user_message.lower():
                    elements.append(element)
        
        # 如果找到了国家、商品和指标，则生成相应的洞察
        if countries and commodities and elements:
            country = countries[0]
            commodity = commodities[0]
            element = elements[0]
            
            # 筛选数据
            filtered_data = df[(df['country'] == country) & 
                              (df['commodity'] == commodity) & 
                              (df['element'] == element)]
            
            if len(filtered_data) > 0:
                # 获取单位信息
                unit = filtered_data['unit'].iloc[0] if 'unit' in filtered_data.columns else ""
                
                # 按年份排序
                filtered_data = filtered_data.sort_values('year')
                
                # 准备图表数据
                years = filtered_data['year'].unique().tolist()
                values = []
                
                for year in years:
                    year_data = filtered_data[filtered_data['year'] == year]
                    values.append(year_data['value'].mean())
                
                # 如果有多个国家，则比较数据
                if len(countries) > 1:
                    country2 = countries[1]
                    filtered_data2 = df[(df['country'] == country2) & 
                                      (df['commodity'] == commodity) & 
                                      (df['element'] == element)]
                    
                    if len(filtered_data2) > 0:
                        values2 = []
                        for year in years:
                            year_data = filtered_data2[filtered_data2['year'] == year]
                            if len(year_data) > 0:
                                values2.append(year_data['value'].mean())
                            else:
                                values2.append(None)
                        
                        insights = {
                            'text': f"{country}和{country2}的{commodity}{element}比较",
                            'chart_data': {
                                'title': {
                                    'text': f"{country}和{country2}的{commodity}{element}比较 ({unit})"
                                },
                                'tooltip': {
                                    'trigger': 'axis'
                                },
                                'legend': {
                                    'data': [country, country2]
                                },
                                'xAxis': {
                                    'type': 'category',
                                    'data': years
                                },
                                'yAxis': {
                                    'type': 'value',
                                    'name': unit
                                },
                                'series': [
                                    {
                                        'name': country,
                                        'type': 'line',
                                        'data': values
                                    },
                                    {
                                        'name': country2,
                                        'type': 'line',
                                        'data': values2
                                    }
                                ]
                            }
                        }
                else:
                    # 单国家数据洞察
                    insights = {
                        'text': f"{country}的{commodity}{element}趋势分析",
                        'chart_data': {
                            'title': {
                                'text': f"{country}的{commodity}{element}趋势 ({unit})"
                            },
                            'tooltip': {
                                'trigger': 'axis'
                            },
                            'xAxis': {
                                'type': 'category',
                                'data': years
                            },
                            'yAxis': {
                                'type': 'value',
                                'name': unit
                            },
                            'series': [{
                                'name': element,
                                'type': 'line',
                                'data': values,
                                'markPoint': {
                                    'data': [
                                        {'type': 'max', 'name': '最大值'},
                                        {'type': 'min', 'name': '最小值'}
                                    ]
                                }
                            }]
                        }
                    }
                    
                    # 添加表格数据
                    table_data = {
                        'headers': ['年份', f'{element} ({unit})'],
                        'rows': []
                    }
                    
                    for i, year in enumerate(years):
                        table_data['rows'].append([year, round(values[i], 2)])
                    
                    insights['table_data'] = table_data
        
        # 中国与美国水稻产量比较（特定问题的处理）
        elif '中国' in user_message and '美国' in user_message and '水稻' in user_message and '产量' in user_message:
            # 筛选中国水稻产量数据
            china_data = df[(df['country'] == 'China') & 
                           (df['commodity'] == 'RICE') & 
                           (df['element'] == 'Production')]
            
            # 筛选美国水稻产量数据
            us_data = df[(df['country'] == 'United States') & 
                        (df['commodity'] == 'RICE') & 
                        (df['element'] == 'Production')]
            
            if len(china_data) > 0 and len(us_data) > 0:
                # 获取单位信息
                unit = china_data['unit'].iloc[0] if 'unit' in china_data.columns else ""
                
                # 找出共同的年份
                china_years = set(china_data['year'].unique())
                us_years = set(us_data['year'].unique())
                common_years = sorted(list(china_years.intersection(us_years)))
                
                if common_years:
                    china_values = []
                    us_values = []
                    
                    for year in common_years:
                        china_year_data = china_data[china_data['year'] == year]
                        us_year_data = us_data[us_data['year'] == year]
                        
                        china_values.append(china_year_data['value'].mean())
                        us_values.append(us_year_data['value'].mean())
                    
                    insights = {
                        'text': '根据AMIS数据，中国是全球最大的水稻生产国，产量远超美国。',
                        'chart_data': {
                            'title': {
                                'text': f'中国和美国水稻产量比较 ({unit})'
                            },
                            'tooltip': {
                                'trigger': 'axis'
                            },
                            'legend': {
                                'data': ['中国', '美国']
                            },
                            'xAxis': {
                                'type': 'category',
                                'data': common_years
                            },
                            'yAxis': {
                                'type': 'value',
                                'name': unit
                            },
                            'series': [
                                {
                                    'name': '中国',
                                    'type': 'bar',
                                    'data': china_values
                                },
                                {
                                    'name': '美国',
                                    'type': 'bar',
                                    'data': us_values
                                }
                            ]
                        },
                        'table_data': {
                            'headers': ['年份', f'中国水稻产量({unit})', f'美国水稻产量({unit})', '中国/美国比值'],
                            'rows': []
                        }
                    }
                    
                    # 添加表格数据
                    for i, year in enumerate(common_years):
                        ratio = round(china_values[i] / us_values[i], 2) if us_values[i] != 0 else 'N/A'
                        insights['table_data']['rows'].append([
                            year, 
                            round(china_values[i], 2), 
                            round(us_values[i], 2),
                            ratio
                        ])
        
        return insights
    
    def get_data_summary(self, df=None):
        """获取数据摘要信息"""
        if df is not None and (self.data_summary is None):
            self.analyze_data(df)
            
        return self.data_summary