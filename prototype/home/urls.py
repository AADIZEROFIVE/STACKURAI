from django.urls import path # type: ignore
from django.views.decorators.csrf import csrf_exempt # type: ignore
from . import views

urlpatterns = [
    path('', csrf_exempt(views.index), name='index'),
    path('constitution', views.constitution_chatbot_view, name='const_chatbot'),
    path('api/chat/const', views.constitution_process_chat, name='const_process_chat'),
    path('government', views.govt_chatbot_view, name='govt_chatbot'),
    path('api/chat/govt', views.govt_process_chat, name='govt_process_chat'),
    path('dashboard/', views.news_dashboard, name='news_dashboard'),
]
