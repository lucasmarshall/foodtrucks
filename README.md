SF Food Trucks
==============
This simple application uses the [SODA 2.0 API](http://dev.socrata.com/consumers/getting-started) to query [sfgov.org's table of mobile food facility permit applications](https://data.sfgov.org/Permitting/Mobile-Food-Facility-Permit/rqzj-sfat) and show their locations on a Google map, along with details of what the food truck sells and the address of the food truck.

My Experience with the Technology Stack
---------------------------------------
This application was written as a coding challenge. If you aren't evaluating this coding challenge, feel free to skip to the [Demo](#demo) section below.

In the coding challenge instructions, it says to specify how familiar I am with the stack I chose. I describe a bit of the logic behind my choices in the [Technologies Used](#technologies-used) section below, but here's a concise description of my personal experience:

* It's been a few years since I've done any serious Python web app coding, so I'm a bit rusty.
* This is my first time using Flask.
    * _Years_ ago I used [Zope](http://www.zope.org), [CherryPy](http://www.cherrypy.org/), and [Django](https://www.djangoproject.com/) as my frameworks of choice for Python web apps.
* This is definitely not my first time using Redis - I've used it extensively with PHP code - but
  it is the first time using it in Python code.
* I'm pretty familiar with backbone.js due to its use at StumbleUpon, but I was not a frontend
  engineer there, so I'm sure I've missed some best practices.
* I'm very familiar with jQuery.
* I'm passingly familiar with the Google Maps API, have done similar things with earlier versions.
* This is my first time using a SODA API.
* This is my first time using Heroku as a cloud-based hosting solution.

Demo
----
A running instance of the application can be found at: <http://fathomless-plateau-4167.herokuapp.com/>

Technologies Used
-----------------
The backend is written in Python, using the [Flask](http://flask.pocoo.org) microframework , which I chose to use due to the fact that it was adequate for a simple app such as this, and the fact that I'd never used it before... it seemed interesting.

The frontend is JavaScript, using backbone.js for views and models, the [Google Maps API](https://developers.google.com/maps/) for the map controls and geocoding, and one instance of an [underscore.js](http://underscorejs.org) template , since I thought that including something like handlebars or mustache would be overkill for such a simple use case when backbone has a dependency on underscore.

I also wrote a generic SODA 2.0 Query API class that could be broken out and used in other projects that could use data sources that implement SODA 2.0 APIs. This class interface is conceptually similar to Django's ResultSet class. I followed that pattern due to the fact that most Python developers are at least cursorily familiar with it and that the SODA API's SoQL is very similar to SQL, which the ResultSet is meant to provide an abstraction to.

The SODA class does some very simple query-based caching of results. It's currently hard-coded to use a [Redis](http://redis.io)-based cache.

The app is immediately deployable to [Heroku](https://www.heroku.com/). I chose Heroku because it's adequate for this application, and I've never used it before and wanted to try it out. It shouldn't be difficult to deploy in another environment like EC2.

Possible Future Optimizations and Improvements
----------------------------------------------
* Minifying and combining the JS files used.
* Adding the functionality to give directions to the truck from the current location.
* Make it more generic to support other data sources for food truck locations in other cities.
* The caching strategy is very simple - it does a query to the SODA API at sfgov.org and caches the result in redis. This strategy depends on the fact that we always generate the same query to the API. If that changes, the stragegy would not be adequate.
* We currently have support in the JavaScript to send the viewport coordinates to the server to just get the trucks in the viewport, but it looks like sfgov.org's SODA API's `within_box()` query function is not working. It could do all that server side, but that would complicate the caching strategy needlessly for what is currently a very simple application.
* Make it less Heroku-dependent.

Other Projects
--------------
[easyconfig](https://github.com/lucasmarshall/easyconfig) - a easy-to-use YAML-based configuration system for PHP

About Me
--------
I'm (Robert) Lucas Marshall, a software engineer with quite a bit of experience.
You can find out more about me at:

* <http://www.linkedin.com/in/robertlmarshall>
* <http://about.me/lucasmarshall>