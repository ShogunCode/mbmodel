import unittest
from flask_testing import TestCase
from app import create_app

class TestFlaskApp(TestCase):
    def create_app(self):
        # Here you configure your app for testing and return it
        app = create_app()
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        # Make sure the app does not use the same resources as your production or development environments
        return app

    def test_home_page(self):
        # Test a simple route to see if it works
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Welcome', response.data.decode())

    # Additional tests can be added here
    def test_other_route(self):
        response = self.client.get('/other-route')
        self.assertEqual(response.status_code, 200)
        # More assertions can be added here based on expected outcomes

if __name__ == '__main__':
    unittest.main()
