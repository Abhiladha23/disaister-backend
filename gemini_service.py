import os
import google.generativeai as genai

# Configure Gemini using environment variable
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")


def classify_incident(message: str):
    try:
        prompt = f"""
        Analyze the following disaster report and return structured data.

        Report: "{message}"

        Respond ONLY in this JSON format:
        {{
            "disaster_type": "fire/flood/earthquake/cyclone/other",
            "severity": 1-10,
            "risk_level": "LOW/MEDIUM/HIGH/CRITICAL",
            "confidence": 0-100,
            "medical_needed": "YES/NO"
        }}
        """

        response = model.generate_content(prompt)

        # Extract JSON safely
        text = response.text.strip()

        # Sometimes Gemini wraps JSON in ```json ```
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]

        result = eval(text)  # Controlled because we forced JSON format

        # Add satellite verification placeholder (frontend-based validation)
        result["satellite_verified"] = False

        return result

    except Exception as e:
        print("Gemini Error:", e)

        # Safe fallback
        return {
            "disaster_type": "other",
            "severity": 5,
            "risk_level": "MEDIUM",
            "confidence": 50,
            "medical_needed": "NO",
            "satellite_verified": False
        }