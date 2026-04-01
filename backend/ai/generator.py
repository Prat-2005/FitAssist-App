import os
import json
import logging
import google.generativeai as genai

from .prompts import SYSTEM_PROMPT, build_user_prompt, NUTRITION_SYSTEM_PROMPT, build_nutrition_prompt
from .fallback import generate_with_groq, generate_nutrition_with_groq

# Configure logger
logger = logging.getLogger(__name__)

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def validate_plan_schema(plan: dict) -> bool:
    """
    Validates the generated JSON plan to ensure it meets the required schema.
    """
    if not isinstance(plan, dict):
        return False
        
    required_keys = {"plan_name", "summary", "days"}
    if not required_keys.issubset(plan.keys()):
        return False
        
    if not isinstance(plan.get("days"), list):
        return False
        
    for day in plan.get("days", []):
        if not isinstance(day, dict):
            return False
        
        day_required_keys = {"day", "title", "is_rest_day", "exercises"}
        if not day_required_keys.issubset(day.keys()):
            return False
            
        if not isinstance(day.get("exercises"), list):
            return False
            
    return True

def validate_nutrition_schema(plan: dict) -> bool:
    """
    Validates the generated JSON nutrition plan to ensure it meets the required schema.
    """
    if not isinstance(plan, dict):
        return False
        
    required_keys = {"plan_name", "daily_calories_target", "summary", "nutrition_tips", "days"}
    if not required_keys.issubset(plan.keys()):
        return False
        
    if not isinstance(plan.get("days"), list):
        return False
        
    for day in plan.get("days", []):
        if not isinstance(day, dict):
            return False
        
        day_required_keys = {"day", "meals", "daily_total_calories"}
        if not day_required_keys.issubset(day.keys()):
            return False
            
    return True

async def generate_workout_plan(profile: dict) -> dict:
    """
    Generates a 7-day workout plan using Gemini 1.5 Flash.
    Falls back to Groq if generation or validation fails.
    """
    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_PROMPT
        )
        
        user_prompt = build_user_prompt(profile)
        
        generation_config = {
            "temperature": 0.7,
            "max_output_tokens": 4096,
            "response_mime_type": "application/json"
        }
        
        response = await model.generate_content_async(
            user_prompt,
            generation_config=generation_config
        )
        
        plan_data = json.loads(response.text)
        
        if validate_plan_schema(plan_data):
            return plan_data
        else:
            logger.error("Generated plan failed schema validation. Triggering fallback.")
            return await generate_with_groq(profile)
            
    except Exception as e:
        logger.error(f"Gemini generation failed with an error: {e}. Triggering fallback.")
        return await generate_with_groq(profile)

async def generate_nutrition_plan(profile: dict) -> dict:
    """
    Generates a 7-day nutrition plan using Gemini 1.5 Flash.
    Falls back to Groq if generation or validation fails.
    """
    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=NUTRITION_SYSTEM_PROMPT
        )
        
        user_prompt = build_nutrition_prompt(profile)
        
        generation_config = {
            "temperature": 0.7,
            "max_output_tokens": 4096,
            "response_mime_type": "application/json"
        }
        
        response = await model.generate_content_async(
            user_prompt,
            generation_config=generation_config
        )
        
        plan_data = json.loads(response.text)
        
        if validate_nutrition_schema(plan_data):
            return plan_data
        else:
            logger.error("Generated nutrition plan failed schema validation. Triggering fallback.")
            return await generate_nutrition_with_groq(profile)
            
    except Exception as e:
        logger.error(f"Gemini nutrition generation failed with an error: {e}. Triggering fallback.")
        return await generate_nutrition_with_groq(profile)
