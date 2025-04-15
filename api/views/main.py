"""
Main views module that imports all other view modules
"""

# Import user views
from .user_views import UserViewSet

# Import campaign views
from .campaign_views import CampaignViewSet

# Import CSV views
from .csv_views import UploadCsvView, ProcessCsvView

# Import metric views
from .metric_views import MarketingMetricViewSet, CalculateMetricsView

# Import insight views
from .insight_views import AiInsightViewSet, GenerateInsightsView

# Import API configuration views
from .api_config_views import ApiConfigurationViewSet