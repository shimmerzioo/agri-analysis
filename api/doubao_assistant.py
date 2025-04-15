import requests
import json
from django.conf import settings

class DouBaoAssistant:
    def __init__(self):
        self.api_key = settings.DOUBAO_API_KEY
        self.api_url = settings.DOUBAO_API_URL
    
    def ask_question(self, question, context=None):
        """向豆包API提问"""
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        
        payload = {
            'question': question,
            'model': 'doubao-lite'
        }
        
        if context:
            payload['context'] = context
        
        try:
            response = requests.post(f"{self.api_url}/chat", headers=headers, data=json.dumps(payload))
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': f'API请求失败: {response.status_code}', 'message': response.text}
        except Exception as e:
            return {'error': f'请求异常: {str(e)}'}
    
    def analyze_agricultural_data(self, country, commodity, element, data):
        """分析农业数据并提供见解"""
        context = f"""
        国家/地区: {country}
        商品: {commodity}
        指标: {element}
        数据: {data}
        """
        
        question = f"请分析{country}的{commodity}在{element}指标上的表现，提供见解和可能的发展趋势。"
        
        return self.ask_question(question, context)
    
    def get_market_recommendations(self, country, commodity):
        """获取市场建议"""
        question = f"基于当前全球农产品市场情况，请提供关于{country}的{commodity}市场的建议和策略。"
        
        return self.ask_question(question)
    
    def explain_agricultural_term(self, term):
        """解释农业术语"""
        question = f"请解释农业术语'{term}'的含义和重要性。"
        
        return self.ask_question(question)

# 创建全局实例
doubao_assistant = DouBaoAssistant()