#!/usr/bin/env python
# coding: utf-8

# In[1]:


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService 
#from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import re
import requests


# In[2]:


# Scrapping the data from IMDB website
service = Service(executable_path='chromedriver.exe')
driver = webdriver.Chrome(service=service)
driver.get("https://www.imdb.com/chart/top/?ref_=nv_mv_250")

wait = WebDriverWait(driver, 10)

try:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    movies = soup.find_all('li', class_ = 'ipc-metadata-list-summary-item sc-4929eaf6-0 DLYcv cli-parent')

finally:
    driver.quit()


# In[3]:


#function to get title, href and movieid
def get_id_href(soup):
    movie=soup.find('a', attrs={'class':'ipc-title-link-wrapper'})
    title=''
    href=''
    movieid=''
    title=str(movie.text[3:].strip())
    href=movie['href']
    movieid = href.split('/')[2]
    return movieid,href,str(title)


# In[4]:


#function to get year, duration and censorship
def get_year_time(soup):
    ytr = soup.find_all('span', attrs={'class':'sc-ab348ad5-8 cSWcJI cli-title-metadata-item'})
    print('in function ytr',ytr)
    x = []
    for i in ytr:
        x.append(i.text)
    print('x:',x)
    
    try: 
        year = int(x[0])
    except:
        year = ''
    try:
        match = re.match(r'(?:(\d+)h)?\s*(?:(\d+)m)?', x[1])
        # Extract hours and minutes, defaulting to 0 if not found
        hours = int(match.group(1)) if match.group(1) else 0
        minutes = int(match.group(2)) if match.group(2) else 0
        # Convert the total time to minutes
        total_minutes = hours * 60 + minutes
        duration = total_minutes
    except:
        duration = ''
    try: 
        censorship = str(x[2])
    except:
        censorship = ''
    return year, duration, censorship


# In[5]:


def get_ratings(soup):
    imdb_rating = float(soup.find('span', attrs={'class':'ipc-rating-star--rating'}).text)
    rating_count = soup.find('span', attrs={'class':'ipc-rating-star--voteCount'}).text.strip()
    match = re.match(r'\(?([\d\.]+)([MK]?)\)?', rating_count)
    number = float(match.group(1))  
    suffix = match.group(2)  
    if suffix == 'M':
        number = number  
    elif suffix == 'K':
        number = round(number / 1000,2)  
    else:
        number =  round(number / 1_000_000,2)  
    rating_count = float(number)
    return imdb_rating, rating_count


# In[6]:


#function to get cast, director, tags
def get_movie_det(href, movie_data):
    url = "https://www.imdb.com"+href
    print(url)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print("Successfully fetched the webpage!")
        s = BeautifulSoup(response.content, "html.parser")
        time.sleep(5)
        try:
            tags = s.find_all('span',class_ = 'ipc-chip__text')
            movie_tags = [tag.text for tag in tags]
        except:
            movie_tags = []
        movie_data.get("Tags").append(movie_tags)

        try:
            summary = s.find('span', attrs={'data-testid':'plot-xs_to_m'}).text
        except:
            summary = ''
        movie_data.get("Summary").append(summary)
        
        try:
            crew = s.find('ul', class_ = 'ipc-metadata-list ipc-metadata-list--dividers-all title-pc-list ipc-metadata-list--baseAlt')
            crew_list = s.find_all('a', class_ ='ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link')
        except:
            cre_list = []
            
        if len(crew_list)!=0:
            actors=[]
            directors=[]
            for i in crew_list:
                if 'dr' in i['href']:
                    # print(i.text)
                    directors.append(i.text)
                elif 'ov_st' in i['href']:
                    # print(i.text)
                    actors.append(i.text)
        movie_data.get('Director').append(directors)
        movie_data.get('Actors').append(actors)
                
    else:
        print(f"Failed to retrieve webpage. Status code: {response.status_code}")


# In[7]:


movie_data = {'Movie_id':[],'Title':[],'Link':[],'Year':[],'Runtime':[],'Censorship':[],'Ratings':[],'Rating_count':[]}
for i in range(len(movies)):
    id_href=get_id_href(movies[i])
    ytr=get_year_time(movies[i])
    rt = get_ratings(movies[i])
    movie_data.get('Movie_id').append(id_href[0])
    movie_data.get('Link').append(id_href[1])
    movie_data.get('Title').append(id_href[2])
    movie_data.get('Year').append(ytr[0])
    movie_data.get('Runtime').append(ytr[1])
    movie_data.get('Censorship').append(ytr[2])
    movie_data.get('Ratings').append(rt[0])
    movie_data.get('Rating_count').append(rt[1])
    #get_movie_det(id_href[1],movie_data)
    
    
    


# In[8]:


print ("movie_id:", len(movie_data['Movie_id']))
print ("Title", len(movie_data['Title']))
print ("LINK", len(movie_data['Link']))
print ("Year", len(movie_data['Year']))
print ("Runtime", len(movie_data['Runtime']))
print ("Censorship", len(movie_data['Censorship']))
print ("Ratings", len(movie_data['Ratings']))
print ("Rating_count", len(movie_data['Rating_count']))



# In[9]:


import pandas as pd

movie_df=pd.DataFrame(movie_data)
movie_df.info()


# In[10]:


movie_df.head(10)


# In[13]:


movie_df.to_excel('movies_meatadata.xlsx', index = False)


# In[16]:


#Scraping movie reviews 
import time

reviews_data1 = {'Movie_id':[],'review':[]}
for link in movie_data['Link'][0:50]:
    movie_id=link.split('/')[2]
    url = "https://www.imdb.com"+link[:link.find('?')]+'reviews/?ref_=tt_urv_sm'  # Replace with the target URL
    print(url)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    
    
    # Check if the request was successful
    if response.status_code == 200:
        print("Successfully fetched the webpage!")
        s = BeautifulSoup(response.content, "html.parser")
        time.sleep(5) #change time if necessary
        reviews = s.find_all('div', class_='lister-item-content')
    
        for review in reviews:
            reviews_data1.get('Movie_id').append(movie_id)
            x=review.find('div', class_='content').text
            
            reviews_data1.get('review').append(x[:x.find('\n',1)].lstrip('\n'))
            print("\n")
    else:
        print(f"Failed to retrieve webpage. Status code: {response.status_code}")
    


# In[15]:


#Review scrapping code is modified by chatgpt for parllel processing to make the extraction faster.

import time
import requests
from bs4 import BeautifulSoup
import concurrent.futures


reviews_data = {'Movie_id': [], 'review': []}
# Define a function to scrape reviews for a single movie
def scrape_reviews(link):
    movie_id = link.split('/')[2]
    url = "https://www.imdb.com" + link[:link.find('?')] + 'reviews/?ref_=tt_urv_sm'
    print(f"Fetching URL: {url}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print(f"Successfully fetched the webpage for movie {movie_id}")
        soup = BeautifulSoup(response.content, "html.parser")
        reviews = soup.find_all('article', class_='sc-2b6c2ed6-1 gHSlW user-review-item')

        # Extract reviews and append to the data
        for review in reviews:
            reviews_data['Movie_id'].append(movie_id)
            x = review.find('div', class_='ipc-html-content-inner-div').text
            reviews_data['review'].append(x[:x.find('\n', 1)].lstrip('\n'))

    else:
        print(f"Failed to retrieve webpage for movie {movie_id}. Status code: {response.status_code}")

    # Introduce a slight delay to avoid overwhelming the server
    time.sleep(2)
    return reviews_data

# Use ThreadPoolExecutor for parallel processing
def parallel_scrape(movie_links):
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # Submit the scrape_reviews function for each movie link
        executor.map(scrape_reviews, movie_links)





# In[16]:


import pandas as pd
# List of movie links from your movie_data DataFrame
movie_meta = pd.read_excel("movies_meatadata.xlsx")
movie_links = movie_meta['Link']


# Run the scraping in parallel
parallel_scrape(movie_links)

# Check results
print(f"Scraped {len(reviews_data['review'])} reviews.")


# In[14]:


import time
import requests
from bs4 import BeautifulSoup
import concurrent.futures
import pandas as pd

# Define a function to scrape reviews for a single movie
def scrape_reviews(link):
    reviews_data = {'Movie_id': [], 'review': []}
    movie_id = link.split('/')[2]
    url = "https://www.imdb.com" + link[:link.find('?')] + 'reviews/?ref_=tt_urv_sm'
    print(f"Fetching URL: {url}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print(f"Successfully fetched the webpage for movie {movie_id}")
        soup = BeautifulSoup(response.content, "html.parser")
        reviews = soup.find_all('div', class_='lister-item-content')

        # Extract reviews and append to the data
        for review in reviews:
            reviews_data['Movie_id'].append(movie_id)
            x = review.find('div', class_='content').text
            reviews_data['review'].append(x[:x.find('\n', 1)].lstrip('\n'))

    else:
        print(f"Failed to retrieve webpage for movie {movie_id}. Status code: {response.status_code}")

    # Introduce a slight delay to avoid overwhelming the server
    time.sleep(2)
    return reviews_data

# Use ThreadPoolExecutor for parallel processing
def parallel_scrape(movie_links):
    reviews_accumulated = {'Movie_id': [], 'review': []}

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # Submit the scrape_reviews function for each movie link and collect the results
        results = executor.map(scrape_reviews, movie_links)

        # Aggregate results from each thread
        for result in results:
            reviews_accumulated['Movie_id'].extend(result['Movie_id'])
            reviews_accumulated['review'].extend(result['review'])

    return reviews_accumulated

# List of movie links from your movie_data DataFrame
movie_meta = pd.read_excel("movies_meatadata.xlsx")
movie_links = movie_meta['Link']

# Run the scraping in parallel and collect reviews
reviews_data = parallel_scrape(movie_links)

# Check results
print(f"Scraped {len(reviews_data['review'])} reviews.")


# In[15]:


reviews_df=pd.DataFrame(reviews_data)
reviews_df.head()


# In[13]:





# In[46]:


reviews_df.to_excel('movie_reviews.xlsx', index = False)


# In[43]:


url = "https://www.imdb.com/title/tt0025316/reviews/?ref_=tt_urv_sm"
print(f"Fetching URL: {url}")
headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

response = requests.get(url, headers=headers)
if response.status_code == 200:
    print(f"Successfully fetched the webpage for movie")
    soup = BeautifulSoup(response.content, "html.parser")
    reviews = soup.find_all('div', class_='lister-item-content')

    # Extract reviews and append to the data
    for review in reviews:
        x = review.find('div', class_='content').text
        reviews_data['review'].append(x[:x.find('\n', 1)].lstrip('\n'))
else:
    print(f"Failed to retrieve webpage for movie {movie_id}. Status code: {response.status_code}")

    
    


# In[49]:


soup.find('article', class_='sc-2b6c2ed6-1 gHSlW user-review-item').text

