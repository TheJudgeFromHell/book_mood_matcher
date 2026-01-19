# books/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Главная страница
    path('', views.home, name='home'),

    path('books/', views.all_books, name='all_books'),
    path('search/', views.search_books, name='search'),
    path('selection/', views.selection, name='selection'),
    path('statistics/', views.statistics, name='statistics'),
]
