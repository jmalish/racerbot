# racerbot

Chat bot made for the #hoggit.iracing IRC room on the freenode server.  
  Mainly made to learn a new language, but is ultimately just a goofy project.

racerbot is written in Python 2.7, running it with 3.0 and up will cause issues  

###Dependencies: (I used "pip install \<dependency\>")
  - PRAW: Reddit's API
  - requests: Easy to use HTTP library
  - BeautifulSoup4: Translates what we get from requests into an easy to "read" format
  - cleverbot: it talks!
  - mysql-connector-python: used for quote system (may need to use 'mysql-connector-python --allow-external mysql-connector-python')
  - PyHyphen: Used in fishify for breaking words down into syllables