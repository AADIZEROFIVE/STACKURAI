from django.urls import path # type: ignore
from django.views.decorators.csrf import csrf_exempt # type: ignore
from . import views

urlpatterns = [
    path('', csrf_exempt(views.index), name='index'),
    path('constitution', views.constitution_chatbot_view, name='const_chatbot'),
    path('api/chat/', views.constitution_process_chat, name='const_process_chat')
]
