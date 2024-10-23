## General Notes for Running this Flask App!:
---
To run the tool locally download the code and follow the steps below:
- Open command prompt & change directory to the project folder `cd <folder_path>`
- make sure your Python version >= 3.12 
- Set up a virtual environment for python, in the command prompt:
    - For Windows- 
        - run `python -m venv .venv`
        - to activate the virtual envirnoment- `.venv\Scripts\activate.bat`
    - For MAC- 
        - first run `pip install virtualenv`
        - then `virtualenv .venv`
        - to activate the virtual envirnoment- `source .venv/bin/activate`
    - note- ".venv" is the name of the environment, so you can use whatever name you want.

- Once the virtual environment is active then (* only if you are running the app for the first time/or there is a change in requirements.txt on the device, otherwise skip this step*) `pip install -r requirements.txt`

- create ".env" file to store all the environment variables for Flask, Huggingface, OpenAI & Langchain. Copy this code into the ".env" file-
    - `FLASK_APP = app`
    - `FLASK_RUN_PORT = 8080`
    - `FLASK_DEBUG = True`
    - `HF_TOKEN = ""`
    - `OPENAI_API_KEY = ""`