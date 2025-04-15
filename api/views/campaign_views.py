from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..models import Campaign
from ..serializers import CampaignSerializer
from ..permissions import IsOwnerOrAdmin

class CampaignViewSet(viewsets.ModelViewSet):
    """
    API endpoint for campaigns.
    """
    serializer_class = CampaignSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    queryset = Campaign.objects.all()
    
    def get_queryset(self):
        """
        This view should return a list of all campaigns
        for the currently authenticated user.
        """
        user = self.request.user
        return Campaign.objects.filter(user=user)
    
    def perform_create(self, serializer):
        """
        Save the campaign with the authenticated user.
        """
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        Return list of active campaigns.
        """
        active_campaigns = self.get_queryset().filter(status='active')
        serializer = self.get_serializer(active_campaigns, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def completed(self, request):
        """
        Return list of completed campaigns.
        """
        completed_campaigns = self.get_queryset().filter(status='completed')
        serializer = self.get_serializer(completed_campaigns, many=True)
        return Response(serializer.data)