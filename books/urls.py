from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    # Список всех книг
    path('', views.book_list, name='book_list'),

    # Детальная страница книги
    path('<int:book_id>/', views.book_detail, name='book_detail'),

    # Добавление новой книги
    path('add/', views.book_add, name='book_add'),

    # Поиск книг
    path('search/', views.book_search, name='book_search'),

    # Рекомендации по настроению
    path('recommend/', views.book_recommend, name='book_recommend'),
]