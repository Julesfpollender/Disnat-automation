# Disnat-automation
Selenium bot to automate Disnat transactions

# First time start
* Install Python
* Run `pip install -r requirements.txt`
* Setup a `.env` file at the project roots. Follow `.env_example` structure

# Start
* Run `python .\src\main.py`

# Build
* Run `pyinstaller --onefile src/main.py --name disnat-automation`.
`.exe` will be created under `/dist`. Do not forget to set a `.env` file with the `.exe`