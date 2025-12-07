import math
from pathlib import Path
from typing import Tuple, Literal, List

from PIL import Image, ImageOps, UnidentifiedImageError


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

    MIN_SPLIT_ASPECT = 2 / 3
    MAX_STACK_ASPECT = 2.2
    FILENAME_SUFFIX = "_pan"

    @staticmethod
    def prepare_queue(files: List[str], settings: dict) -> List[Tuple[List[str], dict]]:
        """
        Groups files into payloads. Handles logic for stacking landscape images.
        Returns a list of payloads: ([file_paths...], settings_dict)
        """
        if not settings.get("stack_landscape_images"):
            return [([f], settings) for f in files]

        queue = []
        skip_count = 0
        limit = len(files)

        for i in range(limit):
            if skip_count > 0:
                skip_count -= 1
                continue

            current_file = files[i]
            stack_candidates = [current_file]

            if Toolkit._is_stackable(current_file):
                for j in range(1, 3):
                    if i + j < limit:
                        next_file = files[i + j]
                        if Toolkit._are_compatible(current_file, next_file):
                            stack_candidates.append(next_file)
                        else:
                            break
                    else:
                        break
            if len(stack_candidates) > 1:
                queue.append((stack_candidates, settings))
                skip_count = len(stack_candidates) - 1
            else:
                queue.append(([current_file], settings))

        return queue

    @staticmethod
    def get_queue_names(files: List[str], settings: dict) -> List[str]:
        """Generates display names for the Loading Screen."""
        payloads = Toolkit.prepare_queue(files, settings)
        names = []
        for path_list, _ in payloads:
            if len(path_list) > 1:
                names.append(f"Stack ({len(path_list)}): {Path(path_list[0]).name}...")
            else:
                names.append(Path(path_list[0]).name)
        return names

    @staticmethod
    def _is_stackable(file_path: str) -> bool:
        """Checks if an image is suitable for stacking (Wide > 16:9 BUT < 2.2)."""
        try:
            with Image.open(file_path) as img:
                ratio = img.width / img.height
                # Must be wide enough (1.77) but not SO wide that it should be a panorama (2.2)
                return 1.77 < ratio < Toolkit.MAX_STACK_ASPECT
        except (OSError, UnidentifiedImageError):
            return False

    @staticmethod
    def _are_compatible(file1: str, file2: str) -> bool:
        """
        Checks if two images should be stacked together.
        1. Both must be wide (within stackable range).
        2. Ratios must be similar (within tolerance).
        """
        try:
            with Image.open(file1) as img1, Image.open(file2) as img2:
                r1 = img1.width / img1.height
                r2 = img2.width / img2.height

                if not (1.77 < r2 < Toolkit.MAX_STACK_ASPECT):
                    return False
                # Allow 5% deviation
                if abs(r1 - r2) / r1 > 0.05:
                    return False

                return True
        except (OSError, UnidentifiedImageError):
            return False

    @staticmethod
    def process_image(payload: tuple[list[str], dict]) -> bool:
        """
        Main worker. Accepts a LIST of file paths.
        """
        file_paths, settings = payload

        valid_paths = [Path(p) for p in file_paths if Path(p).exists()]
        if not valid_paths:
            return False

        path = valid_paths[0]
        try:
            if len(valid_paths) > 1:
                Toolkit._render_stack(valid_paths, settings)
                return True
            with Image.open(path) as img:
                is_wide = (img.width / img.height) > 1.5
                if settings.get("split_wide_images") and is_wide:
                    Toolkit._process_panorama(img, settings, path)
                else:
                    Toolkit._render_panel(
                        img,
                        settings,
                        path.stem,
                        path.parent,
                        align="center"
                    )
            return True

        except (OSError, UnidentifiedImageError, ValueError, TypeError) as e:
            output_dir = path.parent / "panelizer_output"
            output_dir.mkdir(exist_ok=True)
            fail_file = output_dir / f"{path.name}.failed"
            error_msg = f"Export failed for {path.name} (or stack).\nDetails: {e}"

            try:
                with open(fail_file, "w", encoding="utf-8") as f:
                    f.write(error_msg)
            except OSError:
                pass
            return False

    @staticmethod
    def _render_stack(paths: List[Path], settings: dict) -> None:
        """
        Vertically stacks multiple images onto one panel.
        """
        layout = settings.get("layout")
        ref_h = int(settings.get("canvas_height") or 2500)
        bg_color_name = settings.get("background_color") or "white"
        bg_hex = Toolkit.COLOR_MAP.get(bg_color_name, "#FFFFFF")

        images = [Image.open(p) for p in paths]
        max_w = max(img.width for img in images)
        norm_images = []

        for img in images:
            if img.width != max_w:
                scale = max_w / img.width
                norm_images.append(img.resize((max_w, int(img.height * scale)), Image.Resampling.LANCZOS))
            else:
                norm_images.append(img)
        images = norm_images

        if layout == "uniform":
            pad_data = settings.get("padding") or {}
            border_pct = pad_data.get("uniform") or 5
            orientation = pad_data.get("orientation") or "inward"

            border_px = int(ref_h * (border_pct / 100))
            gap_px = border_px
            total_gaps = gap_px * (len(images) - 1)

            if orientation == "outward":
                final_images = images
                stack_h = sum(img.height for img in final_images) + total_gaps
                canvas_w = max_w + (2 * border_px)
                canvas_h = stack_h + (2 * border_px)
                start_x = border_px
                start_y = border_px

            else:
                canvas_h = ref_h
                available_h = canvas_h - (2 * border_px) - total_gaps
                current_img_h = sum(img.height for img in images)
                scale = available_h / current_img_h

                final_images = []
                for img in images:
                    new_w = int(img.width * scale)
                    new_h = int(img.height * scale)
                    final_images.append(img.resize((new_w, new_h), Image.Resampling.LANCZOS))

                canvas_w = final_images[0].width + (2 * border_px)
                start_x = border_px
                start_y = border_px

            canvas = Image.new("RGB", (canvas_w, canvas_h), bg_hex)
            curr_y = start_y
            for img in final_images:
                canvas.paste(img, (start_x, curr_y))
                curr_y += img.height + gap_px

        else:
            ratio_str = settings.get("canvas_ratio") or "4:5"
            ratio_val = Toolkit.RATIO_MAP.get(ratio_str) or 4 / 5
            canvas_w = int(ref_h * ratio_val)

            # Determine Padding first to set Gap
            _, _, pad_t, _ = Toolkit._calculate_base_padding(canvas_w, ref_h, settings)
            gap_px = pad_t
            total_gaps = gap_px * (len(images) - 1)

            safe_w, safe_h = Toolkit._calculate_safe_area(canvas_w, ref_h, settings)
            available_h_for_images = safe_h - total_gaps

            max_img_w = max_w
            total_original_h = sum(img.height for img in images)

            scale_w = safe_w / max_img_w
            scale_h = available_h_for_images / total_original_h
            final_scale = min(scale_w, scale_h)

            resized_images = []
            for img in images:
                w = int(img.width * final_scale)
                h = int(img.height * final_scale)
                resized_images.append(img.resize((w, h), resample=Image.Resampling.LANCZOS))

            canvas = Image.new("RGB", (canvas_w, ref_h), bg_hex)

            stack_content_h = sum(img.height for img in resized_images) + total_gaps

            # Re-use the pad_t we calculated earlier for vertical centering offset
            local_y_offset = (safe_h - stack_content_h) // 2
            current_y = pad_t + local_y_offset

            for r_img in resized_images:
                current_x = (canvas_w - r_img.width) // 2
                canvas.paste(r_img, (current_x, current_y))
                current_y += r_img.height + gap_px

        output_dir = paths[0].parent / "panelizer_output"
        output_dir.mkdir(exist_ok=True)
        stem = paths[0].stem + "_stacked"
        save_path = output_dir / f"{stem}.jpg"

        if canvas.mode in ("RGBA", "P"):
            canvas = canvas.convert("RGB")
        canvas.save(save_path, quality=95, subsampling=0)

    @staticmethod
    def _process_panorama(img: Image.Image, settings: dict, path: Path) -> None:
        """Standard Panorama logic."""
        canvas_h = int(settings.get("canvas_height") or 2500)
        ratio = Toolkit.RATIO_MAP.get(settings.get("canvas_ratio") or "4:5", 4 / 5)
        canvas_w = int(canvas_h * ratio)

        safe_w, safe_h = Toolkit._calculate_safe_area(canvas_w, canvas_h, settings)
        safe_aspect = safe_w / safe_h

        if safe_aspect < Toolkit.MIN_SPLIT_ASPECT:
            threshold_aspect = safe_aspect * 0.25
        else:
            threshold_aspect = Toolkit.MIN_SPLIT_ASPECT

        scale = safe_h / img.height
        proj_w = int(img.width * scale)
        proj_h = int(img.height * scale)

        exact_panels = proj_w / safe_w
        num_panels = math.ceil(exact_panels)

        remainder_w = proj_w - ((num_panels - 1) * safe_w)
        if remainder_w <= 0: remainder_w = safe_w

        remainder_aspect = remainder_w / safe_h

        if num_panels > 1 and remainder_aspect < threshold_aspect:
            target_total_w = (num_panels - 1) * safe_w
            scale = target_total_w / img.width
            proj_w = int(img.width * scale)
            proj_h = int(img.height * scale)
            num_panels = num_panels - 1

        work_img = img.resize((proj_w, proj_h), resample=Image.Resampling.LANCZOS)

        for i in range(num_panels):
            x_start = i * safe_w
            x_end = x_start + safe_w
            if x_end > proj_w:
                x_end = proj_w
            slice_img = work_img.crop((x_start, 0, x_end, proj_h))

            pad_overrides = {}
            is_first = (i == 0)
            is_last = (i == num_panels - 1)

            if not is_last:
                pad_overrides["right"] = 0
            if not is_first:
                pad_overrides["left"] = 0

            align: Literal["center", "left", "right"] = "left" if not is_first else "right"
            suffix = f"_{i + 1}"

            Toolkit._render_panel(
                slice_img,
                settings,
                path.stem + suffix,
                path.parent,
                align=align,
                pad_overrides=pad_overrides,
                bypass_resize=True
            )

    @staticmethod
    def _calculate_base_padding(target_w: int, target_h: int, settings: dict) -> Tuple[int, int, int, int]:
        """Calculates the base framing padding (Left, Right, Top, Bottom) in pixels."""
        pad_data = settings.get("padding") or {}
        pad_l = int(target_w * ((pad_data.get("left") or 0) / 100))
        pad_r = int(target_w * ((pad_data.get("right") or 0) / 100))
        pad_t = int(target_h * ((pad_data.get("top") or 0) / 100))
        pad_b = int(target_h * ((pad_data.get("bottom") or 0) / 100))
        return pad_l, pad_r, pad_t, pad_b

    @staticmethod
    def _calculate_safe_area(w: int, h: int, settings: dict) -> Tuple[int, int]:
        """Returns (safe_width, safe_height) based on layout settings."""
        layout = settings.get("layout")

        if layout == "uniform":
            pad_data = settings.get("padding") or {}
            border_pct = pad_data.get("uniform") or 5
            orientation = pad_data.get("orientation") or "inward"

            border_px = int(h * (border_pct / 100))

            if orientation == "outward":
                return w, h
            else:
                return w - (2 * border_px), h - (2 * border_px)
        else:
            p_l, p_r, p_t, p_b = Toolkit._calculate_base_padding(w, h, settings)
            return w - p_l - p_r, h - p_t - p_b

    @staticmethod
    def _render_panel(
            img: Image.Image,
            settings: dict,
            stem: str,
            source_dir: Path,
            align: Literal["center", "left", "right"] = "center",
            pad_overrides: dict | None = None,
            bypass_resize: bool = False
    ) -> str:
        """Internal helper to apply layout, create canvas, and save the file."""
        if pad_overrides is None:
            pad_overrides = {}

        layout = settings.get("layout")
        canvas_height = settings.get("canvas_height") or 2500
        bg_color_name = settings.get("background_color") or "white"
        bg_hex = Toolkit.COLOR_MAP.get(bg_color_name, "#FFFFFF")

        if layout == "uniform":
            canvas, final_img, pos = Toolkit._apply_uniform_layout(
                img, canvas_height, settings, bg_hex, pad_overrides, bypass_resize
            )
        else:
            canvas, final_img, pos = Toolkit._apply_framing_layout(
                img, canvas_height, settings, bg_hex, align, pad_overrides, bypass_resize
            )

        canvas.paste(final_img, pos)
        output_dir = source_dir / "panelizer_output"
        output_dir.mkdir(exist_ok=True)
        save_path = output_dir / f"{stem}{Toolkit.FILENAME_SUFFIX}.jpg"

        if canvas.mode in ("RGBA", "P"):
            canvas = canvas.convert("RGB")
        canvas.save(save_path, quality=95, subsampling=0)
        return save_path.name

    @staticmethod
    def _apply_framing_layout(
            img: Image.Image,
            target_h: int,
            settings: dict,
            bg_color: str,
            align: str,
            pad_overrides: dict,
            bypass_resize: bool
    ) -> Tuple[Image.Image, Image.Image, Tuple[int, int]]:

        ratio_str = settings.get("canvas_ratio") or "4:5"
        ratio = Toolkit.RATIO_MAP.get(ratio_str) or 4 / 5
        target_w = int(target_h * ratio)
        canvas = Image.new("RGB", (target_w, target_h), bg_color)

        pad_l, pad_r, pad_t, pad_b = Toolkit._calculate_base_padding(target_w, target_h, settings)

        if "left" in pad_overrides: pad_l = pad_overrides["left"]
        if "right" in pad_overrides: pad_r = pad_overrides["right"]
        if "top" in pad_overrides: pad_t = pad_overrides["top"]
        if "bottom" in pad_overrides: pad_b = pad_overrides["bottom"]

        safe_w = target_w - pad_l - pad_r
        safe_h = target_h - pad_t - pad_b

        if bypass_resize:
            resized_img = img
        else:
            resized_img = ImageOps.contain(img, (safe_w, safe_h), method=Image.Resampling.LANCZOS)

        res_w, res_h = resized_img.size
        y_pos = pad_t + ((safe_h - res_h) // 2)
        if align == "left":
            x_pos = pad_l
        elif align == "right":
            x_pos = target_w - pad_r - res_w
        else:
            x_pos = pad_l + ((safe_w - res_w) // 2)

        return canvas, resized_img, (x_pos, y_pos)

    @staticmethod
    def _apply_uniform_layout(
            img: Image.Image,
            target_h: int,
            settings: dict,
            bg_color: str,
            pad_overrides: dict,
            bypass_resize: bool
    ) -> Tuple[Image.Image, Image.Image, Tuple[int, int]]:

        pad_data = settings.get("padding") or {}
        border_pct = pad_data.get("uniform") or 5
        orientation = pad_data.get("orientation") or "inward"
        base_border = int(target_h * (border_pct / 100))

        b_left = 0 if "left" in pad_overrides else base_border
        b_right = 0 if "right" in pad_overrides else base_border
        b_top = base_border
        b_bottom = base_border

        if bypass_resize:
            new_w, new_h = img.size
            base_img = img
        else:
            new_h = target_h
            scale = new_h / img.height if img.height else 1.0
            new_w = int(img.width * scale)
            base_img = img.resize((new_w, new_h), resample=Image.Resampling.LANCZOS)

        if orientation == "outward" or bypass_resize:
            canvas_w = new_w + b_left + b_right
            canvas_h = new_h + b_top + b_bottom
            resized_img = base_img
            pos = (b_left, b_top)
        else:
            canvas_w = new_w
            canvas_h = new_h
            crop_box = (b_left, b_top, new_w - b_right, new_h - b_bottom)

            # Safety Check
            if crop_box[2] <= crop_box[0] or crop_box[3] <= crop_box[1]:
                mid_x, mid_y = new_w // 2, new_h // 2
                crop_box = (mid_x, mid_y, mid_x + 1, mid_y + 1)

            resized_img = base_img.crop(crop_box)
            pos = (b_left, b_top)

        canvas = Image.new("RGB", (canvas_w, canvas_h), bg_color)
        return canvas, resized_img, pos