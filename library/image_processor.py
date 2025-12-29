import os
import io
import uuid
import requests
from PIL import Image
import cairosvg


def _load_image(url: str, path: str) -> Image.Image:
    """
    Loads an image from a URL or local file path.

    Parameters:
        url (str): Image URL.
        path (str): Local file path.

    Returns:
        Image.Image: PIL Image object.

    Raises:
        IOError: If loading or downloading fails.
    """
    try:
        if url:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            content = response.content

            # Check if SVG
            if url.lower().endswith('.svg') or b'<svg' in content[:100]:
                png_data = cairosvg.svg2png(bytestring=content)
                return Image.open(io.BytesIO(png_data)).convert("RGBA")

            return Image.open(io.BytesIO(content)).convert("RGBA")

        else:
            # Check if local file is SVG
            if path.lower().endswith('.svg'):
                png_data = cairosvg.svg2png(url=path)
                return Image.open(io.BytesIO(png_data)).convert("RGBA")

            return Image.open(path).convert("RGBA")
    except Exception as e:
        raise IOError(f"Failed to load image: {e} -> {url}")


class ImageProcessor:
    """
    A utility class to download or load an image, center-crop it,
    overlay another image, and either return the result or save it to disk.
    """

    def __init__(self, image_url: str = None, image_path: str = None):
        """
        Initialize the ImageProcessor with either an image URL or a local path.

        Parameters:
            image_url (str, optional): The URL of the image to download.
            image_path (str, optional): The local path to the image file.

        Raises:
            ValueError: If neither image_url nor image_path is provided.
            IOError: If image loading or downloading fails.
        """
        if not image_url and not image_path:
            raise ValueError("Either 'image_url' or 'image_path' must be provided.")
        self.image = _load_image(image_url, image_path)

    def process(
            self,
            overlay_path: str = None,
            save_dir: str = None,
            return_image: bool = False
    ) -> str or Image.Image:
        """
        Center-crops the base image, overlays another image if provided, and either saves or returns it.

        Parameters:
            overlay_path (str, optional): Path to the overlay image.
            save_dir (str, optional): Directory to save the processed image. Required if return_image is False.
            return_image (bool): If True, returns the PIL Image object instead of saving it.

        Returns:
            str or Image.Image: Path to saved image or Image object.

        Raises:
            ValueError: If save_dir is missing when return_image is False.
            IOError: If image saving or overlay loading fails.
        """
        base_img = self.image
        width, height = base_img.size
        target_w, target_h = 600, 500
        target_aspect = target_w / target_h
        current_aspect = width / height

        # Calculate cropping box for center crop
        if current_aspect > target_aspect:
            new_width = int(height * target_aspect)
            offset = (width - new_width) // 2
            crop_box = (offset, 0, offset + new_width, height)
        else:
            new_height = int(width / target_aspect)
            offset = (height - new_height) // 2
            crop_box = (0, offset, width, offset + new_height)

        # Crop and resize to target size
        cropped_img = base_img.crop(crop_box).resize((target_w, target_h), Image.Resampling.LANCZOS)

        # Apply overlay if provided
        if overlay_path:
            try:
                overlay_img = Image.open(overlay_path).convert("RGBA").resize((target_w, target_h),
                                                                              Image.Resampling.LANCZOS)
                final_img = Image.alpha_composite(cropped_img, overlay_img).convert("RGB")
            except Exception as e:
                raise IOError(f"Failed to load overlay image: {e}")
        else:
            final_img = cropped_img.convert("RGB")

        if return_image:
            return final_img

        if not save_dir:
            raise ValueError("Parameter 'save_dir' is required when return_image is False.")

        os.makedirs(save_dir, exist_ok=True)
        filename = f"processed_{uuid.uuid4().hex}.jpg"
        output_path = os.path.join(save_dir, filename)

        try:
            final_img.save(output_path, quality=95)
        except Exception as e:
            raise IOError(f"Failed to save image: {e}")

        return output_path