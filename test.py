import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
from scraper_api import ScraperAPIClient
import pygsheets
from google.oauth2 import service_account

clientAPI = ScraperAPIClient('e8a3b272e459a3e3721168939db31f8b')
client = pygsheets.authorize(client_secret='client_secret.json')
sheet = client.open_by_key('178NvxT9wFQ9Bx-2uwsxsuwRQ45hr-hfZqTBWjXycSSA')
wks = sheet.worksheet_by_title('Sheet1')


def word_scrape():
    url = 'https://www.wordreference.com/es/translation.asp?tranword=address'
    words = []
    # parts_speach = ['adj + prep', 'verbal expression', 'vtr + adv','vi + adv','phrasal verb, transitive, inseparable', 'phrasal verb, intransitive, separable', 'phrasal verb, intransitive', 'verb, auxiliary', 'verb copulative', 'verb impersonal', 'verb, intransitive', 'verb, intransitive phrasal',
    # 'verb, past simple', 'verb, past participle', 'verb, past simple and past participle', 'verb, present participle', 'verb, present tense'
    # 'verb pronominal', 'verb, transitive and reflexive verb', 'verb, transitive', 'verb, transitive phrasal, inseparable', 'verb, transitive phrasal sep'
    # 'verbal expression', 'verb', 'transitive verb', 'intransitive verb', 'vtr + prep', 'vi + prep', 'phrasal verb, transitive, separable', 'phrasal verb, intransitive, inseparable']

    counter = 0
    end = 'start'
    session = requests.Session()
    start = time.time()
    while url:
        # r = clientAPI.get(url)
        r = session.get(url)
        soup = BeautifulSoup(r.text ,"html.parser")
        links = soup.find('li', id='link').find_all('a')
        #if the url is the last then stop the while loop
        if(end=='end'):
            break
        elif(counter >= 10000):
            break
        #else proceed
        else:
            for link in links:
                #check if the url is not repeated and if its not, add it to list
                if(link.get('href') not in words):
                    words.append(link.get('href'))
                    counter += 1
                    print(counter)
                    dic = {
                    "Word":[]
                    # , "Meaning":[], "Example":[], 
                    # "Speach":[], "Type":[], "Transitive/Intransitive":[], 
                    # "Separable/Inseparable":[], "Inflections":[]
                    }
                    url = 'https://www.wordreference.com' + link.get('href')
                    done = 'no'

                    # r = clientAPI.get(url)
                    r = session.get(url)
                    soup = BeautifulSoup(r.text ,"html.parser")
                    main = soup.find('div', class_='hw-flex-container')
                    principal_trans = False
                    additional_trans = False
                    all_translation = soup.find_all('table', class_='WRD')
                    #if the end_word variable equals zymurgy(thats the last word) then add it to dic and break the loop
                    for translation in all_translation:
                            try:
                                if(principal_trans == False):
                                    if(translation.find('span', class_='ph').text == 'Principal Translations'):
                                        principal_trans = True
                                        ingles = translation.find_all('td', class_='FrWrd')
                                        for ingle in ingles:
                                            for word in ingle.findAll("strong"):
                                                    text = word.text
                                                    dic["Word"].append(text)
                                if(additional_trans == False):
                                    if(translation.find('span', class_='ph').text == 'Additional Translations'):
                                        additional_trans = True
                                        ingles = translation.find_all('td', class_='FrWrd')
                                        for ingle in ingles:
                                            for word in ingle.findAll("strong"):
                                                # if word not in dic["Word"]:
                                                    text = word.text
                                                    dic["Word"].append(text)
                            except:
                                print("An exception occurred")
                    print('DONE')
                    # try:
                    df = pd.DataFrame(dic)
                    i = wks.rows+1 
                    print(i)
                    print(df)
                    wks.set_dataframe(df, start=(i,1), extend=True, copy_head=False)
                    # except:
                    #     print("Good job")
    end = time.time()
    print("Time Taken: {:.6f}s".format(end-start))

word_scrape()
