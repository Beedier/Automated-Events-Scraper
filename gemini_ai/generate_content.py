import google.generativeai as genai

def generate_text_with_gemini(api_key: str, prompt: str):
    """
    Generates text using the Gemini API based on input text and a prompt.

    Args:
        api_key (str): Gemini api key.
        prompt (str): The prompt to guide the text generation.

    Returns:
        str: The generated text, or None if an error occurs.
    """
    try:
        # Configure the Gemini API with the API key.
        genai.configure(api_key=api_key)

        # Set up the model
        model = genai.GenerativeModel('gemini-2.0-flash')

        # Generate content using the model.
        response = model.generate_content(prompt)

        # Return the generated text.
        return response.text

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
