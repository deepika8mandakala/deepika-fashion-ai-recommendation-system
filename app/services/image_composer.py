"""Generate outfit board images from dataset product images only."""

from __future__ import annotations

from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFont

from app.models.product import Outfit, RankedProduct


class OutfitImageComposer:
    """Compose retrieved dataset images into a single recommendation board."""

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def compose(self, outfit: Outfit, outfit_index: int) -> str | None:
        """Create and persist a board image for an outfit."""

        items = [
            ("Topwear", outfit.topwear),
            ("Bottomwear", outfit.bottomwear),
            ("Footwear", outfit.footwear),
        ]
        items.extend((f"Accessory {index + 1}", item) for index, item in enumerate(outfit.accessories))
        items = [(label, item) for label, item in items if item and item.product.image_path]
        if not items:
            return None

        tile_width = 260
        tile_height = 360
        margin = 28
        header_height = 72
        columns = min(4, len(items))
        rows = (len(items) + columns - 1) // columns
        width = margin * 2 + columns * tile_width
        height = header_height + margin + rows * tile_height
        board = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(board)
        font = ImageFont.load_default()

        draw.text((margin, 24), f"Generated Outfit Board | Score {outfit.compatibility_score}/100", fill="black", font=font)

        for idx, (slot, ranked_product) in enumerate(items):
            product = ranked_product.product
            col = idx % columns
            row = idx // columns
            x = margin + col * tile_width
            y = header_height + row * tile_height
            self._draw_tile(board, draw, x, y, tile_width, tile_height, slot, ranked_product)

        output_path = self.output_dir / f"outfit_{outfit_index + 1}_{self._slug(items[0][1].product.id)}.jpg"
        board.save(output_path, quality=92)
        return str(output_path.resolve())

    def _draw_tile(
        self,
        board: Image.Image,
        draw: ImageDraw.ImageDraw,
        x: int,
        y: int,
        width: int,
        height: int,
        slot: str,
        ranked_product: RankedProduct,
    ) -> None:
        product = ranked_product.product
        draw.rectangle((x + 8, y + 8, x + width - 8, y + height - 8), outline="#d0d0d0", width=1)
        image_box = (x + 20, y + 34, x + width - 20, y + 250)
        try:
            with Image.open(product.image_path or "") as image:
                image = image.convert("RGB")
                image.thumbnail((image_box[2] - image_box[0], image_box[3] - image_box[1]))
                paste_x = image_box[0] + ((image_box[2] - image_box[0]) - image.width) // 2
                paste_y = image_box[1] + ((image_box[3] - image_box[1]) - image.height) // 2
                board.paste(image, (paste_x, paste_y))
        except Exception:
            draw.rectangle(image_box, fill="#f2f2f2", outline="#cccccc")
            draw.text((image_box[0] + 10, image_box[1] + 90), "Image unavailable", fill="black")

        draw.text((x + 20, y + 14), slot, fill="#333333")
        name_lines = textwrap.wrap(product.product_display_name, width=28)[:3]
        for line_index, line in enumerate(name_lines):
            draw.text((x + 20, y + 262 + line_index * 16), line, fill="black")
        draw.text((x + 20, y + 318), f"{product.article_type} | {product.usage}", fill="#555555")
        draw.text((x + 20, y + 334), f"Item score: {ranked_product.score}/100", fill="#555555")

    def _slug(self, value: str) -> str:
        return "".join(char if char.isalnum() else "_" for char in value.lower()).strip("_")
