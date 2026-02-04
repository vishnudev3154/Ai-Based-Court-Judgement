


# app/gemini_chat.py
import google.generativeai as genai
import os

# Configure your API Key
GOOGLE_API_KEY = "AIzaSyDViJN8ZTdL_Jq3THFoesbIBsj8jUC_8kk"  # Keep your key here
genai.configure(api_key=GOOGLE_API_KEY)

def ask_ai(message):
    """
    Sends a message to the Gemini API and returns the text response.
    """
    try:
        # Correct model based on your list
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(message)
        
        if response.text:
            return response.text
        else:
            return "Sorry, I couldn't generate a response."
            
    except Exception as e:
        return f"AI Error: {str(e)}"