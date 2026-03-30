# AI-Agent-System-with-Weaviate

Flask demo app using **Weaviate Query Agent** (pre-built Agents service) over two collections:

- `Recipes` (recipes text + ingredients + rating + URL)
- `Ingredients` (ingredient nutrition facts)

## Requirements

- Python 3.13 (matches the included `.venv`)
- Weaviate Cloud cluster (WCS)
- Weaviate collections loaded via [load_dataset.py](load_dataset.py)

Install deps (important: Agents extra):

`pip install weaviate-client[agents] flask python-dotenv pandas`

## Environment variables

Create a `.env` file in the project root:

```
WEAVIATE_URL=...
WEAVIATE_API_KEY=...
OPENAI_API_KEY=...
```

Notes:

- `OPENAI_API_KEY` is used by Weaviate vectorization (`text2vec-openai`) and also by the Agents service when needed.

## Load data

Run:

`python load_dataset.py`

This recreates `Recipes` and `Ingredients` and inserts the first 1000 rows from each CSV.

## Run the app

`python app.py`

Open `http://127.0.0.1:5000`.

## Query Agent behavior (demo queries)

The chat endpoint is `POST /chat`. The front-end persists a `chat_id` and sends it with each message so **follow-up** questions reuse agent context.

Use these prompts to demonstrate the required 5 query types:

1) **Basic search (single-collection)**

`Suggest 3 quick chicken recipes.`

2) **Multi-collection (Recipes + Ingredients)**

`Suggest a salmon recipe and tell me roughly how much protein the main ingredient has according to Ingredients.`

3) **Follow-up question (uses context)**

After the agent suggests recipes:

`Out of those, which one has the highest rating? Include the link.`

4) **Filtering / aggregation logic**

`Find recipes with rating above 4.5 and give me the top 5 by rating.`

5) **Looser phrasing**

`I have eggs, tomatoes, and cheese and I want something light for dinner. What would you recommend?`