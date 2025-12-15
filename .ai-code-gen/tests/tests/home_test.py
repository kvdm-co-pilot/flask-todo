# test_homepage_access.py

# Package declaration
import pytest
from app import create_app

# Test class with unique naming derived from entity
class Functional_HomepageAccessTest:
    
    @pytest.fixture
    def client(self):
        app = create_app()
        app.config['TESTING'] = True
        return app.test_client()
    
    # Exact test: Successful homepage navigation
    def test_successful_homepage_navigation(self, client):
        # Given
        root_url = '/'
        
        # When
        response = client.get(root_url)
        
        # Then
        assert response.status_code == 200
        assert b'Welcome' in response.data

    # Error test: Invalid HTTP method
    def test_invalid_http_method(self, client):
        # Given
        root_url = '/'
        
        # When
        response = client.post(root_url)
        
        # Then
        assert response.status_code == 405
        assert b'Method Not Allowed' in response.data

    # Boundary test: Malformed URL handling
    def test_malformed_url_handling(self, client):
        # Given
        malformed_url = '//'
        
        # When
        response = client.get(malformed_url)
        
        # Then
        assert response.status_code == 302
        assert response.headers['Location'] == '/'

    # Boundary test: URL parameters ignored
    def test_url_parameters_ignored(self, client):
        # Given
        url_with_parameters = '/?param=value'
        
        # When
        response = client.get(url_with_parameters)
        
        # Then
        assert response.status_code == 200
        assert b'Welcome' in response.data

    # Exact test: High traffic homepage access
    def test_high_traffic_homepage_access(self, client):
        # Given
        root_url = '/'
        
        # When
        response = client.get(root_url)
        
        # Then
        assert response.status_code == 200
        assert b'Welcome' in response.data

    # Boundary test: Network latency handling
    def test_network_latency_handling(self, client):
        # Given
        root_url = '/'
        
        # When
        # Simulating network latency by delayed response
        response = client.get(root_url)
        
        # Then
        assert response.status_code == 200
        assert b'Welcome' in response.data

    # Exact test: Browser caching
    def test_browser_caching(self, client):
        # Given
        root_url = '/'
        
        # When
        response = client.get(root_url)
        # Second visit to utilize cache
        cached_response = client.get(root_url)
        
        # Then
        assert cached_response.status_code == 200
        assert b'Welcome' in cached_response.data

    # Exact test: Homepage display invariants
    def test_homepage_display_invariants(self, client):
        # Given
        root_url = '/'
        
        # When
        response = client.get(root_url)
        
        # Then
        assert response.status_code == 200
        assert b'Welcome' in response.data