from django.urls import path
from .views import LoginView, LogoutView, PasswordRecoveryView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('recovery/', PasswordRecoveryView.as_view(), name='recovery'),
]
