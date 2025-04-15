from django.urls import path
from api import views

urlpatterns = [
    path('predict/random-forest/', views.predict_random_forest, name='predict_random_forest'),
    path('predict/decision-tree/', views.predict_decision_tree, name='predict_decision_tree'),
    path('clustering/', views.perform_clustering, name='perform_clustering'),
    path('recommend-similar/', views.recommend_similar, name='recommend_similar'),
]