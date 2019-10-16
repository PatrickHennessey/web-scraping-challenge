import time
import pymongo
import requests
import pandas as pd
from splinter import Browser
from bs4 import BeautifulSoup as bs

client = pymongo.MongoClient('mongodb://localhost:27017') # creating mongodb connection
db = client.mars_db  # creating the required db
collection = db.mars  # creating a collection of scraped data to insert into the db

executable_path = {"executable_path": "Resources/chromedriver.exe"}

def scrape():
    collection.drop() # get rid of any previous scraped data
    browser = Browser("chrome", **executable_path, headless=False)

    ### NASA Mars News - Title and Text
    news_url = "https://mars.nasa.gov/news" # url to scrape | I will not be commenting every line of code like this, but I will comment on unique code as it comes up.
    browser.visit(news_url) # browser connection & target url
    news_html = browser.html # returned browser object variable
    news_soup = bs(news_html, "lxml") # bs setup 
    news_title = news_soup.find('div', class_='content_title').text # bs function to find article title
    time.sleep(5) # using to to help prevent 
    news_text = news_soup.find('div', class_='article_teaser_body').text # bs function to find article content

    ### JPL Mars Space Images - Featured Image
    jpl_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(jpl_url)
    jpl_html = browser.html
    jpl_soup = bs(jpl_html, "lxml")
    jpl_img_route = jpl_soup.find(
        'a', class_='fancybox').get('data-fancybox-href')
    base_route = jpl_url.rstrip('spaceimages/?search=&category=Mars') #bs function to get last part of image url
    jpl_featured_img = base_route + jpl_img_route # concatinating the complete url
    jpl_featured_title = jpl_soup.find(
        'h1', class_='media_feature_title').text.strip()

    ### Mars Weather - Tweet
    mars_weather_url = "https://twitter.com/marswxreport?lang=en"
    browser.visit(mars_weather_url)
    mars_weather_html = browser.html
    mars_weather_soup = bs(mars_weather_html, "lxml")
    mars_weather_tweet = mars_weather_soup.find(
        'p', class_="tweet-text").text.strip() # grabbing tweet text, stripping away pythong code
    
    ### Mars Facts - Pandas Data Table
    mars_facts_url = "https://space-facts.com/mars/"
    browser.visit(mars_facts_url)
    mars_facts_html = browser.html
    mars_facts_soup = bs(mars_facts_html, "lxml")
    mars_facts_table = pd.read_html(mars_facts_url)[0] # using pandas to create a table from the first indexed table in bs object
    mars_facts_table_html = mars_facts_table.to_html(
        header=False, index=False).replace('\n', ' ') # using pandas to create table html, and replacing the line continuations from python (\n) with a space (" ")

    ### Mars Hemispheres - Full Res Image and Title/Name
    mars_hemi_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(mars_hemi_url)
    mars_hemi_html = browser.html
    mars_hemi_soup = bs(mars_hemi_html, "lxml")
    mars_hemi_img_urls = [] # empty list
    mars_products = mars_hemi_soup.find("div", class_="result-list")
    mars_hemispheres = mars_products.find_all("div", class_="item") # grabbing all cotent related to full sized image links

    for hemisphere in mars_hemispheres: # for loop to run through the 4 chunks of content collected from above line
        img_title = hemisphere.find("h3").text
        img_title = img_title.replace("Enhanced", "")
        img_route = hemisphere.find("a")["href"]
        img_link = "https://astrogeology.usgs.gov/" + img_route
        browser.visit(img_link) # going to the above link to grab info/image
        img_html = browser.html
        img_soup = bs(img_html, "lxml")
        img_downloads = img_soup.find("div", class_="downloads")
        img_url = img_downloads.find("a")["href"]
        img_dictionary = {"text": img_title, "url": img_url} # creating a dictionary of info to insert into the above empty list
        mars_hemi_img_urls.append(img_dictionary)

    # Close the browser after scraping
    browser.quit()

    # Store data in a dictionary
    mars_scraped_data = {
        "news_title": news_title,
        "news_text": news_text,
        "featured_img": jpl_featured_img,
        "featured_img_title": jpl_featured_title,
        "mars_tweet": mars_weather_tweet,
        "mars_table": mars_facts_table_html,
        "mars_hemi_imgs_title" : img_title,
        "mars_hemi_imgs": img_link,
        "mars_hemi":  mars_hemi_img_urls

    }

    # Inserting scapped data into collection, and then into the db
    collection.insert(mars_scraped_data)
