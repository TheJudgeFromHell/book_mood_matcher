from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import ReadingProfile, ReadingSession, BookRecommendation


class ReadingProfileInline(admin.StackedInline):
    model = ReadingProfile
    can_delete = False
    verbose_name_plural = 'Читательский профиль'
    filter_horizontal = ('favorite_mood_tags',)


class UserAdmin(BaseUserAdmin):
    inlines = (ReadingProfileInline,)


@admin.register(ReadingSession)
class ReadingSessionAdmin(admin.ModelAdmin):
    list_display = ('user_info', 'energy_level', 'time_available', 'created_at')
    list_filter = ('energy_level', 'time_available', 'created_at')
    search_fields = ('user__username', 'current_mood', 'desired_mood_after')
    readonly_fields = ('created_at', 'ip_address', 'user_agent')
    filter_horizontal = ('selected_mood_tags',)

    def user_info(self, obj):
        return obj.user.username if obj.user else 'Гость'

    user_info.short_description = 'Пользователь'


@admin.register(BookRecommendation)
class BookRecommendationAdmin(admin.ModelAdmin):
    list_display = ('book', 'session', 'relevance_score', 'is_clicked')
    list_filter = ('is_shown', 'is_clicked')
    search_fields = ('book__title', 'session__user__username')
    readonly_fields = ('match_reasons', 'clicked_at')


# Перерегистрируем User
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
