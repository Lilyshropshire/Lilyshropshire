import PySimpleGUI as sg
import requests
import re

# Spoonacular API key
API_KEY = "75477a5144824f80a6199da27d5337a1"

# Function to get recipe suggestions from Spoonacular API
def get_recipe_suggestions(ingredients):
    url = "https://api.spoonacular.com/recipes/findByIngredients"
    params = {
        "ingredients": ",".join(ingredients),
        "number": 5,  # Number of recipes to retrieve
        "apiKey": API_KEY
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Function to get detailed recipe information
def get_recipe_details(recipe_id):
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
    params = {
        "apiKey": API_KEY
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Capitalize ingredient names
def capitalize_ingredients(ingredients_list):
    capitalized_list = [ingredient.capitalize() for ingredient in ingredientList]
    return capitalized_list

# Set theme and background color
sg.theme('Reddit')

# Define the ingredients organized by categories
ingredientList = {
    "Flour": ["All-Purpose Flour", "Whole Wheat Flour", "Bread Flour", "Cake Flour", "Gluten Free Flour", "Almond Flour"],
    "Leaveners": ["Baking Soda", "Baking Powder", "Yeast"], 
    "Sugar and Sweeteners": ["Granulated Sugar", "Light Brown Sugar", "Dark Brown Sugar", "Confectioners' Sugar", "Honey", "Molasses", "Maple Syrup"],
    "Dairy": ["Unsalted Butter", "Salted Butter", "Eggs", "Milk", "Buttermilk", "Cream Cheese", "Milk Powder"],
    "Fats": ["Vegetable Oil", "Shortening", "Coconut Oil", "Peanut Butter", "Almond Butter", "Hazelnut Butter", "Cashew Butter", "Sunflower Butter"], 
    "Extracts and Flavorings": ["Vanilla Extract", "Almond Extract", "Lemon Extract", "Mint Extract", "Vanilla Bean"],
    "Spices": ["Cinnamon", "Nutmeg", "Allspice", "Ginger"],
    "Chocolate": ["Milk Chocolate Chips", "Dark Chocolate Chips", "White Chocolate Chips", "Semisweet Chocolate Chips", "Dark Chocolate Bar", "Milk Chocolate Bar", "White Chocolate Bar", "Unsweetened Cocoa Powder", "Dutch-Process Cocoa Powder"], 
    "Nuts": ["Almonds", "Pecans", "Macadamia Nuts", "Walnuts", "Peanuts", "Pistachios", "Hazelnuts"],
    "Fruits": ["Strawberries", "Raspberries", "Blueberries", "Blackberries", "Bananas", "Apples", "Peaches", "Cherries", "Pears", "Nectarines", "Oranges", "Lemons", "Limes", "Pineapple"],
    "Dried Fruits": ["Raisins", "Candied Ginger", "Dried Apricots", "Dried Cherries", "Dried Cranberries", "Prunes"],
    "Other": ["Salt", "Cornstarch", "Cream of Tartar"], 
}

# Generate layout dynamically
layout = []
column_layout = []
for ingredientList, ingredients in ingredientList.items():
    column_layout.append([sg.Text(ingredientList, font=('Helvetica', 14))])
    column_layout.extend([[sg.Checkbox(ingredient, key=ingredient)] for ingredient in ingredients])
    column_layout.append([sg.HorizontalSeparator()])

layout.append([sg.Column(column_layout, scrollable=True, vertical_scroll_only=True, size=(500, 300))])
layout.append([sg.Button("Submit", size=(10, 1), pad=(10, 10))])

# Create the window
window = sg.Window("Recipe Ingredient Checklist", layout, size=(600, 400))

# List to store selected ingredients
selected_ingredients_list = []

# Check to see if user has added ingredients
while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break
    if event == "Submit":
        # Clear the list before adding new ingredients
        selected_ingredients_list.clear()
        # Store selected ingredients in the list
        selected_ingredients_list.extend([ingredient for ingredient in values if values[ingredient]])
        
        # Get recipe suggestions from Spoonacular API
        suggested_recipes = get_recipe_suggestions(selected_ingredients_list)
        
        # Format for recipe suggestions
        if suggested_recipes:
            recipe_names = [recipe["title"] for recipe in suggested_recipes]
            recipe_selection_layout = [
                [sg.Listbox(values=recipe_names, size=(30, len(recipe_names)), key="-RECIPE LIST-", select_mode=sg.LISTBOX_SELECT_MODE_SINGLE)],
                [sg.Button("View Recipe", size=(10, 1), pad=(10, 10))]
            ]
            recipe_selection_window = sg.Window("Select Recipe", recipe_selection_layout)
            
            # Suggest recipes to user
            while True:
                event, values = recipe_selection_window.read()
                if event == sg.WINDOW_CLOSED:
                    break
                if event == "View Recipe" and values["-RECIPE LIST-"]:
                    selected_recipe_name = values["-RECIPE LIST-"][0]
                    selected_recipe = next((recipe for recipe in suggested_recipes if recipe["title"] == selected_recipe_name), None)
                    if selected_recipe:
                        # Get detailed recipe information
                        recipe_details = get_recipe_details(selected_recipe["id"])
                        if recipe_details:
                            ingredients_list = [f"{ingredient['name'].capitalize()}: {ingredient['amount']} {ingredient['unit']}" for ingredient in recipe_details["extendedIngredients"]]
                            # Remove HTML list tags and replace with line breaks
                            instructions = re.sub(r'<[^>]+>', '\n', recipe_details["instructions"])
                            sg.popup_scrolled("\n".join(ingredients_list) + "\n\n" + instructions, title=selected_recipe_name + " Recipe")
                        else:
                            sg.popup("Failed to retrieve recipe details.")
                    
            recipe_selection_window.close()
        # Notify user if no there are no possible recipes
        else:
            sg.popup("Sorry, no recipes found with the selected ingredients.")

# Close the window
window.close()