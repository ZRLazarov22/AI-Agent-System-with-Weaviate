# Cooking Assistant Backend

## Overview

This project is a backend service for a cooking assistant chatbot using
Flask, Weaviate, and OpenAI.

## Requirements

-   Python 3.9+
-   Weaviate Cloud account
-   OpenAI API key

## Installation

``` bash
git clone <repo-url>
cd <project-folder>
pip install -r requirements.txt
```

Create `.env`:

    WEAVIATE_URL=your_url
    WEAVIATE_API_KEY=your_key
    OPENAI_API_KEY=your_key

## Load Data

``` bash
python load_dataset.py
```

## Run App

``` bash
python app.py
```

Server runs at http://localhost:5000

## API

POST /chat

Request: { "message": "How to cook pasta?", "chat_id": "optional",
"reset": false }

Response: { "reply": "...", "timestamp": "...", "chat_id": "..." }
