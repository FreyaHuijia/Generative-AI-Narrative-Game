from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import os
from openai import OpenAI
from huggingface_hub import InferenceClient
from PIL import Image
import io
import requests 

load_dotenv()


app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/')

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
hf_client = InferenceClient(os.getenv("HF_API_KEY"))

# Get the current working directory
cwd = os.getcwd()

# Initialize message list
msg_list = [
    {"role": "system", "content": "Create an interactive text-based adventure game where the user controls the actions of a character through written commands, and you respond with dynamic, narrative-driven outcomes. The game should have a magical, whimsical atmosphere similar to a Studio Ghibli film, incorporating elements like spirits, fairies, and mystical creatures."},
    {"role": "assistant", "content": "As the sun begins to set, casting a golden hue over the landscape, you find yourself standing at the edge of the Whispering Woods—a magical forest known for its whimsical creatures and hidden secrets. The air is thick with the scent of blooming flowers and the soft hum of nature surrounds you, as if the forest itself is alive and beckoning you to explore. What do you want to do now?"}
]

def extract_scene_description(message):
    return message[:100] + "..."

@app.route('/')
def index():
    return render_template('about.html')

API_URL = "https://api-inference.huggingface.co/models/aleksa-codes/flux-ghibsky-illustration"
headers = {"Authorization": "Bearer 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"}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.content

@app.route('/milestone1', methods=['GET', 'POST'])
def interaction_1():
    global msg_list
    if request.method == 'POST':
        user_input = request.form['user_input']
        
        # Add user input to the message list
        msg_list.append({"role": "user", "content": user_input})
        
        # Calling the GPT API
        completion = client.chat.completions.create(
             model="gpt-4o-mini",
            temperature=0.2,
            max_tokens=500,
            messages=msg_list
        )
        
        gpt_response = completion.choices[0].message.content
        msg_list.append({"role": "assistant", "content": gpt_response})
        
    # Extract scene description from GPT response
        scene_description = extract_scene_description(gpt_response)
        
        # Generate image
        image_prompt = f"A Ghibli-style painting: {scene_description}. In the foreground is a 12-year-old girl with long golden hair, wearing a blue dress."
        image_bytes = query({"inputs": image_prompt})
        
        # Save the generated image
        image = Image.open(io.BytesIO(image_bytes))
        file_name = secure_filename(f"generated_image_{len(msg_list)}.png")
        upld_path = os.path.join(cwd, 'static', 'imgs', file_name)
        image.save(upld_path)
        
        return jsonify({"response": gpt_response, "image_url": f"/imgs/{file_name}"})
    
    return render_template('milestone1.html', active='interaction_1')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
