
from dotenv import load_dotenv
from PIL import Image
from google import genai
from io import BytesIO
import datetime
import os

"""
Create a hyper-realistic 3D render of a toy action figure version of me inside collectible packaging. The figure should look like me, posed in a fun stance, with glossy plastic blister wrapping over the toy. Place the given accessories around the figure. Add a bold name label at the top of the box, styled like a retro action figure line, and include bright, eye-catching background graphics inside the packaging. Make it look like an official toy you'd find in a store aisle. Add lighting and shadows that enhance the plastic and cardboard textures.
"""

# Load environment variables from a .env file
load_dotenv()

def generate_image(prompt, image_paths):
    """Generates an image using the Gemini API based on a prompt and input images.

    This function initializes the Gemini client, prepares the input content by
    combining the text prompt and opening the provided image files, and then
    calls the Gemini API to generate a new image. The generated image is saved
    to a local directory with a timestamped filename.

    Args:
        prompt (str): The text prompt to guide the image generation process.
        image_paths (list of str): A list of file paths for the images to be
            used as input for the generation.

    Returns:
        str: The file path of the newly created image if generation is successful.
        str: An error message string if an exception occurs during the API call.
        None: If the API response does not contain image data.
    """
    try:
        client = genai.Client()
        images = [Image.open(image_path) for image_path in image_paths]
        contents = [prompt, *images]
        
        response = client.models.generate_content(
            model="gemini-2.5-flash-image-preview",
            contents=contents,
        )

        output_dir = "generated_images"
        os.makedirs(output_dir, exist_ok=True)

        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"generated_{timestamp}.png"
                filepath = os.path.join(output_dir, filename)
                
                image = Image.open(BytesIO(part.inline_data.data))
                image.save(filepath)
                return filepath  # Return the path to the new image
            elif part.text is not None:
                print(part.text)
        return None
    except Exception as e:
        print(f"An error occurred during Gemini API call: {e}")
        return f"Error: {e}"
