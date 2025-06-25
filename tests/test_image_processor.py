import unittest
from library import ImageProcessor
from PIL import Image
import os

TEST_IMAGE_PATH = "tests/images/input/car.png"
TEST_OVERLAY_PATH = "tests/images/overlay/RIBA_logo.png"
TEST_IMAGE_URL = "https://raw.githubusercontent.com/MajesticMinhaz/Blender-Python/refs/heads/main/Blender/Image/3.png"
TEST_OUTPUT_DIR = "tests/images/output/"

class TestImageProcessor(unittest.TestCase):

    def test_local_image_processing_save(self):
        processor = ImageProcessor(image_path=TEST_IMAGE_PATH)
        result_path = processor.process(overlay_path=TEST_OVERLAY_PATH, save_dir=TEST_OUTPUT_DIR, return_image=False)
        self.assertTrue(os.path.exists(result_path))

    def test_local_image_processing_return_image(self):
        processor = ImageProcessor(image_path=TEST_IMAGE_PATH)
        img = processor.process(overlay_path=TEST_OVERLAY_PATH, save_dir=TEST_OUTPUT_DIR, return_image=True)
        self.assertIsInstance(img, Image.Image)

    def test_image_url_processing(self):
        processor = ImageProcessor(image_url=TEST_IMAGE_URL)
        result_path = processor.process(overlay_path=TEST_OVERLAY_PATH, save_dir=TEST_OUTPUT_DIR)
        self.assertTrue(os.path.exists(result_path))

    def test_invalid_url_handling(self):
        with self.assertRaises(IOError):
            processor = ImageProcessor(image_url="http://invalid.url/image.jpg")
            processor.process(overlay_path=TEST_OVERLAY_PATH, save_dir=TEST_OUTPUT_DIR)

    def test_invalid_path_handling(self):
        with self.assertRaises(IOError):
            processor = ImageProcessor(image_path="invalid_path.jpg")
            processor.process(overlay_path=TEST_OVERLAY_PATH, save_dir=TEST_OUTPUT_DIR)

    def test_missing_input(self):
        with self.assertRaises(ValueError):
            ImageProcessor()

    def test_invalid_overlay_path(self):
        with self.assertRaises(IOError):
            processor = ImageProcessor(image_path=TEST_IMAGE_PATH)
            processor.process(overlay_path="invalid_overlay.png", save_dir=TEST_OUTPUT_DIR)

    def test_processing_without_overlay_save(self):
        processor = ImageProcessor(image_path=TEST_IMAGE_PATH)
        result_path = processor.process(save_dir=TEST_OUTPUT_DIR)
        self.assertTrue(os.path.exists(result_path))

    def test_processing_without_overlay_return_image(self):
        processor = ImageProcessor(image_path=TEST_IMAGE_PATH)
        img = processor.process(return_image=True)
        self.assertIsInstance(img, Image.Image)

    def test_non_image_file_url(self):
        with self.assertRaises(IOError):
            processor = ImageProcessor(image_url="https://example.com")
            processor.process(overlay_path=TEST_OVERLAY_PATH, save_dir=TEST_OUTPUT_DIR)

    def test_overlay_preserves_size(self):
        processor = ImageProcessor(image_path=TEST_IMAGE_PATH)
        result_path = processor.process(overlay_path=TEST_OVERLAY_PATH, save_dir=TEST_OUTPUT_DIR)
        with Image.open(result_path) as img:
            self.assertEqual(img.size, (600, 500))

    def test_overlay_on_different_size_image(self):
        processor = ImageProcessor(image_path=TEST_IMAGE_PATH)
        result = processor.process(overlay_path=TEST_OVERLAY_PATH, save_dir=TEST_OUTPUT_DIR, return_image=True)
        self.assertEqual(result.size, (600, 500))

if __name__ == "__main__":
    unittest.main()
