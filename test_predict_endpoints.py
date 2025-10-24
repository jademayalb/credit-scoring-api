"""
Tests for POST prediction endpoints to validate feature simulation functionality.
"""
import pytest
import json
from app import app, fetch_github_data
import pandas as pd


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_client_id():
    """Get a valid client ID from the dataset."""
    df = fetch_github_data()
    return int(df['SK_ID_CURR'].iloc[0])


def test_post_predict_with_client_id_and_modifications(client, sample_client_id):
    """Test POST /predict with client_id and feature modifications."""
    # First, get the baseline prediction
    response_baseline = client.get(f'/predict/{sample_client_id}')
    assert response_baseline.status_code == 200
    baseline_data = json.loads(response_baseline.data)
    baseline_proba = baseline_data['probability']
    
    # Now test with modified feature
    payload = {
        "client_id": sample_client_id,
        "features": {
            "AMT_CREDIT": 300000  # Significantly different value
        }
    }
    
    response = client.post('/predict', 
                          data=json.dumps(payload),
                          content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Verify response structure
    assert 'probability' in data
    assert 'client_id' in data
    assert data['client_id'] == sample_client_id
    assert 'status' in data
    assert data['status'] == 'OK'
    assert 'input_features' in data
    assert 'AMT_CREDIT' in data['input_features']
    
    # Verify that the probability may have changed
    # (it might not change significantly depending on the model and other features)
    modified_proba = data['probability']
    assert isinstance(modified_proba, float)
    assert 0 <= modified_proba <= 1


def test_post_predict_client_id_with_modifications(client, sample_client_id):
    """Test POST /predict/<client_id> with feature modifications."""
    # First, get the baseline prediction
    response_baseline = client.get(f'/predict/{sample_client_id}')
    assert response_baseline.status_code == 200
    baseline_data = json.loads(response_baseline.data)
    baseline_proba = baseline_data['probability']
    
    # Test with modified feature
    payload = {
        "features": {
            "AMT_CREDIT": 300000,
            "AMT_INCOME_TOTAL": 100000
        }
    }
    
    response = client.post(f'/predict/{sample_client_id}',
                          data=json.dumps(payload),
                          content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Verify response structure
    assert 'probability' in data
    assert 'client_id' in data
    assert data['client_id'] == sample_client_id
    assert 'status' in data
    assert data['status'] == 'OK'
    assert 'input_features' in data
    assert 'modifications_applied' in data  # New field for debugging
    
    # Verify modifications_applied contains the changes
    modifications = data['modifications_applied']
    assert 'AMT_CREDIT' in modifications
    assert 'old' in modifications['AMT_CREDIT']
    assert 'new' in modifications['AMT_CREDIT']
    assert modifications['AMT_CREDIT']['new'] == 300000
    
    # Verify that the probability is valid
    modified_proba = data['probability']
    assert isinstance(modified_proba, float)
    assert 0 <= modified_proba <= 1


def test_post_predict_without_client_id(client):
    """Test POST /predict without client_id (new profile)."""
    payload = {
        "features": {
            "AMT_CREDIT": 500000,
            "AMT_INCOME_TOTAL": 150000,
            "AMT_ANNUITY": 25000
        }
    }
    
    response = client.post('/predict',
                          data=json.dumps(payload),
                          content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Verify response structure
    assert 'probability' in data
    assert 'client_id' in data
    assert data['client_id'] is None  # No client_id provided
    assert 'status' in data
    assert data['status'] == 'OK'
    assert 'input_features' in data


def test_post_predict_invalid_payload(client):
    """Test POST /predict with invalid payload."""
    # Empty payload
    response = client.post('/predict',
                          data=json.dumps({}),
                          content_type='application/json')
    assert response.status_code == 400
    
    # Missing features
    response = client.post('/predict',
                          data=json.dumps({"client_id": 12345}),
                          content_type='application/json')
    assert response.status_code == 400


def test_post_predict_nonexistent_client(client):
    """Test POST /predict with non-existent client_id."""
    payload = {
        "client_id": 999999999,  # Non-existent client
        "features": {
            "AMT_CREDIT": 300000
        }
    }
    
    response = client.post('/predict',
                          data=json.dumps(payload),
                          content_type='application/json')
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'erreur' in data
    assert data['status'] == 'NOT_FOUND'


def test_post_predict_client_id_nonexistent(client):
    """Test POST /predict/<client_id> with non-existent client_id."""
    payload = {
        "features": {
            "AMT_CREDIT": 300000
        }
    }
    
    response = client.post('/predict/999999999',
                          data=json.dumps(payload),
                          content_type='application/json')
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'erreur' in data
    assert data['status'] == 'NOT_FOUND'


def test_post_predict_client_id_empty_features(client, sample_client_id):
    """Test POST /predict/<client_id> with empty features (should return original prediction)."""
    payload = {
        "features": {}
    }
    
    response = client.post(f'/predict/{sample_client_id}',
                          data=json.dumps(payload),
                          content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Should work fine with empty features (no modifications)
    assert 'probability' in data
    assert 'modifications_applied' in data
    assert len(data['modifications_applied']) == 0  # No modifications


def test_post_predict_feature_logging(client, sample_client_id, caplog):
    """Test that feature modifications are properly logged."""
    import logging
    
    payload = {
        "client_id": sample_client_id,
        "features": {
            "AMT_CREDIT": 400000
        }
    }
    
    with caplog.at_level(logging.INFO):
        response = client.post('/predict',
                              data=json.dumps(payload),
                              content_type='application/json')
    
    assert response.status_code == 200
    
    # Check if modification was logged
    log_messages = [record.message for record in caplog.records]
    modification_logged = any("Modification appliquée" in msg for msg in log_messages)
    assert modification_logged, "Feature modification should be logged"
