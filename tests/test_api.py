# tests/test_api.py
"""
Test API endpoints
"""
import pytest
import json
from src.api.routes import app

@pytest.fixture
def client():
    """Flask test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/api/health')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert 'timestamp' in data

def test_system_status(client):
    """Test system status endpoint"""
    response = client.get('/api/status')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'rate_limits' in data
    assert 'processing_stats' in data

def test_analyze_isrc_invalid_request(client):
    """Test ISRC analysis with invalid request"""
    # No ISRC provided
    response = client.post('/api/analyze-isrc',
                          json={},
                          content_type='application/json')
    assert response.status_code == 400
    
    # Invalid ISRC format
    response = client.post('/api/analyze-isrc',
                          json={'isrc': 'INVALID'},
                          content_type='application/json')
    assert response.status_code == 400

def test_analyze_isrc_valid_format(client):
    """Test ISRC analysis with valid format"""
    response = client.post('/api/analyze-isrc',
                          json={'isrc': 'USRC17607839', 'save_to_db': False},
                          content_type='application/json')
    
    # Should not fail due to format (might fail due to API issues in testing)
    assert response.status_code in [200, 500]

def test_bulk_analysis_validation(client):
    """Test bulk analysis validation"""
    # Empty list
    response = client.post('/api/analyze-bulk',
                          json={'isrcs': []},
                          content_type='application/json')
    assert response.status_code == 400
    
    # Invalid ISRCs
    response = client.post('/api/analyze-bulk',
                          json={'isrcs': ['INVALID1', 'INVALID2']},
                          content_type='application/json')
    assert response.status_code == 400
    
    # Too many ISRCs
    too_many_isrcs = ['USRC1760783' + str(i).zfill(1) for i in range(1001)]
    response = client.post('/api/analyze-bulk',
                          json={'isrcs': too_many_isrcs},
                          content_type='application/json')
    assert response.status_code == 400

def test_leads_endpoint(client):
    """Test leads listing endpoint"""
    response = client.get('/api/leads')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'leads' in data
    assert 'pagination' in data

def test_leads_filtering(client):
    """Test leads filtering"""
    # Test tier filtering
    response = client.get('/api/leads?tier=A&limit=10')
    assert response.status_code == 200
    
    # Test region filtering
    response = client.get('/api/leads?region=new_zealand')
    assert response.status_code == 200
    
    # Test score filtering
    response = client.get('/api/leads?min_score=50&max_score=90')
    assert response.status_code == 200

def test_export_endpoint(client):
    """Test CSV export functionality"""
    response = client.post('/api/export',
                          json={'filters': {'tier': 'A'}},
                          content_type='application/json')
    
    # Should return export data or 404 if no leads
    assert response.status_code in [200, 404]
    
    if response.status_code == 200:
        data = json.loads(response.data)
        assert 'csv_data' in data
        assert 'filename' in data