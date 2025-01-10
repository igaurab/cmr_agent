### CMRAgent

CMRAgent is an AI agent that interfaces with NASA's Common Metadata Repository(CMR) using natural language commands

### Installation

Note: This project was developed using python version 3.12.4

1. Create a virtual environment: `virtualenv venv` 
2. Activate the virtual environment: `. venv/bin/activate`
3. Install required dependencies: `pip install -r requirements.txt`
4. Run the web based app: `cd src && streamlit run app.py`
5. Run app in cli: `cd src && python main.py`

If you have make installed:

1. `make install` : Creates an virtualenv and installs all dependencies
2. `make run` : Run's streamlit application
3. `make cli` : Run the cli interface
4. `make clean` : Removes virtualenv

Note: Create an `.env` file from the `.env.sample` file and update your OPENAI credentials before running the app

### Features

* Natural language queries for NASA CMR.
* Search through collections
    * Supported query params: temporal, spatial and keyword based search
* Search through granules using collection id
* Supports multi-conversations: Ask followup on questions or for granules for a particular collection
* CLI and web-based (Streamlit) interface options.
* View debug logs in Streamlit application

![CMRAgent Demo](assets/demo.gif)