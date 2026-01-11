from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/admin/')),
]

# Кастомизация заголовков админки
admin.site.site_header = "Book Mood Matcher - Панель администратора"
admin.site.site_title = "Админка Book Mood Matcher"
admin.site.index_title = "Добро пожаловать в систему подбора книг!"