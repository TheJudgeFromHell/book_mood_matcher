from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('books/', include('books.urls')),
    path('users/', include('users.urls')),
    path('analytics/', include('analytics.urls')),
    path('', RedirectView.as_view(url='/books/', permanent=True)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Кастомизация заголовков админки
admin.site.site_header = "Book Mood Matcher - Панель администратора"
admin.site.site_title = "Админка Book Mood Matcher"
admin.site.index_title = "Добро пожаловать в систему подбора книг!"