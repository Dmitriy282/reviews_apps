import os
import pytest
from unittest.mock import patch
from app import app, db

@pytest.fixture
def client():
    # Configuration for tests: use In-Memory SQLite instead of Postgres
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'    
    with app.app_context():
        db.create_all()
        with app.test_client() as c:
            yield c
        db.drop_all()


@patch('app.cache.incr')
@patch('app.LogEntry.query')
def test_index_get(mock_query, mock_incr, client):
    """Test GET request to the main page"""
    # Mock Redis
    mock_incr.return_value = 42
    
    # Mock DB query (return empty list of entries)
    mock_query.order_by.return_value.all.return_value = []

    response = client.get('/')
    assert response.status_code == 200
    
    # Verify the correct text is on the page
    html = response.data.decode('utf-8')
    assert "Space Explorer Logbook" in html
    assert "42" in html # Value from Redis

@patch('app.cache.incr')
def test_index_post_success(mock_incr, client):
    """Test successful addition of a new planet (POST)"""
    mock_incr.return_value = 43
    
    response = client.post('/', data={
        'planet_name': 'Test Planet X',
        'description': 'A very nice test planet'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    
    # The entry should appear on the page
    assert "Test Planet X" in html
    assert "A very nice test planet" in html
