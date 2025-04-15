from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import (
    UserProfile, Campaign, CsvUpload, 
    MarketingMetric, AiInsight, ApiConfiguration
)

# Inline admin for UserProfile
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'profile'

# Extend User admin
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'get_status', 'is_staff')
    list_filter = BaseUserAdmin.list_filter + ('userprofile__role', 'userprofile__status')
    
    def get_role(self, obj):
        return obj.profile.role if hasattr(obj, 'profile') else '-'
    get_role.short_description = 'Role'
    
    def get_status(self, obj):
        return obj.profile.status if hasattr(obj, 'profile') else '-'
    get_status.short_description = 'Status'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'status', 'start_date', 'end_date', 'budget', 'created_at')
    list_filter = ('status', 'start_date', 'user')
    search_fields = ('name', 'description')
    date_hierarchy = 'created_at'

@admin.register(CsvUpload)
class CsvUploadAdmin(admin.ModelAdmin):
    list_display = ('filename', 'user', 'processed', 'row_count', 'uploaded_at', 'processed_at')
    list_filter = ('processed', 'user')
    search_fields = ('filename',)
    date_hierarchy = 'uploaded_at'

@admin.register(MarketingMetric)
class MarketingMetricAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'csv_upload', 'platform', 'date', 'campaign_name', 
                   'impressions', 'clicks', 'conversions', 'cost', 'revenue', 'created_at')
    list_filter = ('platform', 'user', 'csv_upload')
    search_fields = ('platform', 'campaign_name')
    date_hierarchy = 'created_at'

@admin.register(AiInsight)
class AiInsightAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'created_at')
    list_filter = ('category', 'user')
    search_fields = ('title', 'content')
    date_hierarchy = 'created_at'

@admin.register(ApiConfiguration)
class ApiConfigurationAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'service_type', 'active', 'created_at')
    list_filter = ('service_type', 'active', 'user')
    search_fields = ('name', 'service_type')
    date_hierarchy = 'created_at'
