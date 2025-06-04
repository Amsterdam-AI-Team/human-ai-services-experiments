# FastText Language Detection Script

This repository contains a simple Python script (`detect_language.py`) that allows a user to input text via the terminal and uses Facebook’s fastText library to detect the language of the input. It will print the detected language code and a confidence score.

---

## Contents

- `detect_language.py`  
  The main script. It loads (or downloads, if missing) the pre-trained fastText language identification model (`lid.176.ftz`) and accepts user input to identify its language.

- `requirements.txt`  
  Lists the Python dependency (`fasttext`) needed for the script.

- `README.md`  
  Instructions on how to set up and run the script.

---

## Prerequisites

- Python 3.7 or higher
- Internet connection (only the first time to download the model if it’s not already present)

---

## Setup

1. **Clone or download this repository** to your local machine.

2. **Create and activate a virtual environment** (recommended):

   ```bash
   python3 -m venv venv
   source venv/bin/activate       # macOS / Linux
   venv\Scripts\activate.bat      # Windows
