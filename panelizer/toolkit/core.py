import os
from pathlib import Path
from typing import Tuple

from PIL import Image, ImageOps

# We don't strictly need custom Errors here anymore since we catch everything,
# but keeping the import doesn't hurt if you use it elsewhere.
from textual_neon import Errors


class Toolkit:
    """
    A static container for all image processing business logic for Panelizer.
    """
    RATIO_MAP = {
        "3:4": 3 / 4,
        "4:5": 4 / 5,
        "2:3": 2 / 3,
        "9:16": 9 / 16,
    }
    COLOR_MAP = {
        "white": "#FFFFFF",
        "black": "#000000",
        "lightgray": "#D3D3D3",
        "darkgray": "#333333",
    }

    @staticmethod
    def process_image(payload: tuple[str, dict]) -> bool:
        """
        The main worker function used by the LoadingScreen.
        Accepts a tuple of (file_path_string, settings_dict).

        Returns:
            True -> Success
            False -> Failure (Sidecar .failed file created)
        """
        file_path_str, settings = payload
        path = Path(file_path_str)
        if not path.exists():
            return False

        try:
            with Image.open(path) as img:
                if settings.get("split_wide_images") and (img.width / img.height) > 1.8:
                    left_img, right_img = Toolkit._split_image(img)
                    Toolkit._render_panel(
                        left_img,
                        settings,
                        path.stem + "_L",
                        path.parent
                    )
                    Toolkit._render_panel(
                        right_img,
                        settings,
                        path.stem + "_R",
                        path.parent
                    )
                else:
                    Toolkit._render_panel(
                        img,
                        settings,
                        path.stem,
                        path.parent
                    )

            return True

        except Exception as e:
            output_dir = path.parent / "panelizer_output"
            output_dir.mkdir(exist_ok=True)

            fail_file = output_dir / f"{path.name}.failed"
            error_msg = (
                f"{path.name} export has failed. "
                f"Either there is a bug, or the image is corrupted.\n"
                f"Details: {e}"
            )
            # noinspection PyBroadException
            try:
                with open(fail_file, "w", encoding="utf-8") as f:
                    f.write(error_msg)
            except Exception:
                pass

            return False

    @staticmethod
    def _split_image(img: Image.Image) -> Tuple[Image.Image, Image.Image]:
        """Splits an image vertically into two halves (Left, Right)."""
        width, height = img.size
        mid_x = width // 2

        left = img.crop((0, 0, mid_x, height))
        right = img.crop((mid_x, 0, width, height))

        return left, right

    @staticmethod
    def _render_panel(
            img: Image.Image,
            settings: dict,
            stem: str,
            source_dir: Path
    ) -> str:
        """
        Internal helper to apply layout, create canvas, and save the file.
        Returns the name of the saved file.
        """
        layout = settings.get("layout")
        canvas_height = settings.get("canvas_height", 2500)
        bg_color_name = settings.get("background_color", "white")
        bg_hex = Toolkit.COLOR_MAP.get(bg_color_name, "#FFFFFF")

        if layout == "uniform":
            canvas, final_img, pos = Toolkit._apply_uniform_layout(img, canvas_height, settings, bg_hex)
        else:
            canvas, final_img, pos = Toolkit._apply_framing_layout(img, canvas_height, settings, bg_hex)

        canvas.paste(final_img, pos)

        output_dir = source_dir / "panelizer_output"
        output_dir.mkdir(exist_ok=True)

        save_path = output_dir / f"{stem}_panel.jpg"

        if canvas.mode in ("RGBA", "P"):
            canvas = canvas.convert("RGB")

        canvas.save(save_path, quality=95, subsampling=0)

        return save_path.name

    @staticmethod
    def _apply_framing_layout(
            img: Image.Image,
            target_h: int,
            settings: dict,
            bg_color: str
    ) -> Tuple[Image.Image, Image.Image, Tuple[int, int]]:
        """
        Calculates framing layout:
        1. Determines canvas width from Aspect Ratio setting.
        2. Calculates 'safe area' inside padding.
        3. Fits image into a safe area (contain).
        """
        ratio_str = settings.get("canvas_ratio", "4:5")
        ratio = Toolkit.RATIO_MAP.get(ratio_str, 4 / 5)
        target_w = int(target_h * ratio)

        canvas = Image.new("RGB", (target_w, target_h), bg_color)

        pad_data = settings.get("padding", {})
        pad_l = int(target_w * (pad_data.get("left", 0) / 100))
        pad_r = int(target_w * (pad_data.get("right", 0) / 100))
        pad_t = int(target_h * (pad_data.get("top", 0) / 100))
        pad_b = int(target_h * (pad_data.get("bottom", 0) / 100))

        safe_w = target_w - pad_l - pad_r
        safe_h = target_h - pad_t - pad_b

        resized_img = ImageOps.contain(img, (safe_w, safe_h), method=Image.Resampling.LANCZOS)

        res_w, res_h = resized_img.size
        x_pos = pad_l + ((safe_w - res_w) // 2)
        y_pos = pad_t + ((safe_h - res_h) // 2)

        return canvas, resized_img, (x_pos, y_pos)

    @staticmethod
    def _apply_uniform_layout(
            img: Image.Image,
            target_h: int,
            settings: dict,
            bg_color: str
    ) -> Tuple[Image.Image, Image.Image, Tuple[int, int]]:
        """
        Calculates uniform layout:

        Outward: Image = target_h. Canvas = target_h + 2*Border. (Image fully visible).
        Inward: Image = target_h. Canvas = target_h. (Border eats into image edges / Cropped).
        """
        pad_data = settings.get("padding", {})
        border_pct = pad_data.get("uniform", 5)
        orientation = pad_data.get("orientation", "inward")
        border_px = int(target_h * (border_pct / 100))

        new_h = target_h
        if img.height > 0:
            scale = new_h / img.height
        else:
            scale = 1.0
        new_w = int(img.width * scale)

        base_img = img.resize((new_w, new_h), resample=Image.Resampling.LANCZOS)

        if orientation == "outward":
            # OUTWARD: Image stays unchanged, and the canvas grows.
            resized_img = base_img
            canvas_w = new_w + (border_px * 2)
            canvas_h = new_h + (border_px * 2)
            pos = (border_px, border_px)

        else:
            # INWARD: Image gets cropped, and the canvas keeps the exact aspect ratio.
            canvas_w = new_w
            canvas_h = new_h
            crop_box = (
                border_px,
                border_px,
                new_w - border_px,
                new_h - border_px
            )

            if crop_box[2] <= crop_box[0] or crop_box[3] <= crop_box[1]:
                mid_x, mid_y = new_w // 2, new_h // 2
                crop_box = (mid_x, mid_y, mid_x + 1, mid_y + 1)

            resized_img = base_img.crop(crop_box)
            pos = (border_px, border_px)

        canvas = Image.new("RGB", (canvas_w, canvas_h), bg_color)

        return canvas, resized_img, pos