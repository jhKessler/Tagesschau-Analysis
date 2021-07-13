
# imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

# load data
data = pd.read_excel("data/tagesschau_articles.xlsx")

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
# lets drop proof date because we have the time already as a dt obj in the "date_and_time" column
data.drop(columns=["proofdate"], inplace=True)

# get military time as column
data["military_time"] = data["date_and_time"].dt.strftime("%H%M").astype(int)

# get distribution by time
time_distribution = data.groupby(by=["military_time"]).apply(len)

# get most used words and remove commas
god_string = " ".join(data["article"]).replace(",", "")
most_used_words = Counter(god_string.split()).most_common(1000)

def filter_uncapitalized(count_list, n_return: int):
    """Filter out uncapitalized words in most_common list"""
    return_list = []
    while len(return_list) < n_return:
        keyword = count_list[0][0]
        # add word to list if first letter is capitalized
        is_capitalized = keyword[0].isupper()
        # add to keyword list if word is capitalized and not a pronoun
        if is_capitalized and keyword not in pronouns:
            return_list.append(count_list.pop(0))
        # delete word from most used if its not capitalized
        else:
            del count_list[0]
    return return_list

# filter out non capitalized words, since they probably are verbs
pronouns = ["Der", "Die", "Das"]
keyword_list = filter_uncapitalized(most_used_words, n_return=100)

# check for most mentioned countries
# load country names and abbreviations
country_data = pd.read_excel("data/country_data.xlsx")
# remove pronouns from "Amtliche Vollform" column
for pn in pronouns:
    country_data["Amtliche Vollform"] = country_data["Amtliche Vollform"].str.replace(pn, "")

# list for saving country data
countries_list = []

# filter countries by mentions
# loop over keywords
for kw, count in keyword_list:
    # loop over country data
    for col in country_data.columns:
        # if keyword in country data, add it to the list and continue to next word
        if kw.upper() in country_data[col].str.upper().values:
            countries_list.append([kw, count])
            continue

# plot occurence of countries
countries, country_counts = zip(*countries_list)

plt.figure(figsize=(10, 10))
plt.title("Tagesschau Mentions by Country", fontsize=20)
plt.pie(
    country_counts, 
    labels=countries,
    # use absolute counts as labels
    autopct=(lambda x: int(float(x) * sum(country_counts)) // 100),
    )
# save plot
plt.savefig("graphs/Other/mentions_by_country.png")
plt.close()

# plot description length over time
data["desc_length"] = data["article"].str.len()
data["year"] = data["date_and_time"].dt.year
avg_desc_length_per_year = data.groupby(by=["year"])["desc_length"].mean()

plt.figure(figsize=(10, 5))
plt.title("Description length over time", fontsize=20)

plt.plot(
    avg_desc_length_per_year.index,
    avg_desc_length_per_year, 
    linewidth=6
    )

plt.yticks(np.arange(0, 600, 50))
plt.xlabel("Year")
plt.ylabel("Character Count")
# save graph
plt.savefig("graphs/Other/description_length_over_time.png")
plt.close()

# get episode count per day
episodes_per_day = data["date_and_time"].dt.date.value_counts().to_frame()
episodes_per_day.reset_index(inplace=True)
episodes_per_day.rename(columns={"index": "date", "date_and_time": "episodes_that_day"}, inplace=True)

# format date column so we can merge on it
data["date"] = data["date"].dt.date
data = data.merge(episodes_per_day, how="left", on=["date"])

# look at the days where there are more than 2 shows
more_than_two = data[data["episodes_that_day"] > 2]
more_than_two = more_than_two.groupby("date")

# get topics for that day
def get_topics(day_series: pd.Series, n_topics: int):
    """Looks for overlapping words in the different shows of one day
        returns list of top 3 overlapping words"""
    top_keywords = []
    god_string_whole_day = " ".join(day_series).replace(",", "")
    word_counts = Counter(god_string_whole_day.split()).most_common(20)
    return filter_uncapitalized(word_counts, n_return=n_topics)

# filter topics on days where there are more than 2 episodes
more_than_two = more_than_two["article"].apply(lambda x: get_topics(x, n_topics=3)).to_frame()
more_than_two = more_than_two["article"].apply(pd.Series)
more_than_two.columns = [f"Keyword_{i}" for i in range(1, 4)]
more_than_two = more_than_two.applymap(lambda x: x[0])


# lets look at the mentions of specific words over time
def get_mentions_over_time(word: str, group_by_quarter):
    """Creates timeline of mentions of a specific word"""
    timeline = by_quarter["article"].apply(lambda x: get_mentions_in_quarter(word, x))
    timeline = list(timeline.to_dict().items())
    timeline.sort(key=lambda x: int(x[0].split("/")[1])**2 + int(x[0].split("/")[0]))
    return timeline

def get_mentions_in_quarter(word: str, quarter_series: pd.Series):
    """Returns the number of mentions of a specific word in a quarter"""
    quarter_words = " ".join(quarter_series).replace(",", "").lower().split()
    return quarter_words.count(word.lower())

# group data by quarter
data["quarter"] = data["date_and_time"].dt.quarter.astype(str) + "/" + data["year"].astype(str)
by_quarter = data.groupby(by=["quarter"])

# plot mentions of word over time

def plot_trend(word: str, save: bool, show: bool):
    """Plots/saves trend of a specific word"""
    quarters_, word_count_ = zip(*get_mentions_over_time(word, by_quarter))

    plt.figure(figsize=(30, 5))
    plt.title(f"Mentions of word \"{word}\" by quarter")
    plt.plot(quarters_, word_count_)
    plt.xlabel("Quarter")
    plt.ylabel("Mentions")

    if save:
        plt.savefig(f"graphs/mention_graphs/{word}_mentions.png")
    if show:
        plt.show()

words_of_interest = ["coronavirus", "china", "anschlag", "EU", "russland", "krise", "klimawandel", "trump", "biontech"]
# for w in words_of_interest:
#     plot_trend(w, save=True, show=False)


# filter out all episodes of "Tageschau extra"
tagesthemen_extra = data[data["title"].str.lower().str.contains("extra")]
# its itneresting that the average description length is way shorter than normal
extra_by_year = tagesthemen_extra.groupby("year")
by_year = data.groupby("year")
# get average length
avg_length_special_episodes = extra_by_year["desc_length"].mean()
avg_length_normal_episodes = by_year["desc_length"].mean()

# make bar chart
fig, ax = plt.subplots(figsize=(10, 10))
b1 = ax.bar(x=avg_length_normal_episodes.index, height=avg_length_normal_episodes)
b2 = ax.bar(x=avg_length_normal_episodes.index, height=avg_length_special_episodes)

ax.legend(["Normal Episodes", "Special Episodes"])
ax.set_xticks(avg_length_normal_episodes.index)
ax.set_ylabel("Description length", fontsize=20)
ax.bar_label(b1, avg_length_normal_episodes.astype(int), fontsize=12)
ax.bar_label(b2, avg_length_special_episodes.astype(int), label_type="center", fontsize=12)
# save
plt.savefig("graphs/other/special_episode_length.png")

# group description length by weekday

data["wochentag"] = data["date_and_time"].dt.weekday
by_weekday = data.groupby("wochentag")["desc_length"].mean()
# plot relation
fig, ax = plt.subplots(figsize=(10, 10))
day_names = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]

p1 = ax.bar(x=day_names, height=by_weekday)
ax.bar_label(p1, by_weekday.astype(int))
ax.set_ylabel("Description Length", fontsize=15)
plt.savefig("graphs/other/desc_length_weekday.png")
plt.close()