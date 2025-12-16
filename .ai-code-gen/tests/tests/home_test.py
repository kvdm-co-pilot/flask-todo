import unittest
from app import app
from flask import url_for

class TestHomeRoute(unittest.TestCase):
    
    def setUp(self):
        # Given: Set up a test client
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

    def tearDown(self):
        # Clean up after tests if necessary
        self.app_context.pop()

    def test_homepage_loads_successfully(self):
        # When: HTTP request is made to '/'
        response = self.app.get(url_for('home'))

        # Then: Expect a 200 OK response with homepage content
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Homepage Content', response.data)  # Adjust content check as necessary

    def test_homepage_renders_correctly_across_browsers(self):
        # Given: Simulating different browsers
        user_agents = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
                       'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
                       'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/86.0']

        for user_agent in user_agents:
            # When: HTTP request is made with simulated user agent
            response = self.app.get(url_for('home'), headers={'User-Agent': user_agent})

            # Then: Expect consistent rendering
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Homepage Content', response.data)  # Adjust content check as necessary

    def test_homepage_handles_mobile_device_requests(self):
        # Given: Simulating a mobile device request
        mobile_user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'

        # When: HTTP request is made with mobile user agent
        response = self.app.get(url_for('home'), headers={'User-Agent': mobile_user_agent})

        # Then: Expect homepage rendered in mobile-friendly format
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Mobile Homepage Content', response.data)  # Adjust content check as necessary

if __name__ == '__main__':
    unittest.main()