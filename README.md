# Event-Extraction
Event Extraction from Online News articles
Event Extraction

1.Each sentences in each news article is assumed as single events.
2.Tagging Location and date assosiated with single events and storing them in database as single entity.

3.reate 4 seperate folders for date,url,news_articles and news_id.

(3a)Date folder should  contains one csv file for storing date of publishing of the article
(3b)url folder should contain one csv file for storing source url of the news article
(3c)news_article folder for storing body of the news articles(this folder contains output of parsing_json.py)
(3d)news_id should contain one csv file for storing the unique id of each news articles

Note: All the files will store respective Location,ID,and url in the same order 

4.un parsing_json.py.
Note: specify path to each respective file
Output: Stores data in all the 4 folders

5.un event_extraction.py
This module identifies location and date and event type associated with each sentences in the news article and creates a final csv file containg event,evet_type,event_location, event_date,event_url and event_news_id.

6.ideltime temporal tagger and AllenNLP NER are used for identifying date and locations associated with each events.
