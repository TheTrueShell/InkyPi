import os
import logging
import datetime
import pytz # For timezone handling
from PIL import Image, ImageDraw, ImageFont
from plugins.base_plugin.base_plugin import BasePlugin

logger = logging.getLogger(__name__)

class GoogleCalendarPlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        # Any specific initialization can go here

    def generate_settings_template(self):
        settings = super().generate_settings_template()
        settings['style_settings'] = True
        return settings

    def generate_image(self, settings, device_config):
        logger.info("Google Calendar Plugin: Generating image...")
        try:
            width = device_config['width']
            height = device_config['height']

            # Create a placeholder image
            img = Image.new('RGB', (width, height), color = (255, 255, 255))
            d = ImageDraw.Draw(img)

            # Add text to the image
            try:
                # Try to load a system font
                font = ImageFont.truetype("arial.ttf", 20)
            except IOError:
                # Fallback to a default font if arial.ttf is not found
                logger.warning("arial.ttf not found, using default font. Text rendering might be suboptimal.")
                font = ImageFont.load_default()
            
            text = "Google Calendar Plugin"
            textwidth, textheight = d.textsize(text, font=font)
            x = (width - textwidth) / 2
            y = (height - textheight) / 2
            d.text((x, y), text, fill=(0,0,0), font=font)

            logger.info("Google Calendar Plugin: Image generated successfully.")
            return img

        except Exception as e:
            logger.error(f"Error generating Google Calendar image: {e}")
            # Optionally, create a simple error image
            img = Image.new('RGB', (width, height), color = (255, 0, 0)) # Red background for error
            d = ImageDraw.Draw(img)
            error_text = "Error"
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except IOError:
                font = ImageFont.load_default()
            textwidth, textheight = d.textsize(error_text, font=font)
            x = (width - textwidth) / 2
            y = (height - textheight) / 2
            d.text((x,y), error_text, fill=(0,0,0), font=font)
            # It's generally better to return a placeholder or error image 
            # rather than raising an error that might halt the entire system.
            # However, if this plugin failing is critical, raising an error might be appropriate.
            # For now, returning an error image.
            # raise RuntimeError(f"Failed to generate Google Calendar image: {e}")
            return img
