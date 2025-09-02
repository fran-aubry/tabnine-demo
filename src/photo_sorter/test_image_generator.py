
import unittest
from unittest.mock import patch, MagicMock, mock_open
from image_generator import generate_image
import datetime

class TestImageGenerator(unittest.TestCase):

    def test_generate_image_empty_prompt(self):
        """
        Test that generate_image returns an error message when the prompt is empty.
        """
        # The Gemini API would likely raise an error with an empty prompt.
        # We simulate this behavior by having the mock raise an exception.
        with patch('image_generator.genai') as mock_genai, \
             patch('image_generator.Image.open'), \
             patch('image_generator.os.makedirs'):

            mock_client = mock_genai.Client.return_value
            mock_client.models.generate_content.side_effect = Exception("Prompt cannot be empty.")

            prompt = ""
            image_paths = ["dummy_image.jpg"]
            
            result = generate_image(prompt, image_paths)
            
            self.assertTrue(result.startswith("Error:"))
            self.assertIn("Prompt cannot be empty.", result)
            mock_client.models.generate_content.assert_called_once()
