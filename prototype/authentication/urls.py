from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt # type: ignore

app_name = 'authentication'

urlpatterns = [
    path('signup/', csrf_exempt(views.signup), name='signup'),
    path('login/', csrf_exempt(views.login), name='login'),
]