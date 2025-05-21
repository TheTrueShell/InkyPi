import unittest
from unittest.mock import Mock
from PIL import Image
from plugins.google_calendar.google_calendar import GoogleCalendarPlugin

class TestGoogleCalendarPlugin(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures, if any."""
        self.plugin = GoogleCalendarPlugin()
        
        # Create a mock device_config
        self.mock_device_config = Mock()
        
        # Mock the get_resolution method to return a specific resolution
        self.mock_device_config.get_resolution = Mock(return_value=(800, 600))
        self.mock_device_config.width = 800 # Also set width and height attributes directly as per generate_image
        self.mock_device_config.height = 600

        # Mock the get_config method for 'orientation'
        # Note: The current google_calendar.py doesn't use orientation, but good to have for future.
        self.mock_device_config.get_config = Mock(return_value='horizontal')


    def test_generate_settings_template(self):
        """Test that generate_settings_template includes style_settings."""
        settings_template = self.plugin.generate_settings_template()
        self.assertIn('style_settings', settings_template)
        self.assertTrue(settings_template['style_settings'])

    def test_generate_image_placeholder(self):
        """Test the placeholder image generation."""
        # Empty settings for now, as API interaction is not yet implemented/mocked
        settings = {} 
        
        # The generate_image method in the plugin currently expects device_config['width'] and device_config['height']
        # So, instead of passing the mock directly, we might need to pass a dict,
        # or ensure the mock behaves like a dict for those keys if the plugin code is not changed.
        # For now, the plugin code accesses device_config['width'] and device_config['height'].
        # Let's make the mock_device_config a dictionary for this test to match current plugin implementation.
        
        device_config_dict = {
            'width': self.mock_device_config.width,
            'height': self.mock_device_config.height,
            'get_resolution': self.mock_device_config.get_resolution, # Keep methods if needed elsewhere
            'get_config': self.mock_device_config.get_config
        }

        image = self.plugin.generate_image(settings=settings, device_config=device_config_dict)
        
        self.assertIsInstance(image, Image.Image, "The returned object should be a PIL Image.")
        self.assertEqual(image.size, (800, 600), "The image dimensions should match the device config.")

if __name__ == '__main__':
    unittest.main()
