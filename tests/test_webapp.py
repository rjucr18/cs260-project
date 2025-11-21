"""Unit tests for webapp functionality"""
import pytest
import json
from webapp.app import create_app


@pytest.fixture
def client():
    """Create test client"""
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'ok'


def test_index_page(client):
    """Test that index page loads"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'SVEN' in response.data


def test_generate_missing_prompt(client):
    """Test generate endpoint with missing prompt"""
    response = client.post('/generate', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data


def test_generate_empty_prompt(client):
    """Test generate endpoint with empty prompt"""
    response = client.post('/generate', json={'prompt': ''})
    assert response.status_code == 400


def test_generate_secure_mode(client):
    """Test generate endpoint in secure mode"""
    response = client.post('/generate', json={
        'prompt': 'def test(): pass',
        'mode': 'secure',
        'max_length': 32,
        'temperature': 0.8
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'secure' in data
    assert 'secure_meta' in data


def test_generate_vulnerable_mode(client):
    """Test generate endpoint in vulnerable mode"""
    response = client.post('/generate', json={
        'prompt': 'def test(): pass',
        'mode': 'vulnerable',
        'max_length': 32,
        'temperature': 0.8
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'vulnerable' in data
    assert 'vulnerable_meta' in data


def test_generate_both_modes(client):
    """Test generate endpoint with both modes"""
    response = client.post('/generate', json={
        'prompt': 'def add(a, b):',
        'mode': 'both',
        'max_length': 64,
        'temperature': 0.5
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'secure' in data
    assert 'vulnerable' in data
    assert 'secure_meta' in data
    assert 'vulnerable_meta' in data


def test_generate_default_params(client):
    """Test generate with default parameters"""
    response = client.post('/generate', json={'prompt': 'def foo():'})
    assert response.status_code == 200
    data = json.loads(response.data)
    # Should default to both modes
    assert 'secure' in data or 'vulnerable' in data


def test_generate_form_data(client):
    """Test generate with form data instead of JSON"""
    response = client.post('/generate', data={
        'prompt': 'def bar():',
        'max_length': '48',
        'temperature': '0.7'
    })
    assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
