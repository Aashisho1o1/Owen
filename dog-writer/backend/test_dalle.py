import openai
from dotenv import load_dotenv
import os
import sys

load_dotenv()  # Load environment variables from .env file

def test_dalle_generation():
    # Get API key from environment or use the one from .env file
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("Error: No OpenAI API key found in environment variables")
        return
    
    print(f"Using API key: {api_key[:10]}...")
    
    try:
        # Initialize the OpenAI client
        client = openai.OpenAI(api_key=api_key)
        
        # Test API connection
        print("Testing DALL-E API connection...")
        
        # Generate an image
        print("Sending request to DALL-E API...")
        response = client.images.generate(
            model="dall-e-3",
            prompt="A manga-style close-up of a detective looking at a diary, monochrome manga style with clean lines",
            size="1024x1024",
            quality="standard",
            n=1,
            response_format="url"
        )
        
        # Print the image URL
        if hasattr(response, 'data') and len(response.data) > 0 and hasattr(response.data[0], 'url'):
            print(f"Success! Image URL: {response.data[0].url}")
            print("Complete response structure:")
            print(response)
        else:
            print("Error: Response doesn't contain expected data structure")
            print("Response structure:")
            print(response)
        
    except openai.APIConnectionError as e:
        print(f"Error: Network connection failed: {e}")
    except openai.RateLimitError as e:
        print(f"Error: Rate limit exceeded: {e}")
    except openai.APIError as e:
        print(f"Error: API responded with error: {e}")
    except openai.AuthenticationError as e:
        print(f"Error: Authentication failed: {e}")
    except Exception as e:
        print(f"Error generating DALL-E image: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dalle_generation() 