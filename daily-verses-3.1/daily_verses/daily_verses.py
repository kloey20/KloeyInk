#version 3.1.0
import textwrap
import requests
import json
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from plugins.base_plugin.base_plugin import BasePlugin


class DailyVersesPlugin(BasePlugin):
    def __init__(self, config):
        super().__init__(config)
        # Define a path for a local cache file inside the plugin folder
        self.cache_file = os.path.join(os.path.dirname(__file__), "verse_cache.json")

    def generate_image(self, settings, device_config):
        # 1. Fetch resolution dynamically from device config
        width, height = device_config.get_resolution()
        image = Image.new("L", (width, height), color=255)  # 255 = White
        draw = ImageDraw.Draw(image)

        verse_mode = settings.get("verse_mode", "daily")
        
        # NEW: Check if the "Automatically Update Daily" toggle is turned on
        # Web forms pass checkboxes as "true" strings
        auto_daily = settings.get("auto_daily", "false") == "true"
        today_str = datetime.now().strftime("%Y-%m-%d")

        verse_text = ""
        citation = ""
        used_cache = False

        # NEW: Try to read from local cache if auto_daily is enabled
        if auto_daily and os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r") as f:
                    cache_data = json.load(f)
                # If the cached verse belongs to today, use it!
                if cache_data.get("date") == today_str and cache_data.get("mode") == verse_mode:
                    verse_text = cache_data.get("text", "")
                    citation = cache_data.get("citation", "")
                    used_cache = True
            except Exception:
                pass  # Fall back to API if cache file is corrupted

        # 2. Fetch the verse from the API (Only if we didn't use the cache)
        if not used_cache:
            try:
                url = f"https://beta.ourmanna.com/api/v1/get?format=json&order={verse_mode}"
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    verse_text = data["verse"]["details"]["text"]
                    citation = f'{data["verse"]["details"]["reference"]} ({data["verse"]["details"]["version"]})'
                    
                    # NEW: Save this fresh data to the cache for the rest of today
                    if auto_daily:
                        with open(self.cache_file, "w") as f:
                            json.dump({
                                "date": today_str,
                                "mode": verse_mode,
                                "text": verse_text,
                                "citation": citation
                            }, f)
                else:
                    verse_text = "Could not fetch daily verse."
                    citation = "API Error"
            except Exception as e:
                verse_text = f"An error occurred: {str(e)}"
                citation = "Error"

        # 3. Dynamically size, wrap, and draw the body text
        font_size = int(settings.get("font_cap", 90))
        min_font_size = 24
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

        max_target_width = width - 80
        max_target_height = height - 140

        while font_size >= min_font_size:
            try:
                font = ImageFont.truetype(font_path, font_size)
            except IOError:
                font = ImageFont.load_default()
                break

            avg_char_width = font_size * 0.55
            char_limit = max(10, int(max_target_width / avg_char_width))

            lines = textwrap.wrap(verse_text, width=char_limit)
            line_height = int(font_size * 1.35)
            total_text_height = len(lines) * line_height

            if total_text_height <= max_target_height:
                break
            font_size -= 2

        y_position = 50
        for line in lines:
            draw.text((40, y_position), line, font=font, fill=0)
            y_position += line_height

        # 4. Draw the citation
        try:
            citation_size = max(20, int(font_size * 0.65))
            citation_font = ImageFont.truetype(font_path, citation_size)
            text_width = draw.textlength(citation, font=citation_font)
        except IOError:
            citation_font = ImageFont.load_default()
            text_width = 100

        x_position = width - text_width - 40
        draw.text((x_position, y_position + 30), citation, font=citation_font, fill=0)

        return image