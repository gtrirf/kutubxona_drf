from django.contrib import admin
from .models import CustomUser, VerificationCode
from django.contrib import admin
from django.contrib import admin


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'telegram_username', 'telegram_profile_photo', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('phone_number', 'telegram_username')
    list_filter = ('is_active', 'is_staff', 'date_joined')
    readonly_fields = ('date_joined',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related('verificationcode_set')
        return queryset

    def telegram_profile_photo_preview(self, obj):
        if obj.telegram_profile_photo:
            return f'<img src="{obj.telegram_profile_photo.url}" style="width: 500px; height: 500px;"/>'
        return 'No Image'
    telegram_profile_photo_preview.allow_tags = True
    telegram_profile_photo_preview.short_description = 'Profile Photo'

admin.site.register(CustomUser, CustomUserAdmin)


class VerificationCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'user', 'created_at', 'is_active',)
    search_fields = ('code', 'user__phone_number', 'user__telegram_username')
    list_filter = ('is_active', 'created_at')

    def user_phone_number(self, obj):
        return obj.user.phone_number if obj.user else 'N/A'
    user_phone_number.short_description = 'Phone Number'

    def user_telegram_username(self, obj):
        return obj.user.telegram_username if obj.user else 'N/A'
    user_telegram_username.short_description = 'Telegram Username'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('user')
        return queryset

admin.site.register(VerificationCode, VerificationCodeAdmin)

