from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Campaign, CsvUpload, MarketingMetric, AiInsight, ApiConfiguration

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['role', 'status']

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(source='userprofile', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']
        
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Passwords don't match"})
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        
        # Create associated profile
        UserProfile.objects.create(user=user)
        return user

class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = ['id', 'name', 'description', 'status', 'start_date', 'end_date', 'budget', 'user', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']
        
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class CsvUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = CsvUpload
        fields = ['id', 'filename', 'file_path', 'processed', 'row_count', 'uploaded_at', 'processed_at']
        read_only_fields = ['user', 'processed', 'row_count', 'uploaded_at', 'processed_at', 'file_path']
        
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class MarketingMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketingMetric
        fields = ['id', 'platform', 'date', 'campaign_name', 'impressions', 'clicks', 'conversions', 
                 'cost', 'revenue', 'roi', 'ctr', 'conversion_rate', 'cost_per_click', 'cost_per_conversion', 
                 'user', 'csv_upload', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']
        
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class AiInsightSerializer(serializers.ModelSerializer):
    class Meta:
        model = AiInsight
        fields = ['id', 'title', 'content', 'category', 'user', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']
        
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class ApiConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiConfiguration
        fields = ['id', 'name', 'api_key', 'service_type', 'active', 'user', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']
        extra_kwargs = {
            'api_key': {'write_only': True},
        }
        
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)