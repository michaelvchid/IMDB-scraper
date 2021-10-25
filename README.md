In this tutorial, we will be exploring webscraping using the Python package `scrapy`. We will be scraping the movie database IMDb with the goal of finding movies and TV shows that share the same actors from any given show or movie.

## Introduction

For the purposes of this tutorial, we will be using the hit show "American Horror Story." Before we begin, we must setup the tools to run the `scrapy` spider that will "crawl" the web and get the data we need. To begin, we must open up the terminal, or for users who have installed Python using Anaconda, the Anaconda Prompt. 

To create a `scrapy` project, first `cd` to the directory you want the project to be located in, then type `scrapy startproject IMDB_scraper`. Of course, the last word is the title of this project and can be anything you desire. Finally, `cd IMDB_scraper` to get in the proper directory to begin scraping.

`scrapy` will already populate the directory with many files, most of which won't need to be touched. In the "spiders" directory, we create a file called "imdb_scraper.py", which will house all of our code. This file won't be executed in Jupyter, so we must use a text editor to edit the file.

## Creating a Spider

The first step in creating a spider is to import the package and setup our class that will do all the work. Note that our class can be called whatever we like, but it must inherit from `scrapy.Spider`. It must also have the class variables `name` and `start_urls` defined or else it won't function properly. 


```python
import scrapy

class ImdbSpider(scrapy.Spider):
    name = 'imdb_spider'
    
    # Link for American Horror Story page
    start_urls = ['https://www.imdb.com/title/tt1844624/']
```

Next, we will create three parse methods that will do what we want. The first one, `parse`, will be called directly when we run the spider (we will learn how to do that later). This first method will take use from the main page for our TV show to the list of actors/actresses in the entire series. Remember that this is a class method and therefore must be included in the class definition.


```python
def parse(self, response):
    """
    Input: response: an HTTP response, used for processing
    Assumes starting page is the main page of a movie/show
    calls parse_full_credits() for the page of the entire cast
    """
    
    # The cast page is the start_url + "fullcredits"
    cast_page = response.urljoin("fullcredits")

    yield scrapy.Request(cast_page, callback = self.parse_full_credits)
```

Our second parsing method, `parse_full_credits`, will be used to get the link to each actor's IMDb webpage and call our third parse method `parse_actor_page` for each actor. 


```python
def parse_full_credits(self, response):
    """
    Input: response: an HTTP response, used for processing
    Assumes starting page is the full cast of the show/movie
    Calls parse_actor_page() for every actor/actress
    """

    # Gets link ending for each actor/actress
    cast_links = [a.attrib["href"] for a in response.css("td.primary_photo a")]

    for link in cast_links:
        # Creates full-length url that takes user to the actor's main page
        full_cast_link = response.urljoin(link)
        yield scrapy.Request(full_cast_link, callback = self.parse_actor_page)
```

Finally, the last method `parse_actor_page` will retrieve the actor's/actress's name and all the films they've acted in. The method will end with a `yield` that will output the data into a .csv file when we run the spider.


```python
def parse_actor_page(self, response):
    """
    Input: response: an HTTP response, used for processing
    Assumes starting page is the main page of an actor/actress
    Yields the actor's name and movie/show in a dictionary,
    will be sent to a .csv file for storage.
    """

    # By inspecting the webpage, the actor's name is found
    # using the following css selector
    actor_name = response.css(".itemprop::text").get()

    # Selects only the section of films they acted in, not produced in, etc.
    acted_in = response.css("div.filmo-category-section")[0]

    # Retrieves all the movies they acted in
    movies_list = acted_in.css("div.filmo-row b a::text").getall()

    # Yield the {actor, movie} pair for each film
    for movie in movies_list:
        yield {"actor": actor_name, "movie_or_TV_name": movie}
```

That is all we need for our spider to work!

## Running the Spider

To run the spider we just created, first open the terminal or Anaconda Prompt and `cd` to the project. Then, all we need to do is type `scrapy crawl imdb_spider -o results.csv`. This will run the spider we just created (where "imdb_spider" is from the name variable in the class we created) and saves everything we `yield`ed in the third parse method to a file called "results.csv". And like that, we just scraped a website!

## Sorting the Data

The last step in this project is to see what data we got. We will be using `pandas` for a simple table.


```python
import numpy as np
import pandas as pd
```


```python
movies = pd.read_csv("results.csv")
movies.head(5)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>actor</th>
      <th>movie_or_TV_name</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Evan Peters</td>
      <td>Snow Ponies</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Evan Peters</td>
      <td>Monster: The Jeffrey Dahmer Story</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Evan Peters</td>
      <td>American Horror Story</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Evan Peters</td>
      <td>Mare of Easttown</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Evan Peters</td>
      <td>WandaVision</td>
    </tr>
  </tbody>
</table>
</div>



The sample above shows us what a bit of our table looks like. The actual table has over 46,000 rows, so there are a lot of actors who've starred in many films and shows!

We will now create a new column that counts how many times each show/movie appears in the dataFrame, thus counting how many actors/actresses from "American Horror Story" were in each film. We will also clean up the table to make it look nice.


```python
movies["movie count"] = movies.groupby("movie_or_TV_name")["movie_or_TV_name"].transform("count")

# Sort the table so that "movie count" is in descending order
movies = movies.sort_values(["movie count"], ascending=False)

# Next, we clean up the table and remove duplicate film appearances
# as we only care to see how each one ranks against each other
final_list = movies.drop_duplicates(subset="movie_or_TV_name")
final_list = final_list.drop(columns=["actor"])
final_list = final_list.reset_index(drop=True)
final_list = final_list.rename(columns={"movie_or_TV_name": "Movie / TV Show",
                                        "movie count":"Number of Shared Actors"})
```

And we finally get our nice table depicting the number of shared actors for each movie / TV show.


```python
final_list.head(10)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Movie / TV Show</th>
      <th>Number of Shared Actors</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>American Horror Story</td>
      <td>1180</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Criminal Minds</td>
      <td>179</td>
    </tr>
    <tr>
      <th>2</th>
      <td>NCIS</td>
      <td>159</td>
    </tr>
    <tr>
      <th>3</th>
      <td>The Mentalist</td>
      <td>156</td>
    </tr>
    <tr>
      <th>4</th>
      <td>CSI: Crime Scene Investigation</td>
      <td>147</td>
    </tr>
    <tr>
      <th>5</th>
      <td>ER</td>
      <td>124</td>
    </tr>
    <tr>
      <th>6</th>
      <td>Bones</td>
      <td>121</td>
    </tr>
    <tr>
      <th>7</th>
      <td>Grey's Anatomy</td>
      <td>115</td>
    </tr>
    <tr>
      <th>8</th>
      <td>NCIS: Los Angeles</td>
      <td>108</td>
    </tr>
    <tr>
      <th>9</th>
      <td>Shameless</td>
      <td>104</td>
    </tr>
  </tbody>
</table>
</div>



It shouldn't be a surprise that "American Horror Story" is at the top of the chart since that's what all our actors/actresses had in common! What we do see is that a good portion of them have acted in crime shows. 

With this spider, you can scrape any IMDb page and find what other films most actors were in for any movie or show of your choice!
