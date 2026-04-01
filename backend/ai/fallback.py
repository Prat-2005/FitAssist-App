import os
import json
import logging
from groq import AsyncGroq

from .prompts import (
    SYSTEM_PROMPT, 
    NUTRITION_SYSTEM_PROMPT,
    build_user_prompt,
    build_nutrition_prompt
)

logger = logging.getLogger(__name__)

# Initialize the Groq client
# The SDK automatically looks for the GROQ_API_KEY environment variable.
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = AsyncGroq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

GROQ_MODEL = "llama-3.3-70b-versatile"

async def generate_with_groq(profile: dict) -> dict:
    """
    Fallback function to generate workout plans using Groq SDK and Llama 3.3.
    """
    logger.info("Triggering Groq fallback for workout plan generation.")
    try:
        user_prompt = build_user_prompt(profile)
        
        response = await groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            model=GROQ_MODEL,
            temperature=0.7,
            max_tokens=4096,
            response_format={"type": "json_object"}
        )
        
        response_text = response.choices[0].message.content
        return json.loads(response_text)
        
    except Exception as e:
        logger.error(f"Groq fallback workout generation failed: {e}")
        # Last resort return structure when both primary and fallback fail
        return {
            "plan_name": "Service Unavailable", 
            "summary": "Our systems are currently unable to generate your plan. Please try again later.", 
            "days": []
        }

async def generate_nutrition_with_groq(profile: dict) -> dict:
    """
    Fallback function to generate nutrition plans using Groq SDK and Llama 3.3.
    """
    logger.info("Triggering Groq fallback for nutrition plan generation.")
    try:
        user_prompt = build_nutrition_prompt(profile)
        
        response = await groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": NUTRITION_SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            model=GROQ_MODEL,
            temperature=0.7,
            max_tokens=4096,
            response_format={"type": "json_object"}
        )
        
        response_text = response.choices[0].message.content
        return json.loads(response_text)
        
    except Exception as e:
        logger.error(f"Groq fallback nutrition generation failed: {e}")
        # Last resort return structure when both primary and fallback fail
        return {
            "plan_name": "Service Unavailable", 
            "daily_calories_target": 0, 
            "summary": "Our systems are currently unable to generate your nutrition plan. Please try again later.", 
            "nutrition_tips": [],
            "days": []
        }
