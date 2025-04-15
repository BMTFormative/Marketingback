"""
Initialize the views package and export all views
"""

from .main import (
    # User views
    UserViewSet,
    
    # Campaign views
    CampaignViewSet,
    
    # CSV views
    UploadCsvView,
    ProcessCsvView,
    
    # Metric views
    MarketingMetricViewSet,
    CalculateMetricsView,
    
    # Insight views
    AiInsightViewSet,
    GenerateInsightsView,
    
    # API configuration views
    ApiConfigurationViewSet
)