from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .data_processor import data_processor
from ml.ml_models import ml_models
from .doubao_assistant import doubao_assistant

@api_view(['GET'])
def get_metadata(request):
    """获取元数据（国家、商品、元素、季节列表）"""
    return Response({
        'countries': data_processor.get_countries(),
        'commodities': data_processor.get_commodities(),
        'elements': data_processor.get_elements(),
        'seasons': data_processor.get_seasons()
    })

@api_view(['GET'])
def get_time_series(request):
    """获取时间序列数据"""
    country = request.GET.get('country')
    commodity = request.GET.get('commodity')
    element = request.GET.get('element')
    
    if not all([country, commodity, element]):
        return Response({'error': '缺少必要参数'}, status=400)
    
    data = data_processor.get_time_series(country, commodity, element)
    return Response(data)

@api_view(['GET'])
def get_comparison(request):
    """获取比较数据"""
    countries = request.GET.getlist('countries')
    commodity = request.GET.get('commodity')
    element = request.GET.get('element')
    season = request.GET.get('season')
    
    if not all([countries, commodity, element, season]):
        return Response({'error': '缺少必要参数'}, status=400)
    
    data = data_processor.get_comparison_data(countries, commodity, element, season)
    return Response(data)

@api_view(['GET'])
def get_distribution(request):
    """获取分布数据"""
    country = request.GET.get('country')
    season = request.GET.get('season')
    
    if not all([country, season]):
        return Response({'error': '缺少必要参数'}, status=400)
    
    data = data_processor.get_commodity_distribution(country, season)
    return Response(data)

@api_view(['GET'])
def predict_random_forest(request):
    """随机森林预测"""
    country = request.GET.get('country')
    commodity = request.GET.get('commodity')
    element = request.GET.get('element')
    years = int(request.GET.get('years', 5))
    
    if not all([country, commodity, element]):
        return Response({'error': '缺少必要参数'}, status=400)
    
    data = ml_models.predict_random_forest(years, country, commodity, element)
    return Response(data)

@api_view(['GET'])
def predict_decision_tree(request):
    """决策树预测"""
    country = request.GET.get('country')
    commodity = request.GET.get('commodity')
    element = request.GET.get('element')
    years = int(request.GET.get('years', 5))
    
    if not all([country, commodity, element]):
        return Response({'error': '缺少必要参数'}, status=400)
    
    data = ml_models.predict_decision_tree(years, country, commodity, element)
    return Response(data)

@api_view(['GET'])
def perform_clustering(request):
    """执行聚类分析"""
    element = request.GET.get('element')
    season = request.GET.get('season')
    
    if not all([element, season]):
        return Response({'error': '缺少必要参数'}, status=400)
    
    data = ml_models.perform_clustering(element, season)
    return Response(data)

@api_view(['GET'])
def recommend_similar(request):
    """推荐相似商品"""
    country = request.GET.get('country')
    commodity = request.GET.get('commodity')
    element = request.GET.get('element')
    
    if not all([country, commodity, element]):
        return Response({'error': '缺少必要参数'}, status=400)
    
    data = ml_models.recommend_similar_commodities(country, commodity, element)
    return Response(data)

@api_view(['POST'])
def ask_assistant(request):
    """询问智能助手"""
    question = request.data.get('question')
    context = request.data.get('context')
    
    if not question:
        return Response({'error': '缺少问题'}, status=400)
    
    response = doubao_assistant.ask_question(question, context)
    return Response(response)

@api_view(['POST'])
def analyze_data(request):
    """分析数据"""
    country = request.data.get('country')
    commodity = request.data.get('commodity')
    element = request.data.get('element')
    data = request.data.get('data')
    
    if not all([country, commodity, element, data]):
        return Response({'error': '缺少必要参数'}, status=400)
    
    response = doubao_assistant.analyze_agricultural_data(country, commodity, element, data)
    return Response(response)