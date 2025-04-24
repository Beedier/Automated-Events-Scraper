import os
import io
import uuid
import requests
from PIL import Image


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
        self.image = self._load_image(image_url, image_path)

    def _load_image(self, url: str, path: str) -> Image.Image:
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
                return Image.open(io.BytesIO(response.content)).convert("RGBA")
            else:
                return Image.open(path).convert("RGBA")
        except Exception as e:
            raise IOError(f"Failed to load image: {e}")

    def process(
        self,
        overlay_path: str,
        save_dir: str = None,
        return_image: bool = False
    ) -> str or Image.Image:
        """
        Center-crops the base image, overlays another image, and either saves or returns it.

        Parameters:
            overlay_path (str): Path to the overlay image (should support transparency).
            save_dir (str, optional): Directory to save the processed image. Required if return_image is False.
            return_image (bool): If True, returns the PIL Image object instead of saving it.

        Returns:
            str or Image.Image: Path to saved image or Image object.

        Raises:
            ValueError: If overlay_path is missing or save_dir is missing when return_image is False.
            IOError: If image saving or overlay loading fails.
        """
        if not overlay_path:
            raise ValueError("Parameter 'overlay_path' is required.")

        # Get dimensions and aspect ratios
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

        # Load and resize overlay image
        try:
            overlay_img = Image.open(overlay_path).convert("RGBA").resize((target_w, target_h), Image.Resampling.LANCZOS)
        except Exception as e:
            raise IOError(f"Failed to load overlay image: {e}")

        # Overlay and convert to RGB
        final_img = Image.alpha_composite(cropped_img, overlay_img).convert("RGB")

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
