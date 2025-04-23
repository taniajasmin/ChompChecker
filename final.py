import google.generativeai as genai
import openai
import io
from PIL import Image
import re
import os
from dotenv import load_dotenv
import time

load_dotenv()

try:
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file.")
    genai.configure(api_key=gemini_api_key)
except Exception as e:
    print(f"Error loading Gemini API key: {str(e)}")
    exit(1)

# OpenAI API Key
openai.api_key = os.getenv('OPENAI_API_KEY')
if not openai.api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file.")

# Initialize the Gemini model
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

def manual_entry():
    meal_name = input("Enter meal name: ")
    ingredients = []
    
    while True:
        ingredient_name = input("Enter ingredient name (or 'done' to finish): ")
        if ingredient_name.lower() == 'done':
            break
        quantity = input(f"Enter quantity for {ingredient_name}: ")
        if not quantity.strip():
            print("Quantity cannot be empty. Please enter a quantity.")
            continue
        ingredients.append(f"{ingredient_name}: {quantity}")
    
    print("Default serving size = 100 gm.")
    serving_size = "100"
    
    return meal_name, serving_size, ingredients

def upload_image_path():
    file_path = input("Enter the full path to your image file: ")
    if not file_path:
        print("No file path provided. Please try again.")
        return None
    
    try:
        with open(file_path, 'rb') as file:
            image_data = file.read()
        print(f"Image file {file_path} read successfully.")
        return image_data
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except IOError as e:
        print(f"Error reading file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
    return None

def analyze_food_image(image_data):
    if not image_data:
        print("No image data provided.")
        return None
    
    try:
        image = Image.open(io.BytesIO(image_data))
        
        # Convert image to RGB if necessary
        if image.mode not in ('RGB', 'L'):
            image = image.convert('RGB')
        
        # Save image to a temporary file for debugging
        temp_file = "temp_image.jpg"
        image.save(temp_file)
        print(f"Image saved temporarily as {temp_file}")
        
        prompt = """
        Analyze this food image and provide:
        1. Food name and approximate serving size in grams
        2. List of ingredients with quantities
        Format:
        1. [Food Name] (XXX g)
        - ingredient: quantity
        - ingredient: quantity
        """
        
        print("Sending request to Gemini...")
        start_time = time.time()
        response = gemini_model.generate_content([image, prompt])  
        
        if response and response.text:
            print(f"Response received from Gemini in {time.time() - start_time:.2f} seconds")
            return response.text
        else:
            print("No response or empty response from Gemini")
            return None
        
    except Exception as e:
        print(f"An unexpected error occurred during image analysis: {e}")
    
    return None

def format_food_details(response_text):
    if not response_text:
        return "Unknown Food", "100", []
    
    try:
        lines = response_text.split('\n')
        meal_name = "Unknown Food"
        serving_size = "100"
        ingredients = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('1.'):
                parts = line.replace('1.', '').strip().split('(')
                if len(parts) > 0:
                    meal_name = parts[0].strip()
                if len(parts) > 1:
                    size = re.search(r'(\d+)\s*g', parts[1])
                    if size:
                        serving_size = size.group(1)
                        
            elif ':' in line and not line.startswith('2.'):
                ingredients.append(line.strip())
                
        return meal_name, serving_size, ingredients
        
    except Exception as e:
        print(f"Error parsing food details: {e}")
        return "Unknown Food", "100", []

def get_nutritional_data(food_item, ingredients):
    prompt = (
        f"Provide nutritional information for the following meal:\n"
        f"Meal: {food_item}\n"
        f"Ingredients:\n" + "\n".join(ingredients) + "\n"
        "Format the response as follows:\n"
        "- Calories (kcal)\n"
        "- Carbohydrates (g)\n"
        "- Protein (g)\n"
        "- Fat (g)\n"
        "- Fiber (g)"
    )
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  
            messages=[
                {"role": "system", "content": "You are a nutritionist providing detailed nutritional information."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200
        )
        nutritional_data = response['choices'][0]['message']['content'].strip()
        print("OpenAI Response:\n", nutritional_data)
        return nutritional_data
    except Exception as e:
        print(f"Error retrieving nutritional data: {str(e)}")
        return "Error retrieving nutritional data"

def display_info(meal_name, serving_size, ingredients, nutritional_data):
    print("\nFood Details")
    print("------------")
    print(f"Food: {meal_name}")
    print(f"1 serving ({serving_size} g)")

    print("\nIngredients")
    print("-----------")
    print(f"{'Ingredient':<20} {'Quantity':<20}")
    for ingredient in ingredients:
        ing, qty = ingredient.split(':', 1)
        print(f"{ing.strip():<20} {qty.strip():<20}")

    print("\nNutritional Information")
    print("----------------------")
    nutrients = nutritional_data.split('\n')
    for nutrient in nutrients:
        if 'Calories' in nutrient:
            cal_value = re.search(r'(\d+)\s*kcal', nutrient)
            if cal_value:
                print(f"{'Calories':<15} {cal_value.group(1)} kcal")
        elif 'Carbohydrates' in nutrient:
            carb_value = re.search(r'(\d+(?:\.\d+)?)\s*g', nutrient)
            if carb_value:
                print(f"{'Carbohydrate':<15} {carb_value.group(1)} g")
        elif 'Protein' in nutrient:
            protein_value = re.search(r'(\d+(?:\.\d+)?)\s*g', nutrient)
            if protein_value:
                print(f"{'Protein':<15} {protein_value.group(1)} g")
        elif 'Fat' in nutrient:
            fat_value = re.search(r'(\d+(?:\.\d+)?)\s*g', nutrient)
            if fat_value:
                print(f"{'Fat':<15} {fat_value.group(1)} g")
        elif 'Fiber' in nutrient:
            fiber_value = re.search(r'(\d+(?:\.\d+)?)\s*g', nutrient)
            if fiber_value:
                print(f"{'Fiber':<15} {fiber_value.group(1)} g")


def main():
    while True:
        choice = input("Do you want to upload a photo or enter items manually? (photo/manual): ").lower()
        
        if choice == 'photo':
            print("Please provide the full path to your image file.")
            image_data = upload_image_path()
            
            if image_data:
                print("Analyzing image...")
                response = analyze_food_image(image_data)
                
                if response:
                    print("Formatting response...")
                    meal_name, serving_size, ingredients = format_food_details(response)
                    
                    if ingredients:
                        print("Getting nutritional data...")
                        nutritional_data = get_nutritional_data(meal_name, ingredients)
                        display_info(meal_name, serving_size, ingredients, nutritional_data)
                    else:
                        print("No ingredients found. Please try manual entry.")
                else:
                    print("Image analysis failed. Please try manual entry.")
            break
                
        elif choice == 'manual':
            meal_name, serving_size, ingredients = manual_entry()
            nutritional_data = get_nutritional_data(meal_name, ingredients)
            display_info(meal_name, serving_size, ingredients, nutritional_data)
            break
            
        else:
            print("Invalid choice. Please choose 'photo' or 'manual'.")

if __name__ == "__main__":
    main()