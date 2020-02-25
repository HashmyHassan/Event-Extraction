from allennlp.predictors.predictor import Predictor

import re
import glob, os

import nltk
nltk.download('wordnet')
nltk.download('punkt')
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer 
from nltk import sent_tokenize

import pandas as pd 
import os
from py_heideltime import py_heideltime
from datetime import date

import csv
from os import listdir
from os.path import isfile, join
from collections import defaultdict
import sys
import pickle

predictor = Predictor.from_path("./ner-model-2018.12.18 .tar.gz")
lemmatizer = WordNetLemmatizer()
DEBUG = True

def prepend(List, str): 
       
    # Using format() 
    str += '{0}'
    List = ((map(str.format, List))) 
    return List
  
def sentence_location_finder_allennlp(s):
    output = predictor.predict(s)
    res = list(output.values()) 
    res_tags = list(res[2])
    res_words = list(res[3])
    # print(res_tags)
    # print(res_words)
    final_loc =[]
    temp = ""
    for tag,word in zip(res_tags,res_words):
      if tag == '0':
        continue
      if tag == 'U-LOC':
        final_loc.append(word)
      elif tag == 'B-LOC':
        temp = word + " "
      elif tag == 'I-LOC':
        temp = temp + word + " "
      elif tag == 'L-LOC':
        temp = temp + word
        final_loc.append(temp)
    return final_loc

def searchLocInDict(location, csv_path ='./states_data.csv' ):
    if not location:
        return []
    if os.path.exists("town_to_dist") and os.path.exists("dist_to_state") and os.path.exists("states"):
        with open("town_to_dist",'rb') as fp:
            town_to_dist = pickle.load(fp)
        with open("dist_to_state",'rb') as fp:
            dist_to_state = pickle.load(fp)
        with open("states",'rb') as fp:
            states = pickle.load(fp)
    else:
        loc_info = pd.read_csv(csv_path)
        dist_to_state = {}
        town_to_dist = {}
        states = set()
        for p_loc in loc_info.iterrows():
            state = str(p_loc[1][0]).lower()
            district = str(p_loc[1][1]).lower()
            town = str(p_loc[1][2]).lower()
            town_to_dist[town] = district
            dist_to_state[district] = state
            states.add(state)
        with open("town_to_dist",'wb') as fp:
            pickle.dump(town_to_dist,fp)
        with open("dist_to_state",'wb') as fp:
            pickle.dump(dist_to_state,fp)
        with open("states",'wb') as fp:
            pickle.dump(states,fp)
    # if DEBUG:      
    #     print("Data:")
    #     print(states)
    #     print()
    temp_loc = []
    found_states = set()
    for loc1 in location:
        loc = loc1.lower()
        found = False
        for dist in dist_to_state.keys():
            if found:
                break
            # if loc in dist or dist in loc:
            if loc == dist:
                temp_loc.append((dist, dist_to_state[dist]))
                found_states.add(dist_to_state[dist])
                found = True
                
        for state in states:
            if found:
                break
            # if loc in state or state in loc:
            if loc == state:
                if not state in found_states:
                    temp_loc.append((state))
                found_states.add(state)
                found = True
                
        for town in town_to_dist.keys():
            if found:
                break
            # if loc in town or town in loc:
            if loc == town:
                dist = town_to_dist[town]
                temp_loc.append((dist, dist_to_state[dist], town))
                found_states.add(dist_to_state[dist])
                found = True
        
    return temp_loc

def get_closest_all(loc_avail, length):#location from nearest neighbour if location is not identified from the sentence
    location_index = [0 for i in range(length)]
    loc_notavail = []
    for i in range(length):
        if i not in loc_avail:
            loc_notavail.append(i)
        else:
            location_index[i] = i
    pos = 0
    for num in loc_notavail:
        while pos < len(loc_avail):
            if loc_avail[pos] > num:
                break
            pos += 1
        if pos == 0:
            location_index[num] = loc_avail[0]
        elif pos == len(loc_avail):
            location_index[num] = loc_avail[-1]
        else:
            before = loc_avail[pos - 1]
            after = loc_avail[pos]
            if (after - num) < (num - before):
                location_index[num] = after
            else:
                location_index[num] = before
    return location_index

def findlocation(sent_text, states_csv, default_val = [("null","null")]):#null as default location
    #takes array of sentences of an article to find location associated with each sentence
    loc_avail = []
    loc_dict = {}
    info = []
    #location_kashmir = pd.read_csv("J&K locations.csv")
    for i in range(len(sent_text)):
        loc = sentence_location_finder_allennlp(sent_text[i])
        loc = searchLocInDict(loc, states_csv)
        if loc:
            loc_avail.append(i)
            loc_dict[i] = loc
            if DEBUG:
                info.append((loc, loc_dict[i], sent_text[i]))
        # if DEBUG:
            #  print(i+1, "sentence processed for allennlp.")

    # if DEBUG:
        # print("information for location is:")
        # print(info)
    if not loc_avail:
        # if DEBUG:
            # print("no location found....")
        location_list = [default_val for i in range(len(sent_text))]
        return location_list

    location_ind = get_closest_all(loc_avail, len(sent_text))
    location_list = [loc_dict[i] for i in location_ind] 
    if DEBUG:
        # print("Nearest Neighbour algo completed successfully..")
        print(location_ind)
        print(location_list)
    return location_list

def findDates(sent_text, article_date):
    date_avail = []
    date_dict = {}
    for i in range(len(sent_text)):
        results = py_heideltime(sent_text[i], language='english', date_granularity="day", document_type='news', document_creation_time= article_date)
        sentence_date = results[0]
        if sentence_date:
            date_avail.append(i)
            date_dict[i] = sentence_date
        # if DEBUG:
            # print(i+1, "sentence processed for Hiedeltime")

    if not date_avail:
        date_list = [article_date for i in range(len(sent_text))]
        return date_list

    date_ind = get_closest_all(date_avail, len(sent_text))
    date_list = [date_dict[i] for i in date_ind] 
    # if DEBUG:
        # print("Nearest Neighbour algo completed successfully for Date")
        # print(date_ind)
    return date_list
  
def findSyn(event):
    # print("I am in /findsyn1")
    syn = set()
    for synset in wordnet.synsets(event):
        for lemma in synset.lemmas():
            syn.add(lemma.name()) 
    # print('Synonyms: ' + str(syn))
    # print("I am in findsyn")
    return syn

def findEventType(events, event_syn, sent):
    words = nltk.word_tokenize(sent)
    event_types = []
    for word in words:
        token = lemmatizer.lemmatize(word)
        for i in range(len(event_syn)):
            if token in event_syn[i] or word in event_syn[i]:
                event_types.append(events[i])
    return event_types

#finding out the events
def findEventCategory(senttext1):

    events = ["kill","strike","murder","attack","protest","terror","suicide","rape","kidnap","crime","fight","curfew","molest","stone pelting","shoot","Violence","explosion"]#event classes
    event_syn = []
    for event in events:
        syn = findSyn(event)
        print("syn is",syn)
        event_syn.append(syn)
    print(event_syn)
    eventtype_list = []
    for sent in senttext1:
        event_types = findEventType(events, event_syn, sent)
        eventtype_list.append(event_types)
    # if DEBUG:
        # print("Event Type ran succesfully")
        # print(eventtype_list)
    
    return eventtype_list

def writeToCsv(data, article_date, file_to_write, states_csv,url_news_csv,newsid_csv):
    senttext = nltk.sent_tokenize(data)
    try:
        location_list = findlocation(senttext, states_csv)
        date_list = findDates(senttext, article_date)
        eventtype_list = findEventCategory(senttext)
        f = open(file_to_write, "a")
        writer = csv.writer(f)
        i = 0
        for i in range(len(senttext)):
            print(senttext[i])
            print(location_list[i])
            print(date_list[i])
            print(eventtype_list[i])
            print(url_news_csv)
            print(newsid_csv)
            for location in location_list[i]:
                for eventtype in eventtype_list[i]:
                    data1 = senttext[i].replace("\n", " ")
                    data2 = data1.replace("\t", "")
                    senttext[i] = data2
                    writer.writerow(senttext[i], date_list[i][0][0],location[0],location[1],eventtype,url_news_csv,newsid_csv)
        # if DEBUG:
            # print("csv updated once!!")
            # print()
        f.close()
    except (Exception, RuntimeError):
        print("catched exception")
        return

def driverCode(data_folder, date_file, output_file, states_csv,url_csv,news_csv):
    count = 0
    # if DEBUG:
        # print("1. inside driver code....")
    input_files = []
    for root, _, files in os.walk(data_folder):
        for f in files:
            if f.endswith('.txt'):
                input_files.append(os.path.join(f))
                

    input_files.sort(key=lambda x: int(x.split('_')[0]))
    print(input_files)
    
    str = "./Output/" #Folder to store all contents of the news articles in .txt format
    input_files = list(prepend(input_files, str))
    date_list = []
    url_list = []
    newsid_list = []
    f = open(date_file, 'r')
    data = csv.reader(f)
    for row in data:
        date_list.append(row[0])

    f = open(url_csv, 'r')
    data_url = csv.reader(f)
    for row in data_url:
        url_list.append(row[0])

    f = open(news_csv, 'r')
    data_csv = csv.reader(f)
    for row in data_csv:
        newsid_list.append(row[0])
    
    check = False
    i = 1
    for i in range(len(input_files)):
        # if input_files[i] == "2_Held_For_Peddling_Drugs_In_City_2019-07-29.txt":
        #     print("mil gaya")
        #     check = True
        # if not check:
        #     print(input_files[i])
        #     continue 
        
        f = open(input_files[i],'r')
        data = f.read()
        if DEBUG:
            print("----------------------processing input file--", os.path.basename(input_files[i]))
            print(data)
            print(date_list[i])
            print(output_file)        
            print(states_csv)
            print(url_list[i])
            print(newsid_list[i])
        writeToCsv(data, date_list[i], output_file, states_csv,url_list[i],newsid_list[i])
        count += 1
        
        

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

if __name__ == "__main__":
    print("inside main..")
    data_folder = sys.argv[1]
    date_file = sys.argv[2]
    output_file = sys.argv[3]
    states_csv = sys.argv[4]
    url_csv = sys.argv[5]
    news_id_csv = sys.argv[6]
    driverCode(data_folder, date_file, output_file, states_csv,url_csv,news_id_csv)
    #Cypher Query: MATCH (n:Event) return n.Event,n.Location,n.Date,n.URL,n.News_ID
    #Run the code : python3 data_preprocess_update.py ./Output ./date/date.csv ./Write_to_csv/Write_to_csv.csv ./states_data.csv ./URL/url.csv ./News_ID/news_id.csv 
