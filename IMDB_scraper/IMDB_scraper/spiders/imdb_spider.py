# to run 
# scrapy crawl imdb_spider -o movies.csv

import scrapy

class ImdbSpider(scrapy.Spider):
    name = 'imdb_spider'
    
    # Link for American Horror Story page
    start_urls = ['https://www.imdb.com/title/tt1844624/']


    def parse(self, response):
        """
        Input: response: an HTTP response, used for processing
        Assumes starting page is the main page of a movie/show
        calls parse_full_credits() for the page of the entire cast
        """
        
        # The cast page is the start_url + "fullcredits"
        cast_page = response.urljoin("fullcredits")

        yield scrapy.Request(cast_page, callback = self.parse_full_credits)


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


