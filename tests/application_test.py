import os
import application
import unittest
import tempfile

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        application.app.config['TESTING'] = True
        self.app = application.app.test_client()

    def test_mapview(self):
        response = self.app.get('/')
        self.assertIn("maps.googleapis.com", response.data)

    def test_foodtrucks(self):
        response = self.app.get('/foodtrucks?location_box=37.769222,-122.434071,37.780637,-122.40476')
        self.assertIn("Sunrise", response.data)

if __name__ == '__main__':
    unittest.main()