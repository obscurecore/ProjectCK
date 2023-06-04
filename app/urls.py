from django.urls import path, include

from app.views import MainView, Register

urlpatterns = [
    path('app/', include('django.contrib.auth.urls')),
    path('', MainView.as_view(), name='main'),
    path('register/', Register.as_view(), name='register'),
]


