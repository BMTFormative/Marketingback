import pandas as pd
import os
import logging
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from decimal import Decimal

from .models import CsvUpload, MarketingMetric, AiInsight

logger = logging.getLogger(__name__)

class CSVProcessor:
    """
    Process CSV files and create marketing metrics from the data
    """
    
    def __init__(self, csv_upload_id):
        """
        Initialize with a CSV upload ID
        """
        self.csv_upload_id = csv_upload_id
        self.csv_upload = None
        self.metrics_created = 0
        self.insights_created = 0
        
    def process(self):
        """
        Main processing method
        
        Returns:
            tuple: (success, message)
        """
        try:
            # Get the CSV upload record
            self.csv_upload = CsvUpload.objects.get(id=self.csv_upload_id)
            
            # Check if already processed
            if self.csv_upload.processed:
                return True, "CSV file already processed"
            
            # Validate and load the CSV file
            success, result = self._validate_csv()
            if not success:
                return False, result
                
            # Process the data and create metrics
            success, result = self._create_metrics(result)
            if not success:
                return False, result
                
            # Generate insights
            success, result = self._generate_insights()
            if not success:
                logger.warning(f"Failed to generate insights: {result}")
                
            # Update the CSV upload record
            self.csv_upload.processed = True
            self.csv_upload.row_count = self.metrics_created
            self.csv_upload.processed_at = timezone.now()
            self.csv_upload.save()
            
            return True, f"Successfully processed {self.metrics_created} rows and generated {self.insights_created} insights"
            
        except CsvUpload.DoesNotExist:
            return False, f"CSV upload with ID {self.csv_upload_id} not found"
        except Exception as e:
            logger.error(f"Error processing CSV file: {str(e)}")
            return False, f"Error processing CSV file: {str(e)}"
    
    def _validate_csv(self):
        """
        Validate that the CSV file has the expected format
        
        Returns:
            tuple: (success, dataframe or error message)
        """
        try:
            file_path = self.csv_upload.file_path
            
            # Check if file exists
            if not os.path.exists(file_path):
                return False, f"File not found at {file_path}"
                
            # Read CSV file
            df = pd.read_csv(file_path)
            
            # Check required columns
            required_columns = [
                'Date', 'Platform', 'Campaign', 'Spend', 'Revenue', 
                'Clicks', 'Impressions', 'Conversions'
            ]
            
            # Check for case-insensitive matches
            columns_lower = [col.lower() for col in df.columns]
            missing_columns = []
            
            for req_col in required_columns:
                if req_col.lower() not in columns_lower:
                    missing_columns.append(req_col)
            
            if missing_columns:
                return False, f"Missing required columns: {', '.join(missing_columns)}"
            
            # Try to convert columns to appropriate types
            try:
                # Handle column case insensitivity
                date_col = next(col for col in df.columns if col.lower() == 'date')
                platform_col = next(col for col in df.columns if col.lower() == 'platform')
                campaign_col = next(col for col in df.columns if col.lower() == 'campaign')
                spend_col = next(col for col in df.columns if col.lower() == 'spend')
                revenue_col = next(col for col in df.columns if col.lower() == 'revenue')
                clicks_col = next(col for col in df.columns if col.lower() == 'clicks')
                impressions_col = next(col for col in df.columns if col.lower() == 'impressions')
                conversions_col = next(col for col in df.columns if col.lower() == 'conversions')
                
                # Convert columns to appropriate types
                df[date_col] = pd.to_datetime(df[date_col]).dt.date
                df[spend_col] = pd.to_numeric(df[spend_col])
                df[revenue_col] = pd.to_numeric(df[revenue_col])
                df[clicks_col] = pd.to_numeric(df[clicks_col]).astype(int)
                df[impressions_col] = pd.to_numeric(df[impressions_col]).astype(int)
                df[conversions_col] = pd.to_numeric(df[conversions_col]).astype(int)
                
                # Rename columns to standardized names
                column_mapping = {
                    date_col: 'date',
                    platform_col: 'platform',
                    campaign_col: 'campaign',
                    spend_col: 'spend',
                    revenue_col: 'revenue',
                    clicks_col: 'clicks',
                    impressions_col: 'impressions',
                    conversions_col: 'conversions'
                }
                
                df = df.rename(columns=column_mapping)
                
                return True, df
                
            except Exception as e:
                return False, f"Column validation failed: {str(e)}"
                
        except Exception as e:
            return False, f"CSV validation failed: {str(e)}"
    
    def _create_metrics(self, df):
        """
        Create marketing metrics from the DataFrame
        
        Args:
            df: Pandas DataFrame with validated data
            
        Returns:
            tuple: (success, message)
        """
        try:
            # Process each row of the DataFrame
            for _, row in df.iterrows():
                # Calculate derived metrics
                impressions = row['impressions']
                clicks = row['clicks']
                conversions = row['conversions']
                cost = row['spend']
                revenue = row['revenue']
                
                ctr = (clicks / impressions * 100) if impressions > 0 else 0
                cvr = (conversions / clicks * 100) if clicks > 0 else 0
                roi = ((revenue - cost) / cost * 100) if cost > 0 else 0
                cpc = (cost / clicks) if clicks > 0 else 0
                
                # Create a new marketing metric
                MarketingMetric.objects.create(
                    user=self.csv_upload.user,
                    csv_upload=self.csv_upload,
                    date=row['date'],
                    platform=row['platform'],
                    campaign_name=row['campaign'],
                    impressions=impressions,
                    clicks=clicks,
                    conversions=conversions,
                    cost=Decimal(str(cost)),
                    revenue=Decimal(str(revenue)),
                    ctr=Decimal(str(round(ctr, 2))),             # Changed from click_through_rate
                    conversion_rate=Decimal(str(round(cvr, 2))),
                    roi=Decimal(str(round(roi, 2))),
                    cost_per_click=Decimal(str(round(cpc, 2)))   # Changed from average_cpc
                )
                
                self.metrics_created += 1
                
            return True, f"Created {self.metrics_created} marketing metrics"
            
        except Exception as e:
            return False, f"Error creating metrics: {str(e)}"
    
    def _generate_insights(self):
        """
        Generate insights based on the created metrics
        
        Returns:
            tuple: (success, message)
        """
        try:
            # Get metrics for this CSV upload
            metrics = MarketingMetric.objects.filter(csv_upload=self.csv_upload)
            
            if not metrics.exists():
                return False, "No metrics found to generate insights"
                
            # Calculate aggregate metrics
            total_impressions = sum(metric.impressions for metric in metrics)
            total_clicks = sum(metric.clicks for metric in metrics)
            total_conversions = sum(metric.conversions for metric in metrics)
            total_cost = sum(metric.cost for metric in metrics)
            total_revenue = sum(metric.revenue for metric in metrics)
            
            # Calculate overall metrics
            overall_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            overall_cvr = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
            overall_roi = ((total_revenue - total_cost) / total_cost * 100) if total_cost > 0 else 0
            overall_cpc = (total_cost / total_clicks) if total_clicks > 0 else 0
            
            # Generate basic insights
            insights = [
                {
                    'title': 'Campaign Performance Overview',
                    'content': f"Your campaigns generated {total_impressions:,} impressions, {total_clicks:,} clicks, and {total_conversions:,} conversions. The overall ROI was {overall_roi:.2f}%.",
                    'category': 'overview'
                },
                {
                    'title': 'ROI Analysis',
                    'content': f"Your return on investment is {overall_roi:.2f}%. " + ("This positive ROI indicates your marketing spend is generating profit." if overall_roi > 0 else "The negative ROI suggests a need to optimize your campaigns for better returns."),
                    'category': 'roi'
                },
                {
                    'title': 'Conversion Optimization',
                    'content': f"Your conversion rate is {overall_cvr:.2f}%. " + ("This is above the typical industry average." if overall_cvr > 3.0 else "Consider optimizing your landing pages and targeting to improve conversions."),
                    'category': 'conversion'
                }
            ]
            
            # Add platform-specific insights if multiple platforms
            platforms = set(metric.platform for metric in metrics)
            if len(platforms) > 1:
                platform_metrics = {}
                
                for platform in platforms:
                    platform_data = metrics.filter(platform=platform)
                    p_impressions = sum(metric.impressions for metric in platform_data)
                    p_clicks = sum(metric.clicks for metric in platform_data)
                    p_conversions = sum(metric.conversions for metric in platform_data)
                    p_cost = sum(metric.cost for metric in platform_data)
                    p_revenue = sum(metric.revenue for metric in platform_data)
                    
                    p_ctr = (p_clicks / p_impressions * 100) if p_impressions > 0 else 0
                    p_cvr = (p_conversions / p_clicks * 100) if p_clicks > 0 else 0
                    p_roi = ((p_revenue - p_cost) / p_cost * 100) if p_cost > 0 else 0
                    
                    platform_metrics[platform] = {
                        'ctr': p_ctr,
                        'cvr': p_cvr,
                        'roi': p_roi
                    }
                    
                    insights.append({
                        'title': f'{platform} Performance',
                        'content': f"Your {platform} campaigns had a CTR of {p_ctr:.2f}%, conversion rate of {p_cvr:.2f}%, and ROI of {p_roi:.2f}%.",
                        'category': 'platform'
                    })
                
                # Compare platforms
                top_platform = max(platform_metrics.items(), key=lambda x: x[1]['roi'])
                insights.append({
                    'title': 'Platform Comparison',
                    'content': f"{top_platform[0]} is your best performing platform with an ROI of {top_platform[1]['roi']:.2f}%. Consider reallocating budget to favor this platform.",
                    'category': 'recommendation'
                })
            
            # Save insights
            for insight_data in insights:
                AiInsight.objects.create(
                    user=self.csv_upload.user,
                    title=insight_data['title'],
                    content=insight_data['content'],
                    category=insight_data['category']
                )
                self.insights_created += 1
                
            return True, f"Generated {self.insights_created} insights"
            
        except Exception as e:
            return False, f"Error generating insights: {str(e)}"