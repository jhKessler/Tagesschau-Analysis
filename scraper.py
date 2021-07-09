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
ARCHIVE_URL = "https://www.tagesschau.de/archiv/sendungsarchiv100~_date-"
SECOND_DELAY = 1

# dates
first_description = datetime.date(year=2013, month=4, day=22)
today = datetime.date.today()
current_date = first_description

# list for storing articles
all_articles = []

def update_progress_bar(current_date):
    """Update Progress bar"""
    global progress_bar
    progress_bar.update(1)
    estimated_time = ((today - current_date).days * (SECOND_DELAY+0.3)) / 60
    progress_bar.set_description(f"Scraping articles: Date:{current_date.strftime(DATE_FORMAT)}, Articles: {len(all_articles)}, Estimated time left: {round(estimated_time, 2)} min")

# init progressbar
total_days = (today - first_description).days
progress_bar = tqdm(total=total_days)
update_progress_bar(current_date)

# loop over days
while current_date <= today:
    year, month, day = current_date.year, current_date.month, current_date.day
    # pad day from e.g. 1 to 01
    if day < 10:
        day = f"0{day}"
    if month < 10:
        month = f"0{month}"

    # format url to right form
    url_string = f"{ARCHIVE_URL}{year}{month}{day}.html"
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
    update_progress_bar(current_date)


# format data
article_df = pd.DataFrame(all_articles, columns=["date", "article", "title", "time_text"])
article_df.to_excel("data/tagesschau_articles.xlsx", index=False)
