# Marketing Analytics Platform - Django Backend

This directory contains the Django backend for the Marketing Analytics Platform.

## Setup

### Prerequisites

- Python 3.11 or higher
- PostgreSQL database

### Installation

1. Create a virtual environment:
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Create a `.env` file in the `backend` directory
   - Add the following variables:
     ```
     DEBUG=True
     SECRET_KEY=your-secret-key
     DATABASE_URL=postgres://username:password@localhost:5432/marketing_analytics
     ALLOWED_HOSTS=localhost,127.0.0.1
     CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
     ```

5. Run migrations:
   ```
   python manage.py migrate
   ```

6. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

7. Initialize the database with sample data (optional):
   ```
   python manage.py initialize_db
   ```

## Running the Server

```
python manage.py runserver
```

The server will start at http://127.0.0.1:8000/

## API Endpoints

### Authentication
- `POST /api/register/` - Register a new user
- `POST /api/login/` - Login a user
- `POST /api/logout/` - Logout the current user
- `GET /api/user/` - Get the current user's details

### Campaigns
- `GET /api/campaigns/` - List all campaigns
- `POST /api/campaigns/` - Create a new campaign
- `GET /api/campaigns/<id>/` - Get campaign details
- `PUT /api/campaigns/<id>/` - Update a campaign
- `DELETE /api/campaigns/<id>/` - Delete a campaign
- `PUT /api/campaigns/<id>/change_status/` - Change a campaign's status

### CSV Uploads
- `GET /api/csv-uploads/` - List all CSV uploads
- `POST /api/upload-csv/` - Upload a new CSV file
- `GET /api/csv-uploads/<id>/` - Get CSV upload details
- `POST /api/process-csv/<id>/` - Process a CSV file

### Metrics
- `GET /api/metrics/` - List all metrics
- `GET /api/metrics/by_csv_upload/?csv_upload_id=<id>` - Get metrics for a specific CSV upload
- `GET /api/metrics/summary/` - Get summary metrics
- `GET /api/metrics/platforms/` - Get metrics grouped by platform
- `POST /api/calculate-metrics/` - Calculate metrics for a specific dataset

### Insights
- `GET /api/insights/` - List all insights
- `GET /api/insights/by_category/?category=<category>` - Get insights by category
- `POST /api/generate-insights/` - Generate insights from metrics

### API Configurations
- `GET /api/api-configurations/` - List all API configurations
- `POST /api/api-configurations/` - Create a new API configuration
- `GET /api/api-configurations/<id>/` - Get API configuration details
- `PUT /api/api-configurations/<id>/` - Update an API configuration
- `DELETE /api/api-configurations/<id>/` - Delete an API configuration
- `PUT /api/api-configurations/<id>/set_active/` - Set an API configuration as active
- `PUT /api/api-configurations/<id>/verify/` - Verify an API key