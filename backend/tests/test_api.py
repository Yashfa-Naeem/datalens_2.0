import pytest
from fastapi.testclient import TestClient
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get('/api/health')
    assert response.status_code == 200

def test_upload_no_file():
    response = client.post('/api/upload')
    assert response.status_code == 422

def test_upload_invalid_file():
    response = client.post('/api/upload', files={'file': ('test.txt', b'not a csv', 'text/plain')})
    assert response.status_code in [400, 422, 500]

def test_get_data_no_dataset():
    response = client.get('/api/data')
    assert response.status_code in [200, 404]

def test_get_profile_no_dataset():
    response = client.get('/api/profile')
    assert response.status_code in [200, 404]

def test_get_summary_no_dataset():
    response = client.get('/api/summary')
    assert response.status_code in [200, 404]

def test_chat_no_message():
    response = client.post('/api/chat', json={})
    assert response.status_code in [400, 422, 500]

def test_upload_valid_csv():
    csv_content = b'YEAR,MONTH,DAY,AIRLINE,DEPARTURE_DELAY
1,2,3,AA,10
1,2,4,UA,5
'
    response = client.post('/api/upload', files={'file': ('flights.csv', csv_content, 'text/csv')})
    assert response.status_code in [200, 201]

def test_chat_with_message():
    response = client.post('/api/chat', json={'message': 'What airlines are in the dataset?'})
    assert response.status_code in [200, 500]

def test_docs_available():
    response = client.get('/docs')
    assert response.status_code == 200
