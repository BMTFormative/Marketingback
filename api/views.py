from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import UserProfile, Campaign, CsvUpload, MarketingMetric, AiInsight, ApiConfiguration
from .serializers import (
    UserSerializer, 
    CampaignSerializer, 
    CsvUploadSerializer, 
    MarketingMetricSerializer, 
    AiInsightSerializer, 
    ApiConfigurationSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class CampaignViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows campaigns to be viewed or edited.
    """
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Campaign.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CsvUploadViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows CSV uploads to be viewed or edited.
    """
    serializer_class = CsvUploadSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CsvUpload.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MarketingMetricViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows marketing metrics to be viewed or edited.
    """
    serializer_class = MarketingMetricSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return MarketingMetric.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AiInsightViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows AI insights to be viewed or edited.
    """
    serializer_class = AiInsightSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AiInsight.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ApiConfigurationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows API configurations to be viewed or edited.
    """
    serializer_class = ApiConfigurationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ApiConfiguration.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# Simple placeholder views for the other endpoints
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_csv(request):
    return Response({"message": "CSV upload placeholder"}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_csv(request, pk):
    return Response({"message": f"Processing CSV with ID {pk}"}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def calculate_metrics(request):
    return Response({"message": "Metrics calculation placeholder"}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_insights(request):
    return Response({"message": "Insights generation placeholder"}, status=status.HTTP_200_OK)


# Classes for class-based views
class UploadCsvView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def create(self, request):
        return Response({"message": "CSV upload placeholder"}, status=status.HTTP_200_OK)


class ProcessCsvView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def create(self, request, pk=None):
        return Response({"message": f"Processing CSV with ID {pk}"}, status=status.HTTP_200_OK)


class CalculateMetricsView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def create(self, request):
        return Response({"message": "Metrics calculation placeholder"}, status=status.HTTP_200_OK)


class GenerateInsightsView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def create(self, request):
        return Response({"message": "Insights generation placeholder"}, status=status.HTTP_200_OK)