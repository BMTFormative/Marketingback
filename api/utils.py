import os
import pandas as pd
from datetime import datetime
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

def validate_csv_format(file_path):
    """
    Validate that CSV has the expected format
    Expected columns: Date, Platform, Campaign, Spend, Revenue, Clicks, Impressions, Conversions
    """
    try:
        df = pd.read_csv(file_path)
        
        required_columns = [
            'Date', 'Platform', 'Campaign', 'Spend', 'Revenue', 
            'Clicks', 'Impressions', 'Conversions'
        ]
        
        # Check if all required columns exist
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return False, f"Missing columns: {', '.join(missing_columns)}"
        
        # Validate data types
        try:
            # Convert Date to datetime
            df['Date'] = pd.to_datetime(df['Date'])
            
            # Convert numeric columns
            numeric_columns = ['Spend', 'Revenue', 'Clicks', 'Impressions', 'Conversions']
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col])
                
            return True, df
        except Exception as e:
            return False, f"Data type validation failed: {str(e)}"
            
    except Exception as e:
        return False, f"CSV parsing failed: {str(e)}"

def process_csv_data(csv_upload):
    """
    Process the CSV file and create marketing metrics
    """
    from .models import MarketingMetric
    
    file_path = csv_upload.file_path
    success, result = validate_csv_format(file_path)
    
    if not success:
        logger.error(f"CSV validation failed: {result}")
        return False, result
    
    df = result
    metrics_created = 0
    
    try:
        for _, row in df.iterrows():
            # Create a new marketing metric
            MarketingMetric.objects.create(
                user=csv_upload.user,
                csv_upload=csv_upload,
                platform=row['Platform'],
                date=row['Date'],
                campaign_name=row['Campaign'],
                impressions=int(row['Impressions']),
                clicks=int(row['Clicks']),
                conversions=int(row['Conversions']),
                cost=Decimal(str(row['Spend'])),
                revenue=Decimal(str(row['Revenue']))
            )
            metrics_created += 1
            
        # Update the CSV upload record
        csv_upload.processed = True
        csv_upload.row_count = metrics_created
        csv_upload.processed_at = datetime.now()
        csv_upload.save()
        
        return True, f"Successfully processed {metrics_created} rows"
        
    except Exception as e:
        logger.error(f"Error processing CSV: {str(e)}")
        return False, f"Error processing CSV: {str(e)}"

def calculate_metrics(metrics_queryset):
    """
    Calculate metrics from a queryset of marketing metrics
    """
    if not metrics_queryset.exists():
        return {
            "conversionRate": 0,
            "clickThroughRate": 0,
            "roi": 0,
            "averageCpc": 0
        }
    
    total_impressions = sum(metric.impressions for metric in metrics_queryset)
    total_clicks = sum(metric.clicks for metric in metrics_queryset)
    total_conversions = sum(metric.conversions for metric in metrics_queryset)
    total_cost = sum(metric.cost for metric in metrics_queryset)
    total_revenue = sum(metric.revenue for metric in metrics_queryset)
    
    # Calculate metrics
    conversion_rate = (total_conversions / total_clicks) * 100 if total_clicks > 0 else 0
    click_through_rate = (total_clicks / total_impressions) * 100 if total_impressions > 0 else 0
    roi = ((total_revenue - total_cost) / total_cost) * 100 if total_cost > 0 else 0
    average_cpc = total_cost / total_clicks if total_clicks > 0 else 0
    
    return {
        "conversionRate": round(conversion_rate, 2),
        "clickThroughRate": round(click_through_rate, 2),
        "roi": round(roi, 2),
        "averageCpc": round(float(average_cpc), 2)
    }