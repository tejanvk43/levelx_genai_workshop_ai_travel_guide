from flask import Flask, jsonify, request
from flask_cors import CORS
from google import genai
import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

PROMPTS = {
    "Summary": """
You are a professional tourist guide.

Provide a high-level overview of "{place}" in {language}.

Focus on:
- The historical significance
- Why the place is famous
- Key architectural or cultural highlights

Keep the explanation concise, engaging, and easy to follow.
Avoid excessive details and dates.
Limit the response to around 200 words.

Respond ONLY in {language}.
""",

    "Detailed": """
You are a professional tourist guide.

Provide a detailed and immersive explanation of "{place}" in {language}.

Cover:
- Historical background and timeline
- Architectural design and unique features
- Cultural importance and notable events
- Interesting facts and visitor insights

Explain concepts clearly and in a storytelling manner.
Include relevant details and examples to create a rich experience.
Limit the response to around 400 words.

Respond ONLY in {language}.
"""
}


def generate_speech(description, voice_id, locale):

    url = "https://global.api.murf.ai/v1/speech/stream"

    headers = {
        "api-key": os.getenv("MURF_API_KEY"),
        "Content-Type": "application/json"
    }

    data = {
        "text": description,
        "voiceId": voice_id,
        "locale": locale
    }

    response = requests.post(
        url,
        headers=headers,
        json=data
    )

    print("Murf status:", response.status_code)

    if not response.ok:
        print("Murf error:", response.text)
        raise Exception(response.text)

    return response.content


def generate_description(place, answer_type, language):

    prompt = PROMPTS[answer_type].format(
        place=place,
        language=language
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text


@app.route("/generate-audio-guide", methods=["POST"])
def generate_audio_guide():

    try:

        data = request.get_json()

        place = data.get("place")
        answer_type = data.get("answerType")
        language = data.get("language")
        voice_id = data.get("voiceId")
        locale = data.get("locale")

        if not place or not answer_type or not language:
            return jsonify({
                "error": "place, answerType and language are required"
            }), 400

        description = generate_description(
            place,
            answer_type,
            language
        )

        audio_bytes = generate_speech(
            description,
            voice_id,
            locale
        )

        audio_base64 = base64.b64encode(
            audio_bytes
        ).decode("utf-8")

        return jsonify({
            "description": description,
            "audio_base64": audio_base64
        })

    except Exception as e:

        import traceback
        traceback.print_exc()

        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )