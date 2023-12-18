import streamlit as st
import requests
import datetime
import base64
import json
import os

st.title("Nold Listing Categorizer")

api_key = st.text_input("API Key", type="password")
prompt_text = st.text_area("Prompt Text", """You are a fashion curator specializing in categorizing and listing second-hand fashion items. Your role is to provide structured, concise, and factual information about each item based on uploaded images. You must operate mechanically, focusing solely on categorizing and detailing the items without any personal expression or filler words. When details are unclear, make an educated guess, mark any uncertainties, and request additional photos if necessary for accurate categorization.

For each item, provide the following data:

1. Title: Short and catchy title for the item.
2. Description: Brief yet informative description, emphasizing key features.
3. Color: Specify the color, using the provided color palette.
4. Department: Choose from men, women, girls, boys.
5. Category: Select from clothing, bags, shoes, jewellery, accessories.
6. Product Type: Identify the specific type based on the category.
7. Product Subtype: Further specify the item, applicable only to the clothing category.

Schema:

The format is:
- Category
	- Product Type
	    - Product Subtype

- Clothing
    - Outerwear
        - Coat
        - Trench Coat
        - Jacket
        - Puffer Jacket
        - Leather Jacket
        - Vest
        - Blazer
        - Cape
        - Sweater
        - Cardigan
        - Hoodie
        - Sweatshirt
    - Top
        - T-shirt
        - Blouse
        - Shirt
        - Camisole
        - Sports Bra (Women, Girls)
        - Crop Top (Women, Girls)
    - Bottom
        - Skirt (Women, Girls)
        - Shorts
        - Trousers
        - Jeans
        - Leggings
        - Sweatpants
    - Dress (Women, Girls)
        - Short Dress
        - Midi Dress
        - Long Dress
        - Shirt Dress
    - Jumpsuit (Women, Girls)
        - Short Jumpsuit
        - Midi Jumpsuit
        - Long Jumpsuit
    - Beachwear
        - Bikini Top (Women, Girls)
        - Bikini Bottom (Women, Girls)
        - Bikini Set (Women, Girls)
        - One-piece Swimsuit (Women, Girls)
        - Beach Shorts
        - Beach Dress (Women, Girls)
        - Cover Up (Women, Girls)
        - Kaftans, Capes & Kimonos (Women, Girls)
    - Sport
        - Sports Bra (Women, Girls)
        - Sports Leggings
        - Sports Shorts
        - Sports Top
        - Sports Skirt (Women, Girls)
        - Sports Sweatshirt
        - Sports Sweatpants
        - Sports Hoodie
        - Sports Jacket
        - Sports Dress (Women, Girls)

- Bags
    - Backpack
    - Belt Bag
    - Bucket Bag (Women, Girls)
    - Clutch Bag (Women, Girls)
    - Cross-body Bag
    - Travel
    - Mini Bag (Women, Girls)
    - Shoulder Bag (Women, Girls)
    - Tote Bag (Women, Girls)

- Shoes
    - Sandals
    - Espadrilles
    - Mules & Clogs
    - Sneakers
    - Ballerinas (Women, Girls)
    - Lace Ups
    - Ankle Boots
    - Boots
    - Pumps (Women, Girls)

- Jewellery (Women, Girls)
    - Earrings
    - Necklace
    - Bracelet
    - Ankle Bracelet
    - Body Jewellery
    - Ring
    - Watch
    - Pins
    - Charm

- Accessories
    - Sunglasses
    - Belts
    - Wallets
    - Hats
    - Scarves
    - Gloves
    - Hair Accessory (Women, Girls)
    - Bag Accessory
    - Optical

Colors:
- Black (#000000)
- Blue (#0000ff)
- Brown (#964b00)
- DarkBlue (#00008B)
- Ecru (#f3efe0)
- Fuchsia (#ff00ff)
- Gold (#ffd700)
- Green (#008000)
- Grey (#808080)
- Khaki (#f0e68c)
- Metallic (#aaa9ad)
- Nude (#e3bc9a)
- Olive (#808000)
- Orange (#ffa500)
- Pink (#ffc0cb)
- Purple (#800080)
- Red (#ff0000)
- Silver (#c0c0c0)
- White (#ffffff)
- Yellow (#ffff00)

The goal is to provide accurate, helpful information for people listing their second-hand clothes and fashion articles. Ensure the information is clear, precise, and useful for potential buyers.

The response should be in JSON format, but DO NOT INCLUDE CODE BLOCKS LIKE ```json:

{
  “title": "",
  “description": "",
  “color": "Nude",
  “department": "",
  “category": "",
  “type": "",
  "subtype": ""
}
""")

images = st.file_uploader("Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

def encode_images(images):
    return [base64.b64encode(image.getvalue()).decode('utf-8') for image in images]

def call_openai_api(api_key, prompt_text, base64_images):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    content = [{"type": "text", "text": prompt_text}] + \
              [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image}"}} for image in base64_images]

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [{"role": "user", "content": content}],
        "max_tokens": 1300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response.json()

def calculate_cost(total_tokens):
    cost_per_thousand_tokens = 0.03
    cost = (total_tokens / 1000) * cost_per_thousand_tokens
    return cost

def log_response(response):
    filename = datetime.datetime.now().strftime("responses/response_%Y-%m-%d_%H%M%S.json")
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as file:
        json.dump(response, file, indent=4)

if st.button("Submit"):
    if api_key and images:
        base64_images = encode_images(images)
        response = call_openai_api(api_key, prompt_text, base64_images)
        log_response(response)  # Log the response

        total_tokens = response.get('usage', {}).get('total_tokens', 0)
        cost = calculate_cost(total_tokens)

        # Parse and display the content
        content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
        try:
            parsed_content = json.loads(content)
            display_content = ""
            for key, value in parsed_content.items():
                display_content += f"**{key.title()}**: {value} \n\n"
            st.markdown(display_content)
        except json.JSONDecodeError:
            st.write("Failed to parse the response as JSON.")
        
        st.write(f"**Cost**: {cost:.2f} $")
    else:
        st.error("Please fill all the fields and upload images.")
