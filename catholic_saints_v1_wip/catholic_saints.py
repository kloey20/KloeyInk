#version 1.4.0
import os
from datetime import datetime
import requests
import logging
from PIL import Image, ImageDraw, ImageFont
from plugins.base_plugin.base_plugin import BasePlugin

logger = logging.getLogger(__name__)


class CatholicSaintsPlugin(BasePlugin):
    def generate_settings_template(self):
        """Registers and requires the global Magisterium API key within InkyPi."""
        template_params = super().generate_settings_template()
        template_params['api_key'] = {
            "required": True,
            "service": "Magisterium AI",
            "expected_key": "MAGISTERIUM_SECRET"
        }
        template_params['style_settings'] = False
        return template_params

    def fetch_saint_data(self, api_key):
        """Fetches formatted saint text metadata from the Magisterium AI API."""
        today_str = datetime.now().strftime("%Y-%m-%d")
        url = "https://www.magisterium.com/api/v1/search"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": (
                f"Provide the patron saint on {today_str}. Format your response "
                "exactly like this on separate lines with no extra text:\n"
                "Name: [Insert Name]\n"
                "Lifespan: [Insert Lifespan]\n"
                "Quote: [Insert Quote]\n"
                "Description: [Insert Description/Miracles]"
            )
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            raw_text = data.get("results", data.get("response", ""))
            return self.parse_saint_text(raw_text)
        except Exception as e:
            logger.error(f"Error fetching data from Magisterium AI: {e}")
            return self.get_fallback_data()

    def fetch_wikipedia_image_url(self, saint_name):
        """Queries Wikipedia's Pageimages API to safely locate an authentic portrait."""
        # Sanitize common prefix naming to maximize Wikipedia's search index match rate
        search_title = saint_name.replace("St.", "Saint")
        
        url = "https://en.wikipedia.org/w/api.php"
        
        # User-Agent header prevents Wikipedia from throttling or dropping the connection
        headers = {
            "User-Agent": "InkyPiSaintPlugin/1.4 (contact@example.com; local-eink-device)"
        }
        
        params = {
            "action": "query",
            "titles": search_title,
            "prop": "pageimages",
            "piprop": "thumbnail",
            "pithumbsize": 500,  
            "format": "json",
            "redirects": 1
        }
        
        try:
            logger.info(f"Searching Wikipedia illustrations for: {search_title}")
            response = requests.get(url, params=params, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                pages = data.get("query", {}).get("pages", {})
                for page_id, page_data in pages.items():
                    if "thumbnail" in page_data:
                        return page_data["thumbnail"].get("source")
        except Exception as e:
            logger.error(f"Failed to discover image tracking data from Wikipedia: {e}")
        return None

    def get_fallback_data(self):
        """Reliable backup dataset structural baseline."""
        return {
            "Name": "St. Thomas Aquinas",
            "Lifespan": "1225 - 1274 AD",
            "Quote": '"To one who has faith, no explanation is necessary."',
            "Description": "Dominican friar, philosopher, and Doctor of the Church. He synthesized Aristotelian philosophy with Christian theology.",
        }

    def parse_saint_text(self, raw_text):
        """Parses raw text block line-by-line using fuzzy key evaluation rules."""
        parsed_data = {
            "Name": "Unknown Saint",
            "Lifespan": "Unknown",
            "Quote": "No quote available.",
            "Description": "No description available.",
        }

        if not raw_text:
            return parsed_data

        lines = raw_text.split("\n")
        for line in lines:
            if ":" in line:
                parts = line.split(":", 1)
                # Strip markdown bold markers (**Key:**) often returned by LLMs
                key = parts[0].replace("*", "").replace("_", "").strip().lower()
                value = parts[1].strip()
                
                if "name" in key:
                    parsed_data["Name"] = value
                elif "lifespan" in key or "life" in key:
                    parsed_data["Lifespan"] = value
                elif "quote" in key:
                    parsed_data["Quote"] = value
                elif "description" in key or "miracle" in key:
                    parsed_data["Description"] = value

        return parsed_data

    def wrap_text(self, text, font, max_width, draw):
        """Wraps text safely inside horizontal pixel boundaries."""
        words = text.split(" ")
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            test_line = " ".join(current_line)
            bbox = draw.textbbox((0, 0), test_line, font=font)
            line_width = bbox[2] - bbox[0]

            if line_width > max_width:
                current_line.pop()
                lines.append(" ".join(current_line))
                current_line = [word]

        if current_line:
            lines.append(" ".join(current_line))

        return lines

    def generate_image(self, settings, device_config):
        """Main rendering engine executed natively by the InkyPi runner cycle."""
        logger.info("=== Catholic Saints Plugin: Starting image generation ===")
        
        api_key = device_config.load_env_key("MAGISTERIUM_SECRET")
        if not api_key:
            logger.error("Magisterium API Key (MAGISTERIUM_SECRET) not configured in environment")
            raise RuntimeError("Magisterium API Key not configured.")

        width, height = device_config.get_resolution()
        
        # 1. Gather API Content
        saint = self.fetch_saint_data(api_key)

        theme = settings.get("display_theme", "light")
        base_font_size = int(settings.get("base_font_size", 16))

        bg_color = 255 if theme == "light" else 0
        text_color = 0 if theme == "light" else 255

        # Initialize canvas background layer 
        image = Image.new("L", (width, height), color=bg_color)
        draw = ImageDraw.Draw(image)

        # 2. Extract System Fonts
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        try:
            font_name = ImageFont.truetype(font_path, base_font_size + 6)
            font_meta = ImageFont.truetype(font_path, base_font_size)
            font_quote = ImageFont.truetype(font_path, base_font_size + 2)
            font_body = ImageFont.truetype(font_path, base_font_size)
        except IOError:
            font_name = font_meta = font_quote = font_body = ImageFont.load_default()

        # 3. Handle Horizontal Sizing Layout Calculations
        image_zone_width = width // 3
        text_width_budget = width - (image_zone_width + 40)
        text_start_x = image_zone_width + 20

        # Define internal bounding dimensions for image scaling
        img_w = image_zone_width - 20
        img_h = height - 20

        # 4. Fetch and mount Wikipedia Art Layer
        wiki_image_url = self.fetch_wikipedia_image_url(saint["Name"])
        image_rendered = False

        if wiki_image_url:
            try:
                logger.info(f"Downloading portrait asset: {wiki_image_url}")
                # Leverage InkyPi's memory-safe image download tool
                saint_portrait = self.image_loader.from_url(wiki_image_url, (img_w, img_h), timeout_ms=30000)
                if saint_portrait:
                    # Explicit conversion to Grayscale prevents layout bitstream crashes
                    saint_portrait = saint_portrait.convert("L")
                    image.paste(saint_portrait, (10, 10))
                    image_rendered = True
            except Exception as img_err:
                logger.error(f"Failed to cleanly stitch image into main frame context: {img_err}")

        # Fallback framing if no historical portrait is mapped out on Wikipedia
        if not image_rendered:
            draw.rectangle(
                [10, 10, image_zone_width - 10, height - 10],
                outline=text_color,
                width=2,
            )
            draw.text((20, height // 2), "[No Photo]", fill=text_color, font=font_meta)

        # 5. Set up Vertical Grid Targets (10% Name / 40% Quote / 50% Description)
        name_zone_height = int(height * 0.10)
        quote_zone_height = int(height * 0.40)

        y_name_start = 20
        y_quote_start = y_name_start + name_zone_height + 10
        y_desc_start = y_quote_start + quote_zone_height + 10

        # --- Draw Section 1: Name & Lifespan ---
        draw.text((text_start_x, y_name_start), saint["Name"], fill=text_color, font=font_name)
        draw.text((text_start_x, y_name_start + base_font_size + 10), f"Lifespan: {saint['Lifespan']}", fill=text_color, font=font_meta)

        # --- Draw Section 2: Block Quote ---
        wrapped_quote = self.wrap_text(saint["Quote"], font_quote, text_width_budget, draw)
        current_y = y_quote_start
        for line in wrapped_quote:
            if current_y + base_font_size > y_desc_start: 
                break  # Prevents overlapping text
            draw.text((text_start_x, current_y), line, fill=text_color, font=font_quote)
            current_y += (base_font_size + 8)

        # --- Draw Section 3: Biography Description ---
        wrapped_desc = self.wrap_text(saint["Description"], font_body, text_width_budget, draw)
        current_y = y_desc_start
        for line in wrapped_desc:
            if current_y + base_font_size > height - 10: 
                break  # Screen edge collision guard
            draw.text((text_start_x, current_y), line, fill=text_color, font=font_body)
            current_y += (base_font_size + 6)

        logger.info("=== Catholic Saints Plugin: Image generation complete ===")
        return image