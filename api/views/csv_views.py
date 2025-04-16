from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from ..authentication import CsrfExemptSessionAuthentication
from rest_framework.authentication import TokenAuthentication

from django.conf import settings
import os
import uuid

from ..models import CsvUpload
from ..serializers import CsvUploadSerializer
from ..csv_processor import CSVProcessor

class UploadCsvView(APIView):
    """
    API view for uploading CSV files
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, CsrfExemptSessionAuthentication]
    parser_classes = [MultiPartParser, FormParser]
    
    def get(self, request):
        """Return information about CSV upload functionality and list of uploads"""
        # Get user's CSV uploads
        csv_uploads = CsvUpload.objects.filter(user=request.user).order_by('-uploaded_at')
        serializer = CsvUploadSerializer(csv_uploads, many=True)
        
        return Response({
            'message': 'Use POST method to upload a CSV file',
            'allowed_formats': 'csv',
            'max_size': '10MB',
            'uploads': serializer.data
        })
    
    def post(self, request):
        try:
            # Get file from request
            csv_file = request.FILES.get('file')
            if not csv_file:
                return Response(
                    {'error': 'No file provided'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check file extension
            if not csv_file.name.endswith('.csv'):
                return Response(
                    {'error': 'Only CSV files are allowed'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create upload directory if it doesn't exist
            upload_dir = settings.UPLOAD_DIR
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate unique filename to prevent overwrites
            unique_filename = f"{uuid.uuid4()}_{csv_file.name}"
            file_path = os.path.join(upload_dir, unique_filename)
            
            # Save the file
            with open(file_path, 'wb+') as destination:
                for chunk in csv_file.chunks():
                    destination.write(chunk)
            
            # Create CSV upload record
            csv_upload = CsvUpload.objects.create(
                user=request.user,
                filename=csv_file.name,
                file_path=file_path,
                processed=False
            )
            
            # Process the file
            processor = CSVProcessor(csv_upload.id)
            success, message = processor.process()
            
            # Refresh the CSV upload record to get updated fields
            csv_upload.refresh_from_db()
            
            # Return the CSV upload record
            serializer = CsvUploadSerializer(csv_upload)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response(
                {'error': f'Upload failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request, pk=None):
        try:
            # Get the CSV upload record
            csv_upload = CsvUpload.objects.get(pk=pk)
            
            # Check ownership
            if csv_upload.user != request.user and not request.user.is_staff:
                return Response(
                    {'error': 'You do not have permission to delete this file'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Delete the physical file
            if csv_upload.file_path and os.path.exists(csv_upload.file_path):
                os.remove(csv_upload.file_path)
            
            # Delete the record
            csv_upload.delete()
            
            return Response(
                {'message': 'File deleted successfully'}, 
                status=status.HTTP_200_OK
            )
                
        except CsvUpload.DoesNotExist:
            return Response(
                {'error': 'CSV upload not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ProcessCsvView(APIView):
    """
    API view for processing an existing CSV file
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        try:
            # Get the CSV upload record
            csv_upload = CsvUpload.objects.get(pk=pk)
            
            # Check ownership
            if csv_upload.user != request.user and not request.user.is_staff:
                return Response(
                    {'error': 'You do not have permission to process this file'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Process the file
            processor = CSVProcessor(csv_upload.id)
            success, message = processor.process()
            
            if success:
                serializer = CsvUploadSerializer(csv_upload)
                return Response({
                    'message': message,
                    'csv_upload': serializer.data
                })
            else:
                return Response(
                    {'error': message}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except CsvUpload.DoesNotExist:
            return Response(
                {'error': 'CSV upload not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )