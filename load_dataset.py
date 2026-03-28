import math
import pandas as pd
import weaviate
import os
from weaviate.classes.config import Configure, Property, DataType
from dotenv import load_dotenv

load_dotenv()

WEAVIATE_URL = os.getenv("WEAVIATE_URL")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

RECIPES_CSV = "data/recipes.csv"
INGREDIENTS_CSV = "data/ingredients.csv"

BATCH_SIZE = 10


def is_missing(x):
    return pd.isna(x) or x is None or str(x).strip() == ""


def clean_text(x):
    if is_missing(x):
        return None
    return str(x).strip()


def clean_int(x):
    if is_missing(x):
        return None
    try:
        return int(float(str(x).strip()))
    except Exception:
        return None


def clean_float(x):
    if is_missing(x):
        return None
    s = str(x).strip()

    parts = s.split()
    if len(parts) > 1:
        for part in parts:
            try:
                return float(part)
            except Exception:
                pass
        return None

    try:
        return float(s)
    except Exception:
        return None


def show_failed_objects(batch_ctx, label):
    failed = getattr(batch_ctx, "failed_objects", None)
    if failed:
        print(f"\n{label} failed objects: {len(failed)}")
        for obj in failed[:10]:
            print(obj)
    else:
        print(f"\n{label}: no failed_objects reported")


client = weaviate.connect_to_weaviate_cloud(
    cluster_url=WEAVIATE_URL,
    auth_credentials=weaviate.auth.AuthApiKey(WEAVIATE_API_KEY),
    headers={"X-OpenAI-Api-Key": OPENAI_API_KEY},
)

try:
    existing = client.collections.list_all()

    if "Recipes" in existing:
        client.collections.delete("Recipes")
        print("Deleted existing Recipes collection")

    if "Ingredients" in existing:
        client.collections.delete("Ingredients")
        print("Deleted existing Ingredients collection")

    client.collections.create(
        name="Recipes",
        description="Collection of cooking recipes with recipe text, ingredients, directions, times, rating, and nutrition.",
        vector_config=Configure.Vectors.text2vec_openai(),
        properties=[
            Property(name="recipe_name", data_type=DataType.TEXT),
            Property(name="prep_time", data_type=DataType.TEXT),
            Property(name="cook_time", data_type=DataType.TEXT),
            Property(name="total_time", data_type=DataType.TEXT),
            Property(name="servings", data_type=DataType.INT),
            Property(name="ingredients", data_type=DataType.TEXT),
            Property(name="directions", data_type=DataType.TEXT),
            Property(name="rating", data_type=DataType.NUMBER),
            Property(name="url", data_type=DataType.TEXT),
            Property(name="nutrition", data_type=DataType.TEXT),
        ],
    )

    client.collections.create(
        name="Ingredients",
        description="Collection of food ingredients with nutritional properties such as calories, protein, fats, carbs, minerals, and vitamins.",
        vector_config=Configure.Vectors.text2vec_openai(),
        properties=[
            Property(name="Descrip", data_type=DataType.TEXT),
            Property(name="Energy_kcal", data_type=DataType.NUMBER),
            Property(name="Protein_g", data_type=DataType.NUMBER),
            Property(name="Saturated_fats_g", data_type=DataType.NUMBER),
            Property(name="Fat_g", data_type=DataType.NUMBER),
            Property(name="Carb_g", data_type=DataType.NUMBER),
            Property(name="Fiber_g", data_type=DataType.NUMBER),
            Property(name="Sugar_g", data_type=DataType.NUMBER),
            Property(name="Calcium_mg", data_type=DataType.NUMBER),
            Property(name="Iron_mg", data_type=DataType.NUMBER),
            Property(name="Magnesium_mg", data_type=DataType.NUMBER),
            Property(name="Phosphorus_mg", data_type=DataType.NUMBER),
            Property(name="Potassium_mg", data_type=DataType.NUMBER),
            Property(name="Sodium_mg", data_type=DataType.NUMBER),
            Property(name="Zinc_mg", data_type=DataType.NUMBER),
            Property(name="Copper_mcg", data_type=DataType.NUMBER),
            Property(name="Manganese_mg", data_type=DataType.NUMBER),
            Property(name="Selenium_mcg", data_type=DataType.NUMBER),
            Property(name="VitC_mg", data_type=DataType.NUMBER),
            Property(name="Thiamin_mg", data_type=DataType.NUMBER),
            Property(name="Riboflavin_mg", data_type=DataType.NUMBER),
            Property(name="Niacin_mg", data_type=DataType.NUMBER),
            Property(name="VitB6_mg", data_type=DataType.NUMBER),
            Property(name="Folate_mcg", data_type=DataType.NUMBER),
            Property(name="VitB12_mcg", data_type=DataType.NUMBER),
            Property(name="VitA_mcg", data_type=DataType.NUMBER),
            Property(name="VitE_mg", data_type=DataType.NUMBER),
            Property(name="VitD2_mcg", data_type=DataType.NUMBER),
        ],
    )

    print("Collections created")

    recipes_collection = client.collections.get("Recipes")
    ingredients_collection = client.collections.get("Ingredients")

    recipes_df = pd.read_csv(RECIPES_CSV)
    ingredients_df = pd.read_csv(INGREDIENTS_CSV)

    recipes_df = recipes_df.head(1000)
    ingredients_df = ingredients_df.head(1000)

    print(f"Loaded recipes: {len(recipes_df)} rows")
    print(f"Loaded ingredients: {len(ingredients_df)} rows")

    with recipes_collection.batch.dynamic() as batch:
        for _, row in recipes_df.iterrows():
            obj = {
                "recipe_name": clean_text(row["recipe_name"]),
                "prep_time": clean_text(row["prep_time"]),
                "cook_time": clean_text(row["cook_time"]),
                "total_time": clean_text(row["total_time"]),
                "servings": clean_int(row["servings"]),
                "ingredients": clean_text(row["ingredients"]),
                "directions": clean_text(row["directions"]),
                "rating": clean_float(row["rating"]),
                "url": clean_text(row["url"]),
                "nutrition": clean_text(row["nutrition"]),
            }
            batch.add_object(properties=obj)

    show_failed_objects(batch, "Recipes")
    print("Finished inserting Recipes")

    with ingredients_collection.batch.dynamic() as batch:
        for _, row in ingredients_df.iterrows():
            obj = {
                "Descrip": clean_text(row["Descrip"]),
                "Energy_kcal": clean_float(row["Energy_kcal"]),
                "Protein_g": clean_float(row["Protein_g"]),
                "Saturated_fats_g": clean_float(row["Saturated_fats_g"]),
                "Fat_g": clean_float(row["Fat_g"]),
                "Carb_g": clean_float(row["Carb_g"]),
                "Fiber_g": clean_float(row["Fiber_g"]),
                "Sugar_g": clean_float(row["Sugar_g"]),
                "Calcium_mg": clean_float(row["Calcium_mg"]),
                "Iron_mg": clean_float(row["Iron_mg"]),
                "Magnesium_mg": clean_float(row["Magnesium_mg"]),
                "Phosphorus_mg": clean_float(row["Phosphorus_mg"]),
                "Potassium_mg": clean_float(row["Potassium_mg"]),
                "Sodium_mg": clean_float(row["Sodium_mg"]),
                "Zinc_mg": clean_float(row["Zinc_mg"]),
                "Copper_mcg": clean_float(row["Copper_mcg"]),
                "Manganese_mg": clean_float(row["Manganese_mg"]),
                "Selenium_mcg": clean_float(row["Selenium_mcg"]),
                "VitC_mg": clean_float(row["VitC_mg"]),
                "Thiamin_mg": clean_float(row["Thiamin_mg"]),
                "Riboflavin_mg": clean_float(row["Riboflavin_mg"]),
                "Niacin_mg": clean_float(row["Niacin_mg"]),
                "VitB6_mg": clean_float(row["VitB6_mg"]),
                "Folate_mcg": clean_float(row["Folate_mcg"]),
                "VitB12_mcg": clean_float(row["VitB12_mcg"]),
                "VitA_mcg": clean_float(row["VitA_mcg"]),
                "VitE_mg": clean_float(row["VitE_mg"]),
                "VitD2_mcg": clean_float(row["VitD2_mcg"]),
            }
            batch.add_object(properties=obj)

    show_failed_objects(batch, "Ingredients")
    print("Finished inserting Ingredients")

    print("\nRecipes and Ingredients loaded successfully.")

finally:
    client.close()