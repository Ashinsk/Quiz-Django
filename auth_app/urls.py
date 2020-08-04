from django.urls import path, include, reverse_lazy
from django.contrib.auth import views as auth_views
from auth_app import views

app_name = 'auth_app'
urlpatterns = [
    # path('accounts/', include('django.contrib.auth.urls')),

    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html',redirect_authenticated_user=True),name='Login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(),name='Logout'),
    path('accounts/signup/', views.SignUp.as_view(),name='SignUp'),
]