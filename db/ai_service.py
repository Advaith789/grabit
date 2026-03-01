import os
import json
from groq import Groq
from schemas import ExtractionResult

MODEL_NAME = "llama-3.3-70b-versatile"
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def extract_food_data(restaurant_name: str, message: str) -> ExtractionResult:
    system_prompt = (
        "You are an expert food logistics and marketing assistant. "
        "1. Extract food items, their primary cuisines, and quantities. "
        "2. Write a short, exciting email body (2-3 sentences). "
        "3. Write a catchy, short email subject line. "
        "Use emojis in the content to show more engaging content. "
        "STRICT RULE 1: The 'quantity' MUST be strictly numerical digits only (e.g., use '10' instead of 'ten', '1' instead of 'a tray'). "
        "STRICT RULE 2: Normalize the 'name' and 'cuisine' fields to be strictly singular and lowercase (e.g., output 'pizza' instead of 'Pizzas' or 'pizzas', 'taco' instead of 'Tacos'). "
        "Respond ONLY with a valid JSON object matching this structure: "
        "{"
        "'foods': [{'name': 'singular item', 'cuisine': 'singular type', 'quantity': 'digits only'}], "
        "'email_body': 'Body text here', "
        "'email_subject': 'Subject line here'"
        "}"
    )

    user_prompt = f"Vendor: {restaurant_name}\nRaw message: {message}\nExtract food and draft the email alert."

    completion = groq_client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        response_format={"type": "json_object"},
    )

    raw_json = json.loads(completion.choices[0].message.content)
    return ExtractionResult(**raw_json)
