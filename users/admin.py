from django.contrib import admin
from .models import UserProfile

# Register UserProfile in admin panel
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'city', 'country', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone_number']
    list_filter = ['country', 'created_at']