import requests
import datetime
from bs4 import BeautifulSoup
import pandas as pd
import time
from tqdm import tqdm
    
DATE_FORMAT = "%d/%m/%Y"
ARCHIVE_URL = "https://www.tagesschau.de/archiv/sendungsarchiv100~_date-"
SECOND_DELAY = 1

# dates
first_description = datetime.date(year=2013, month=4, day=22)
today = datetime.date.today()
total_days = (today - first_description).days
current_date = first_description

# list for storing articles
all_articles = []

def update_time(current_date):
    """Update Progress bar"""
    global progress_bar
    progress_bar.update(1)
    estimated_time = ((today - current_date).days * (SECOND_DELAY+0.5)) / 360
    progress_bar.set_description(f"Scraping articles from the date {current_date.strftime(DATE_FORMAT)}, {len(all_articles)} Articles gathered so far, estimated time: {round(estimated_time, 2)} hours")

# init progressbar
progress_bar = tqdm(total=total_days)
update_time(current_date)

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
    # here the texts will be saved


    # request html and scrape it for the datapoints 
    response = requests.get(url_string).text
    soup = BeautifulSoup(response, 'html.parser')
    
    # save articles
    article_teasers = soup.findAll(class_="teasertext")
    if len(article_teasers) < 1:
        print(f"No Article on {current_date.strftime(DATE_FORMAT)}")

    for article in article_teasers:
        all_articles.append([current_date, article.text])

    # go to next day
    current_date = current_date + datetime.timedelta(days=1)

    # sleep to not overwhelme target host
    time.sleep(SECOND_DELAY)
    update_time(current_date)


# format data
article_df = pd.DataFrame(all_articles, columns=["date", "article"])
article_df.to_excel("tagesschau_articles.xlsx")