from django.contrib import admin
from django.utils.html import format_html
from .models import Genre, MoodTag, Book, UserBookInteraction


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'book_count')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

    def book_count(self, obj):
        return obj.books.count()

    book_count.short_description = 'Количество книг'


@admin.register(MoodTag)
class MoodTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'emoji', 'mood_type', 'book_count')
    list_filter = ('mood_type',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

    def book_count(self, obj):
        return obj.books.count()

    book_count.short_description = 'Количество книг'


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'genre', 'pace', 'complexity', 'cover_preview', 'is_active')
    list_filter = ('genre', 'is_active', 'pace', 'complexity')
    search_fields = ('title', 'author', 'description', 'isbn')
    filter_horizontal = ('mood_tags',)
    readonly_fields = ('created_at', 'updated_at', 'cover_preview')
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'author', 'isbn', 'description', 'genre')
        }),
        ('Параметры для рекомендаций', {
            'fields': ('pace', 'complexity', 'emotional_intensity', 'mood_tags')
        }),
        ('Детали', {
            'fields': ('page_count', 'published_date', 'publisher', 'language')
        }),
        ('Обложка и ссылки', {
            'fields': ('cover_image', 'cover_url', 'cover_preview', 'google_books_id')
        }),
        ('Статистика', {
            'fields': ('average_rating', 'ratings_count')
        }),
        ('Системные поля', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )

    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" width="50" height="75" />', obj.cover_image.url)
        elif obj.cover_url:
            return format_html('<img src="{}" width="50" height="75" />', obj.cover_url)
        return "Нет обложки"

    cover_preview.short_description = 'Обложка'


@admin.register(UserBookInteraction)
class UserBookInteractionAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'interaction_type', 'rating', 'created_at')
    list_filter = ('interaction_type', 'rating', 'created_at')
    search_fields = ('user__username', 'book__title', 'review')
    readonly_fields = ('created_at', 'updated_at')