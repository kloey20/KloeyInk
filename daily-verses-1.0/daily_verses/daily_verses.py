import textwrap
import requests
from PIL import Image, ImageDraw, ImageFont
from plugins.base_plugin.base_plugin import BasePlugin

class DailyVersesPlugin(BasePlugin):
    def __init__(self, config):
        super().__init__(config)

    def generate_image(self, settings, device_config):
        # 1. Fetch resolution dynamically using the working method
        width, height = device_config.get_resolution()
        image = Image.new("L", (width, height), color=255) # 255 = White
        draw = ImageDraw.Draw(image)

        # 2. Fetch the daily verse from the API
        try:
            response = requests.get("https://beta.ourmanna.com/api/v1/get?format=json&order=daily")
            if response.status_code == 200:
                data = response.json()
                verse_text = data["verse"]["details"]["text"]
                citation = f'{data["verse"]["details"]["reference"]} ({data["verse"]["details"]["version"]})'
            else:
                verse_text = "Could not fetch daily verse."
                citation = "API Error"
        except Exception as e:
            verse_text = f"An error occurred: {str(e)}"
            citation = "Error"

        # 3. Static Font Config (Size 32, Line Height 45 to stop overlapping)
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        font = ImageFont.truetype(font_path, 32)
        
        lines = textwrap.wrap(verse_text, width=45)
        y_position = 50   # Starting top margin
        line_height = 45  # Increased from 20 to clear ascenders/descenders

        # Draw the body text
        for line in lines:
            draw.text((40, y_position), line, font=font, fill=0) # 40px left margin
            y_position += line_height

        # 4. Draw the citation (Slightly smaller, right-aligned)
        citation_font = ImageFont.truetype(font_path, 24)
        text_width = draw.textlength(citation, font=citation_font)
        x_position = width - text_width - 40 # 40px right margin
        
        draw.text((x_position, y_position + 20), citation, font=citation_font, fill=0)

        return image