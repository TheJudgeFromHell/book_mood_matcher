from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Главная страница
    path('', TemplateView.as_view(template_name='home.html'), name='home'),

    # Админка Django
    path('admin/', admin.site.urls),

    # Аутентификация (вход/выход)
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        redirect_authenticated_user=True
    ), name='login'),

    path('logout/', auth_views.LogoutView.as_view(
        next_page='/'
    ), name='logout'),

]