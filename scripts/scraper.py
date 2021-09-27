#
# scraper for getting the data from article descriptions
#

import time
import datetime
import requests
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup
    
DATE_FORMAT = "%d/%m/%Y"
ARCHIVE_URL = "https://www.tagesschau.de/multimedia/video/videoarchiv2~_date-"
SECOND_DELAY = 1

# dates
first_description = datetime.date(year=2013, month=4, day=22)
today = datetime.date.today()
current_date = first_description

# list for storing articles
all_articles = []

def update_progress_bar(pbar: tqdm, current_date: datetime.datetime) -> None:
    """Update Progress bar"""
    pbar.update(1)
    estimated_time = round(((today - current_date).days * (SECOND_DELAY+0.3)) / 60)
    pbar.set_description(f"Scraping articles: Date:{current_date.strftime(DATE_FORMAT)}, Articles: {len(all_articles)}, Estimated time left: {round(estimated_time, 2)} min")

# init progressbar
total_days = (today - first_description).days
print(total_days)
progress_bar = tqdm(total=total_days)
update_progress_bar(progress_bar, current_date)

# loop over days
while current_date <= today:
    date_string = current_date.strftime("%Y%m%d")
    # format url to right form
    url_string = f"{ARCHIVE_URL}{date_string}.html"
    # request html and scrape it for the datapoints 
    response = requests.get(url_string).text
    soup = BeautifulSoup(response, 'html.parser')
    
    # save articles
    article_teasers = list(soup.findAll(class_="teasertext"))
    titles = soup.findAll(class_="headline")
    dates_and_times = list(soup.findAll(class_="dachzeile"))

    for title, date_and_time, article, in zip(titles, dates_and_times, article_teasers): 
        all_articles.append([current_date.strftime(DATE_FORMAT), article.text, title.text, date_and_time.text])


    # go to next day
    current_date = current_date + datetime.timedelta(days=1)

    # sleep
    time.sleep(SECOND_DELAY)
    update_progress_bar(progress_bar, current_date)


# format data
article_df = pd.DataFrame(all_articles, columns=["date", "article", "title", "time_text"])
article_df.to_excel("data/raw.xlsx", index=False)
