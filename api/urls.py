from django.urls import path
from . import views

urlpatterns = [
    path('metadata/', views.get_metadata, name='get_metadata'),
    path('time-series/', views.get_time_series, name='get_time_series'),
    path('comparison/', views.get_comparison, name='get_comparison'),
    path('distribution/', views.get_distribution, name='get_distribution'),
    path('predict/random-forest/', views.predict_random_forest, name='predict_random_forest'),
    path('predict/decision-tree/', views.predict_decision_tree, name='predict_decision_tree'),
    path('clustering/', views.perform_clustering, name='perform_clustering'),
    path('recommend-similar/', views.recommend_similar, name='recommend_similar'),
    path('ask-assistant/', views.ask_assistant, name='ask_assistant'),
    path('analyze-data/', views.analyze_data, name='analyze_data'),
]