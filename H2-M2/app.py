from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from milestone1 import handle_interaction
from milestone2 import generate_story, process_user_input, scenarios 
import os

load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/')

@app.route('/')
def index():
    return render_template('about.html', active='index')

@app.route('/milestone1', methods=['GET', 'POST'])
def interaction_1():
    result = handle_interaction()
    if result:
        return result
    return render_template('milestone1.html', active='interaction_1')



@app.route('/milestone2', methods=['GET', 'POST'])
def interaction_2():
    if request.method == 'POST':
        if 'user_input' in request.form:
            scenario = request.form.get('scenario')
            user_input = request.form.get('user_input')
            print(f"收到用户输入: {user_input} for 场景: {scenario}")
            
            story, image_url = process_user_input(scenario, user_input)
            print(f"返回故事: {story[:100]}...")
            print(f"返回图片URL: {image_url}")
            
            return jsonify({
                "story": story,
                "image_url": image_url
            })
        else:
            # 处理场景选择
            scenario = request.form.get('scenario')
            initial_story, image_url = generate_story(scenario)
            return render_template('milestone2_story.html', 
                                initial_story=initial_story, 
                                image_url=image_url,
                                scenario=scenario)
    
    return render_template('milestone2_select.html', scenarios=scenarios)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
