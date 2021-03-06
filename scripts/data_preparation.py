# imports
import pandas as pd
import numpy as np
from tqdm import tqdm
import torch
from transformers import pipeline

# load data
print("Loading Data...")
data = pd.read_excel("data/raw.xlsx")
print("Done")

print("Cleaning data...")
# format time string to datetime obj and drop string from df
data["date_and_time"] = pd.to_datetime(data["time_text"], format="%d.%m.%Y %H:%M Uhr")
data.drop(columns=["time_text"], inplace=True)
data.reset_index(inplace=True)
data["sendung_id"] = data.index

# format time strings to datetime
data["date"] = pd.to_datetime(data["date"], format="%d/%m/%Y")

# override date on entries where date and proofdate differ
data["proofdate"] = data["date_and_time"].dt.date
data["date"] = data["proofdate"]
data.drop(columns=["proofdate"], inplace=True)
print("Done")

# adding year, month, quarter, day, weekday, and timeslot as military time
print("Adding Features...")
data["year"] = data["date_and_time"].dt.year
data["month"] = data["date_and_time"].dt.month
data["quarter"] = data["year"].astype(str) + "/" + data["date_and_time"].dt.quarter.astype(str)
data["day"] = data["date_and_time"].dt.day
data["weekday"] = data["date_and_time"].dt.day_name()
data["timeslot"] = data["date_and_time"].dt.strftime("%H%M").astype(int) - data["date_and_time"].dt.strftime("%H%M").astype(int) % 20

data.drop_duplicates(
    subset=["date_and_time", "title"],
    inplace=True
)

# add len of description to data
data["desc_length"] = data["article"].str.len()
data.loc[data["desc_length"] == 1, "article"] = data.loc[data["desc_length"] == 1, "article"].apply(lambda x: [])
data.loc[data["desc_length"] == 1, "desc_length"] = 0
# add number of episode of day to dataframe
episodes_that_day = data.groupby("date").size().to_frame()
episodes_that_day.columns = ["episodes_that_day"]
data = data.merge(episodes_that_day, how="left", on="date")

# format article to different topics and add number of topics that episode
data["article"] = data["article"].str.split(",")
data = data[data["article"].str.len() > 0]

# replace nan vals with empty list
data["article"] = data["article"].apply(lambda x: x if isinstance(x, list) else [])
data["num_topics"] = data["article"].str.len()

# format title column so they are rightly classified
data["title"] = data["title"].str.strip().str.lower()


data.to_pickle("data/sendungen.pkl")

# unstack "article" column to every topic
stacked_column = "article"
other_columns = data.columns.difference([stacked_column])
all_topics = [topic for sublist in data[stacked_column] for topic in sublist]

unstacked_df = {
    col: np.repeat(data[col], data["num_topics"]) for col in other_columns
}
unstacked_df["topic"] = all_topics
data = pd.DataFrame(unstacked_df)

# cast topic column to str and drop missing entries
data.dropna(subset=["topic"], inplace=True)
data = data[data["topic"] != ""]
data["topic"] = data["topic"].astype("str")

reoccuring = data["topic"].str.strip().str.lower().value_counts()
reoccuring = reoccuring[reoccuring > 5]
data["topic"] = data["topic"].str.strip()
data.reset_index(drop=True, inplace=True)
reoccuring = data[data["topic"].str.lower().isin(reoccuring.index)]
data.drop(index=reoccuring.index, inplace=True)
reoccuring.append(data.loc[data["topic"].str.contains("das wetter", case=False)])
data.drop(index=data.loc[data["topic"].str.contains("das wetter", case=False)].index, inplace=True)
reoccuring.to_excel("data/reoccuring.xlsx", index=False)

num_topics = data.groupby("sendung_id").size().to_frame()
data = data.merge(num_topics, how="left", on="sendung_id")
data = data.drop(columns=["num_topics"]).rename(columns={0: "num_topics"})
print("Done")

# init pandas progressbar
tqdm.pandas()

# load model
print("Loading Model...")
classifier = pipeline(
    "zero-shot-classification", 
    model="Sahajtomar/German_Zeroshot", 
    device=torch.cuda.current_device()
    )
print("Done")

categories = [
    "Politik",
    "Wirtschaft",
    "Sport",
    "Naturkatastrophe",
    "Kunst und Kultur",
    "Terrorismus",
    "Lottozahlen"
]

def categorise_topic(topic_str: str) -> str:
    """Categorizes Topic via NLP"""
    try:
        model_output = classifier(topic_str, categories)
    except ValueError:
        pass
    labels = model_output["labels"]
    output = model_output["scores"]
    category_index = output.index(max(output))
    return labels[category_index]

print("Categorizing Topics...")
data["category"] = data["topic"].progress_apply(categorise_topic)
data["topic"] = data["topic"].str.strip()
print("Done")

# save to file
print("Saving to file...")
data.to_pickle("data/topics.pkl")
print("Done")