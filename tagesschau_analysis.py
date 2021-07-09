# %%
# imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
# %%
# load data
data = pd.read_excel("data/tagesschau_articles.xlsx")

# check if date column matches scraped date to validate our data


# format time string to datetime obj and drop string from df
data["date_and_time"] = pd.to_datetime(data["time_text"], format="%d.%m.%Y %H:%M Uhr")
data["proofdate"] = data["date_and_time"].dt.date
data.drop(columns=["time_text"], inplace=True)

# format time strings to datetime
data["date"] = pd.to_datetime(data["date"], format="%d/%m/%Y")

# store values where datestring has different date than date column
not_matching = data["date"].compare(data["proofdate"])

# all values where the columns dont match, are at around 12pm,
# so they probably are missclasified as the previous day, lets take the proof date column as the real date for this reason
# lets drop proof date and date column because qwe have the time already as a dt obj
data.drop(columns=["proofdate", "date"], inplace=True)

# %%

# get hour and minute as column
data["military_time"] = data["date_and_time"].dt.strftime("%H%M").astype(int)
# get distribution by time
time_distribution = data.groupby(by=["military_time"]).apply(len)

# get most used words and remove commas
god_string = " ".join(data["article"]).replace(",", "")
most_used_words = Counter(god_string.split()).most_common(1000)

# filter out non capitalized words, since they probably are verbs
keyword_list = []
pronouns = ["Der", "Die", "Das"]

while len(keyword_list) <= 100:
    keyword = most_used_words[0][0]
    # add word to list if first letter is capitalized
    is_capitalized = keyword[0].isupper()
    # add to keyword list if word is capitalized and not a pronoun
    if is_capitalized and keyword not in pronouns:
        keyword_list.append(most_used_words.pop(0))
    # delete word from most used if its not capitalized
    else:
        del most_used_words[0]
# %%
country_data = pd.read_excel("data/country_data.xlsx")

for pn in pronouns:
    country_data["Amtliche Vollform"] = country_data["Amtliche Vollform"].str.replace(pn, "")

countries_list = []
# filter countries by use

# loop over keywords
for kw, count in keyword_list:

    # loop over country data
    for col in country_data.columns:
        # if keyword in country data, add it to the list and continue to next word
        if kw.upper() in country_data[col].str.upper().values:
            countries_list.append([kw, count])
            continue
# %%

# plot occurence of countries
countries, country_counts = zip(*countries_list)

plt.figure(figsize=(10, 10))
plt.title("Mentions of Country")
plt.pie(
    country_counts, 
    labels=countries,
    # use abosulte counts as labels
    autopct=(lambda x: int(float(x) * sum(country_counts)) // 100),
    )
# show plot
plt.show()
