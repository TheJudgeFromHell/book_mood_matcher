from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    # Регистрация
    path('register/', views.register, name='register'),

    # Профиль пользователя
    path('profile/', views.profile, name='profile'),

    # Изменение профиля
    path('profile/edit/', views.profile_edit, name='profile_edit'),

    # Изменение пароля
    path('password-change/', views.CustomPasswordChangeView.as_view(), name='password_change'),

    # Сброс пароля
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='users/password_reset.html'
    ), name='password_reset'),

    # Подтверждение сброса пароля
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='users/password_reset_done.html'
    ), name='password_reset_done'),

    # Восстановление пароля
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='users/password_reset_confirm.html'
    ), name='password_reset_confirm'),

    # Завершение восстановления пароля
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='users/password_reset_complete.html'
    ), name='password_reset_complete'),
]