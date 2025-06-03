from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import requests

load_dotenv()

# Configure OpenAI
openai_api_key = os.getenv('OPENAI_API_KEY')
openai_api_url = os.getenv('OPENAI_API_URL')

dalle_key = os.getenv('DALLE_KEY')
dalle_url = os.getenv('DALLE_URL')
print(dalle_key, dalle_url)
app = Flask(__name__)
CORS(app, origins=["http://localhost:3000",
                   "http://127.0.0.1:3000"])


@app.route('/')
def hello():
    return 'Stadstuin Backend API'


@app.route('/build_prompt', methods=['POST'])
def build_prompt():
    try:
        data = request.get_json()
        wishes = data.get('wishes', [])

        # Create the initial prompt with the wishes
        initial_prompt = """Below are individual wishes for our shared Amsterdam stadstuin.
                 Combine every wish into **one** richly detailed, realistic scene descriptionthat DALL-E 3 can render.
                 Follow the CO-STAR guard-rails you have been given.
                 TARGET LENGTH ≤ 1000 characters."""

        for wish in wishes:
            initial_prompt += f"– {wish['name']}: {wish['wish']}\n"

        headers = {
            "Content-Type": "application/json",
            "api-key": openai_api_key
        }

        payload = {
            "messages": [
                {"role": "system", "content": """Context (C)
                    You are an expert prompt composer for DALL-E 3. Your task is to merge multiple citizen wishes into a single, clear yet realistic image description of a shared “stadstuin” (neighbourhood garden) in Amsterdam.

                    Objective (O)
                    Produce one self-contained text prompt (maximum 1000 characters) that DALL-E 3 can render directly, without any additional explanation.

                    Style & Specificity (S)
                    • Be concise and precise: translate the residents’ wishes into a coherent visual description without unnecessary flourish.
                    • Include only plant species, materials, and features appropriate for Amsterdam’s temperate maritime climate (e.g., Dutch elm, European beech, tulips, brick pathways, reclaimed-timber benches).
                    • Exclude brand names, copyrighted characters, and photorealistic depictions of private individuals.

                    Tone / Task (T)
                    Use descriptive language that reflects the residents’ own phrasing and spirit—no embellishments beyond their expressed wishes.

                    Audience (A)
                    Primary: DALL-E 3 (the model).
                    Secondary: Amsterdam residents who will view the final artwork.

                    Requirements / Restrictions (R)
                    • Ensure plausibility: no flying cars, fantasy creatures, skyscrapers, or tropical palms.
                    • Keep the setting clearly Amsterdam: reference canal-house façades, cycling paths, Dutch-design benches, etc.
                    • Create one cohesive scene—do not list wishes or use bullet points.
                    • Follow content policy: no hate speech, explicit nudity, violence, or personal data.
                    • Write in English, preserving Dutch place and plant names when authentic (e.g., “gracht”).
                    • Limit to 1000 characters—trim carefully if needed.
                    • ALWAYS ask DALL-E to generate a photorealistic image.

                    Return only the completed prompt text—no commentary.
                    """},
                {"role": "user", "content": initial_prompt}
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }

        # Call Azure OpenAI to generate a combined prompt
        response = requests.post(openai_api_url, headers=headers, json=payload)
        response_data = response.json()

        # Extract the generated prompt from the response
        generated_prompt = response_data["choices"][0]["message"]["content"]

        return jsonify({
            'prompt': generated_prompt
        })
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'error': str(e)
        }), 400


@app.route('/generate_image', methods=['POST'])
def generate_image():
    try:
        data = request.get_json()
        prompt = data.get('prompt')

        if not prompt:
            return jsonify({
                'error': 'Prompt is required'
            }), 400

        # Generate image using Azure OpenAI
        headers = {
            'Content-Type': 'application/json',
            'api-key': dalle_key
        }

        payload = {
            "model": "dall-e-3",
            "prompt": prompt,
            "size": "1024x1024",
            "style": "vivid",
            "quality": "standard",
            "n": 1
        }

        response = requests.post(dalle_url, headers=headers, json=payload)
        response.raise_for_status()

        return jsonify({
            'imageUrl': response.json()['data'][0]['url']
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


if __name__ == '__main__':
    app.run(debug=True)
