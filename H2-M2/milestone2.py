from flask import jsonify, request
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from PIL import Image
import io
import os
from werkzeug.utils import secure_filename
import requests
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o", 
    temperature=0.7,
    max_tokens=800,
    timeout=None,
    max_retries=2
)

scenarios = {
    "forest": {
        "description": "Mystic Forest - A magical forest brimming with mysterious creatures and shimmering lights, where you, a little girl may encounter a magical old tree and talking fairies guiding you through hidden paths and enchanting adventures.",
        "initial_text": "As the sun begins to set, casting a golden hue over the landscape, you find yourself standing at the edge of the Whispering Woods—a magical forest known for its whimsical creatures and hidden secrets. The air is thick with the scent of blooming flowers and the soft hum of nature surrounds you, as if the forest itself is alive and beckoning you to explore. What do you want to do now?"
    },
    "canyon": {
        "description": "Desert Canyon - A stunning landscape of towering sandstone cliffs and rolling sand dunes beneath a brilliant blue sky, where you, a little girl may discover treasures hidden in caves and uncover the secrets of the underground.",
        "initial_text": "Under the vast, cloudless sky, the sun casts warm golden light across the Desert Canyon. Towering sandstone cliffs rise around you, their colors shifting in the sunlight, while sand dunes stretch endlessly ahead. The wind whispers softly through the canyons, carrying with it the ancient secrets of this place. Somewhere among the cliffs, hidden caves and long-lost treasures await discovery. What do you want to do now?"
    },
    "snow": {
        "description": "Snowy Adventure - A picturesque winter wonderland blanketed in fresh, sparkling snow, where you, a little girl may meet wind sprites and explore the mysteries of the icy kingdom.",
        "initial_text": "A gentle snow begins to fall, blanketing the landscape in soft white. The Snowy Adventure unfolds before you, as towering pines dusted in snow create a serene winter wonderland. The air is crisp and filled with the magic of the icy kingdom, where wind sprites drift playfully and hidden mysteries await beneath the snow. The silence is broken only by the distant echo of snowflakes landing softly around you. What do you want to do now?"
    }
}

scenario_messages = {}

def extract_scene_description(story_continuation):
    """提取故事中的前200个字符作为场景描述"""
    try:
        # 直接截取前200个字符
        scene_description = story_continuation[:600]
        
        # 如果最后一个词被截断，找到最后一个完整的句子
        last_period = scene_description.rfind('.')
        if last_period > 0:
            scene_description = scene_description[:last_period + 1]
            
        print("\n=== 场景描述 ===")
        print(scene_description)
        print("==========================")
        
        return scene_description
        
    except Exception as e:
        print(f"Scene extraction error: {str(e)}")
        return story_continuation[:600] + "..."

def query(payload):
    API_URL = "https://api-inference.huggingface.co/models/aleksa-codes/flux-ghibsky-illustration"
    headers = {"Authorization": "Bearer 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"}
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.content

def generate_story(scenario):
    """
    Return the initial text and image for the scenario
    """
    if scenario not in scenarios:
        return "Invalid scenario selection", "/imgs/default.jpg"
    
    return scenarios[scenario]["initial_text"], f"/imgs/{scenario}.jpg"

def getRetriever(dir):
    """
    获取向量数据库检索器
    """
    embeddings_used = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorDB = Chroma(persist_directory=dir, embedding_function=embeddings_used)
    retriever = vectorDB.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    return retriever

def process_user_input(scenario, user_input):
    """
    Process user input and generate response
    """
    if scenario not in scenarios:
        return "Invalid scenario selection", "/imgs/default.jpg"
    
    try:
        # 获取检索器
        db_dir = os.path.join(os.getcwd(), "chroma_db")
        retriever = getRetriever(db_dir)
        
        # 构建带有检索内容的提示
        system_content = (
            "You are an expert storyteller creating an interactive adventure game for children. "
            "Use the following pieces of retrieved context from Adventure and Fantasy stories to enhance the narrative:\n\n"
            "{context}\n\n"
            "Continue the story based on the user's action, then give them recommendations for what to do next." 
            "Focus on the most important and magical elements while keeping the narrative "
            "engaging but succinct."
        )
        
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                system_content
            ),
            (
                "human", 
                f"In this {scenario} scenario, You decide to {user_input}. What happens next?"
            ),
        ])
        
        # 创建 RAG 链
        chain = prompt | llm | StrOutputParser()
        
        # 生成故事
        story_continuation = chain.invoke({
            "context": retriever,
            "scenario": scenario,
            "user_input": user_input
        })
        
        # Extract scene description and print it
        scene_description = extract_scene_description(story_continuation)
        print("\n=== 场景总结 ===")
        print(scene_description)
        print("================")
        
        scene_keywords = {
            "forest": "magical forest",
            "canyon": "vast desert canyon",
            "snow": "snowy winter wonderland"
        }
        
        image_prompt = (
            f"Ghibli-style painting"
            f"a 12-year-old girl with long golden hair in a blue dress is actively {user_input}. "
            f"{scene_description}"
        )
        
        print("\n=== Image Prompt ===")
        print(image_prompt)
        print("==================")
        
        try:
            image_bytes = query({"inputs": image_prompt})
            image = Image.open(io.BytesIO(image_bytes))
            file_name = secure_filename(f"generated_image_{scenario}_{hash(story_continuation)}.png")
            upld_path = os.path.join(os.getcwd(), 'static', 'imgs', file_name)
            image.save(upld_path)
            
            return story_continuation, f"/imgs/{file_name}"
            
        except Exception as e:
            print(f"Image generation error: {str(e)}")
            return story_continuation, f"/imgs/{scenario}.jpg"
            
    except Exception as e:
        print(f"Story generation error: {str(e)}")
        return "Sorry, an error occurred. Please try again.", f"/imgs/{scenario}.jpg"

def handle_interaction():
    if request.method == 'POST':
        scenario = request.form['scenario']
        user_input = request.form['user_input']
        
        print(f"\n收到用户输入: {user_input} for 场景: {scenario}")  # 已有的打印
        
        if scenario not in scenarios:
            return jsonify({
                "story": "Invalid scenario selection",
                "image_url": "/imgs/default.jpg"
            })
        
        try:
            if scenario not in scenario_messages:
                scenario_messages[scenario] = [
                    {"role": "system", "content": scenarios[scenario]["description"]},
                    {"role": "assistant", "content": scenarios[scenario]["initial_text"]}
                ]
            
            # 获取检索器
            db_dir = os.path.join(os.getcwd(), "chroma_db")
            retriever = getRetriever(db_dir)
            
            # 构建带有检索内容的提示
            system_content = (
                "You are an expert storyteller creating an interactive adventure game for children. "
                "Use the following pieces of retrieved context from Adventure and Fantasy stories to enhance the narrative:\n\n"
                "{context}\n\n"
                "Continue the story based on the user's action, then give them recommendations for what to do next." 
                "Focus on the most important and magical elements while keeping the narrative "
                "engaging but succinct."
            )
            
            prompt = ChatPromptTemplate.from_messages([
                (
                    "system",
                    system_content
                ),
                (
                    "human", 
                    f"In this {scenario} scenario, I decides to {user_input}. What happens next? (Keep the response under 400 words)"  
                ),
            ])
            
            chain = prompt | llm | StrOutputParser()
            
            # Generate story continuation with RAG
            story_continuation = chain.invoke({
                "context": retriever,
                "scenario": scenario,
                "user_input": user_input
            })
            
            # Update message history
            scenario_messages[scenario].append({"role": "user", "content": user_input})
            scenario_messages[scenario].append({"role": "assistant", "content": story_continuation})
            scenario_messages[scenario].append({"role": "assistant", "content": story_continuation})

            # Generate scene-specific image prompts
            scene_keywords = {
                "forest": "magical forest",
                "canyon": "vast desert canyon",
                "snow": "snowy winter wonderland"
            }
            
            image_prompt = (
                f"Ghibli-style painting of a {scene_keywords[scenario]} where "
                f"a 12-year-old girl with long golden hair in a blue dress is doing/saying {user_input}. "
                f"{scene_description}"
            )
            
            print("\n=== Image Prompt ===")
            print(image_prompt)
            print("==================")
            
            try:
                # Generate image
                image_bytes = query({"inputs": image_prompt})
                image = Image.open(io.BytesIO(image_bytes))
                file_name = secure_filename(f"generated_image_{scenario}_{len(scenario_messages[scenario])}.png")
                upld_path = os.path.join(os.getcwd(), 'static', 'imgs', file_name)
                image.save(upld_path)
                
                return jsonify({
                    "story": f"{story_continuation}\n\nSummary: {scene_description}",
                    "image_url": f"/imgs/{file_name}"
                })
                
            except Exception as e:
                print(f"Image generation error: {str(e)}")
                return jsonify({
                    "story": f"{story_continuation}\n\nSummary: {scene_description}",
                    "image_url": f"/imgs/{scenario}.jpg"
                })
                
        except Exception as e:
            print(f"Story generation error: {str(e)}")
            return jsonify({
                "story": "Sorry, an error occurred. Please try again.",
                "image_url": f"/imgs/{scenario}.jpg"
            })
    
    return None
