from django.urls import path # type: ignore
from django.views.decorators.csrf import csrf_exempt # type: ignore
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('chat', views.chatbot_view, name='chatbot'),
    path('api/chat/', views.process_chat, name='process_chat')
]
