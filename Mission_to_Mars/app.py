import pymongo
import scrape_nasa
from flask import Flask, render_template, redirect

client = pymongo.MongoClient('mongodb://localhost:27017') # creating mongodb connection
db = client.mars_db  # creating the required db
collection = db.mars  # creating a collection of scraped data to insert into the db

app = Flask(__name__)  # Create an instance of Flask

@app.route("/")  # Route to render index.html template using data from Mongo
def home():
    mars = collection.find_one() # Find one record of data from the mongo database
    return render_template("index.html", mars = mars) # Return template and data

@app.route("/scrape")  # Route that will trigger the scrape function
def scrape():    
    scrape_nasa.scrape() # Run the scrape function
    return redirect("/") # Redirect back to home page

if __name__ == "__main__":
    app.run(debug=True)
