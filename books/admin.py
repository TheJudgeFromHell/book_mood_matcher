from django.contrib import admin
from .models import Book, UserProfile, BookSelection

# Настройки для модели Book
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'mood', 'complexity')
    list_filter = ('mood', 'complexity')
    search_fields = ('title', 'author', 'description')
    list_per_page = 20

# Настройки для модели UserProfile
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'reading_speed', 'favorite_genres')
    list_filter = ('reading_speed',)
    search_fields = ('user__username', 'user__email', 'favorite_genres')
    filter_horizontal = ('favorite_books',)  # Удобный виджет для ManyToMany

# Настройки для модели BookSelection
@admin.register(BookSelection)
class BookSelectionAdmin(admin.ModelAdmin):
    list_display = ('user', 'selected_mood', 'selected_complexity', 'selected_date')
    list_filter = ('selected_mood', 'selected_complexity', 'selected_date')
    search_fields = ('user__username',)
    date_hierarchy = 'selected_date'
    filter_horizontal = ('recommended_books',)