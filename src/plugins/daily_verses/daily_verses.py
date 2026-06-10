import textwrap
import requests
from PIL import Image, ImageDraw, ImageFont
from plugins.base_plugin.base_plugin import BasePlugin

class DailyVersesPlugin(BasePlugin):  # Changed to BasePlugin
    def __init__(self, config):
        super().__init__(config)

    # Added 'settings' parameter to match what the system expects
    def generate_image(self, settings, device_config):
        # 1. Fetch resolution dynamically from device config
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

        # 3. Dynamically size, wrap, and draw the body text
        font_size = 90  # Maximum font cap verified via Photoshop template
        min_font_size = 24
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        
        # Safe bounding box parameters for an 800x480 layout
        max_target_width = 720  # Leaves 40px margins on left/right
        max_target_height = 340 # Leaves room for top margin and citation below

        while font_size >= min_font_size:
            try:
                font = ImageFont.truetype(font_path, font_size)
            except IOError:
                font = ImageFont.load_default()
                break
            
            # Estimate how many characters fit per line at this font size
            avg_char_width = font_size * 0.55
            char_limit = max(10, int(max_target_width / avg_char_width))
            
            # Wrap text and calculate line height with breathing room (1.35x)
            lines = textwrap.wrap(verse_text, width=char_limit)
            line_height = int(font_size * 1.35)
            total_text_height = len(lines) * line_height
            
            # If it fits within our height budget, stop shrinking
            if total_text_height <= max_target_height:
                break
            font_size -= 2  # Shrink and try again

        # Draw the wrapped lines using calculated dynamic spacing
        y_position = 50  # Top margin
        for line in lines:
            draw.text((40, y_position), line, font=font, fill=0) # 40px left margin
            y_position += line_height

        # 4. Draw the citation (dynamically positioned below the text block)
        try:
            # Scale citation size slightly smaller than body text
            citation_size = max(20, int(font_size * 0.65))
            citation_font = ImageFont.truetype(font_path, citation_size)
            text_width = draw.textlength(citation, font=citation_font)
        except IOError:
            citation_font = ImageFont.load_default()
            text_width = 100

        x_position = width - text_width - 40  # Right align with 40px margin
        
        # Place it 30 pixels below the final line of the verse text
        draw.text((x_position, y_position + 30), citation, font=citation_font, fill=0)

        return image