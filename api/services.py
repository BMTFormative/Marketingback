import requests
import logging
import json
from django.conf import settings
from .models import AiInsight, ApiConfiguration, MarketingMetric
from .utils import calculate_metrics

logger = logging.getLogger(__name__)

def generate_ai_insights(metrics_queryset, user_id):
    """
    Generate AI insights based on marketing metrics
    """
    # Check if there's an active API configuration
    try:
        api_config = ApiConfiguration.objects.filter(active=True).first()
        if not api_config:
            return False, "No active AI API configuration found"
        
        # Calculate metrics
        metrics = calculate_metrics(metrics_queryset)
        
        # Create prompts for insights
        prompts = [
            {
                "title": "Performance Overview",
                "prompt": f"Provide a concise overview of marketing performance based on these metrics: Conversion Rate: {metrics['conversionRate']}%, Click Through Rate: {metrics['clickThroughRate']}%, ROI: {metrics['roi']}%, Average CPC: ${metrics['averageCpc']}.",
                "category": "overview"
            },
            {
                "title": "Conversion Analysis",
                "prompt": f"Analyze the conversion rate of {metrics['conversionRate']}% and suggest ways to improve it.",
                "category": "conversion"
            },
            {
                "title": "ROI Optimization",
                "prompt": f"Based on an ROI of {metrics['roi']}%, what optimization strategies would you recommend?",
                "category": "roi"
            },
            {
                "title": "Budget Recommendations",
                "prompt": f"Given an Average CPC of ${metrics['averageCpc']} and Click Through Rate of {metrics['clickThroughRate']}%, provide budget allocation recommendations.",
                "category": "budget"
            }
        ]
        
        # Generate insights
        insights_created = 0
        for prompt_data in prompts:
            try:
                content = generate_insight(prompt_data, api_config.api_key)
                
                # Create insight
                AiInsight.objects.create(
                    title=prompt_data["title"],
                    content=content,
                    user_id=user_id,
                    category=prompt_data["category"]
                )
                insights_created += 1
                
            except Exception as e:
                logger.error(f"Error generating insight for {prompt_data['title']}: {str(e)}")
        
        return True, f"Generated {insights_created} insights"
        
    except Exception as e:
        logger.error(f"Error generating AI insights: {str(e)}")
        return False, f"Error generating AI insights: {str(e)}"

def generate_insight(prompt_data, api_key):
    """
    Generate a single insight using the AI API
    """
    # Example implementation using a generic AI API
    # In a real implementation, this would use a specific AI service API
    try:
        # Simulate API call for now
        # In a real implementation, you'd make an actual API request
        
        sample_responses = {
            "overview": "Based on the metrics provided, the marketing performance shows moderate effectiveness. The conversion rate and click-through rate indicate average engagement, while the ROI suggests a positive return on investment. The average CPC is within industry standards, but there's room for optimization to improve overall performance.",
            
            "conversion": "The current conversion rate indicates there's opportunity for improvement. Consider optimizing landing pages, streamlining the conversion process, and A/B testing different calls-to-action. Implementing personalized content and retargeting campaigns could also help boost conversions from engaged visitors.",
            
            "roi": "With the current ROI, your marketing efforts are providing positive returns. To optimize further, focus on higher-performing channels and campaigns, reallocate budget from underperforming areas, and implement more granular tracking to identify specific tactics driving the best returns. Consider testing new creative approaches while maintaining what's working well.",
            
            "budget": "Based on your CPC and click-through rate, your budget allocation could be optimized. Consider increasing spend on campaigns with above-average CTR and below-average CPC. Implement bid adjustments based on device, location, and time of day performance. Also, explore opportunities to improve ad quality scores to reduce costs while maintaining visibility."
        }
        
        # Return appropriate response based on category
        return sample_responses.get(prompt_data["category"], "No insight available for this category.")
        
    except Exception as e:
        logger.error(f"Error calling AI API: {str(e)}")
        return "Unable to generate insight at this time."