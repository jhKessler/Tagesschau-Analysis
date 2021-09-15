# imports
import pandas as pd
from tqdm import tqdm
from transformers import pipeline

# init pandas progressbar
tqdm.pandas()

# load data
print("Loading Data...")
data = pd.read_excel("data\cleaned_data.xlsx")

# load model
print("Loading Model...")
classifier = pipeline("zero-shot-classification", model="Sahajtomar/German_Zeroshot", device=0)

categories = [
    "Politik",
    "Wirtschaft",
    "Lottozahlen",
    "Sport",
    "Naturkatastrophe",
    "Kunst und Kultur",
    "Terrorismus"
    "Pandemie"
]

def categorise_topic(topic_str: str) -> str:
    """Categorizes Topic"""
    model_output = classifier(topic_str, categories)
    labels = model_output["labels"]
    output = model_output["scores"]
    category_index = output.index(max(output))
    return labels[category_index]

data["category"] = data["topic"].progress_apply(categorise_topic)

data.to_excel("data/final_format.xlsx", index=False)