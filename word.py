import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
from scraper_api import ScraperAPIClient
import pygsheets
from google.oauth2 import service_account

clientAPI = ScraperAPIClient('e8a3b272e459a3e3721168939db31f8b')
client = pygsheets.authorize(client_secret='client_secret.json')
sheet = client.open_by_key('1ZZ0iGjiFC2jqFMHBzlfGGxGJzIBXiW6p4mcSI1qHbF4')
wks = sheet.worksheet_by_title('Sheet1')


def word_scrape():
    url = 'https://www.wordreference.com/es/translation.asp?tranword=acknowledgements'
    words = []
    parts_speach = ['adj + prep', 'verbal expression', 'vtr + adv','vi + adv','phrasal verb, transitive, inseparable', 'phrasal verb, intransitive, separable', 'phrasal verb, intransitive', 'verb, auxiliary', 'verb copulative', 'verb impersonal', 'verb, intransitive', 'verb, intransitive phrasal',
    'verb, past simple', 'verb, past participle', 'verb, past simple and past participle', 'verb, present participle', 'verb, present tense'
    'verb pronominal', 'verb, transitive and reflexive verb', 'verb, transitive', 'verb, transitive phrasal, inseparable', 'verb, transitive phrasal sep'
    'verbal expression', 'verb', 'transitive verb', 'intransitive verb', 'vtr + prep', 'vi + prep', 'phrasal verb, transitive, separable', 'phrasal verb, intransitive, inseparable']

    counter = 0
    end = 'start'
    # session = requests.Session()
    start = time.time()
    try:
        while url:
            r = clientAPI.get(url)
            # r = session.get(url)
            soup = BeautifulSoup(r.text ,"html.parser")
            links = soup.find('li', id='link').find_all('a')
            #if the url is the last then stop the while loop
            if(end=='end'):
                break
            elif(counter >= 100000):
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
                        "Word":[], "Meaning":[], "Example":[], 
                        "Speach":[], "Type":[], "Transitive/Intransitive":[], 
                        "Separable/Inseparable":[], "Inflections":[]
                        }
                        url = 'https://www.wordreference.com' + link.get('href')
                        done = 'no'

                        r = clientAPI.get(url)
                        # r = session.get(url)
                        soup = BeautifulSoup(r.text ,"html.parser")
                        main = soup.find('div', class_='hw-flex-container')
                        principal_trans = False
                        additional_trans = False
                        one_inflection = False
                        two_inflections = False
                        all_translation = soup.find_all('table', class_='WRD')
                        end_word = soup.find('h3', class_='headerWord').text
                        #if the end_word variable equals zymurgy(thats the last word) then add it to dic and break the loop
                        if(end_word == 'zymurgy'):
                            end = 'end'
                            for translation in all_translation:
                                try:
                                    if(principal_trans == False):
                                        if(translation.find('span', class_='ph').text == 'Principal Translations'):
                                            principal_trans = True
                                            ingles = translation.find_all('td', class_='FrWrd')
                                            for ingle in ingles:
                                                for word in ingle.findAll("strong"):
                                                        text = word.text
                                                        meaning = word.find_next('td').text
                                                        if(word.find_next('em').get('class')[0] == 'POS2'):
                                                            word_type = word.find_next('em').text
                                                        else:
                                                            word_type = word.find_next('em').find_next('span').contents[0].text 
                                                        # print(text)
                                                        # print('word_type '+word_type)

                                                        some = word.parent.parent.find_next('tr')
                                                        some2 = some.find_next('tr')
                                                        some3 = some2.find_next('tr')
                                                        
                                                        new = ""
                                                        new2 = ""
                                                        new3 = ""
                                                        if(main is not None):
                                                            if(done == 'no'):
                                                                div_infs = main.find('div', class_='inflectionsSection')
                                                                # print(len(div_infs.find_all('div')))
                                                                if(len(div_infs.find_all('div'))<2):
                                                                    try:    
                                                                        for i in div_infs.find_all('dl'):
                                                                            if(i.find('dt', class_='ListInfl') is None):
                                                                                first = text
                                                                                if(i.find('dd') is not None):
                                                                                    second = i.find_all('dd')
                                                                                    if(len(second)<2):
                                                                                        sec1 = second[0].contents[0].contents[0]
                                                                                        new = new + first + ': ' + sec1 + '; \n'
                                                                                    elif(len(second)>1):
                                                                                        sec = ''
                                                                                        for c in range(len(second)):
                                                                                            sec = sec + first+': '+ second[c].contents[0].contents[0] + '\n'
                                                                                        new = sec
                                                                                else:
                                                                                    new = new + first + '('+ i.find_all('span', class_='tooltip POS2')[0].contents[0] +'): '+ i.find_all('span', class_='tooltip POS2')[1].contents[0] + i.contents[-2].replace(':', '') +'; \n'
                                                                            else:    
                                                                                first =  i.find('dt', class_='ListInfl').text
                                                                                second = i.find('span', class_='POS2').contents[0].contents[0]
                                                                                # print('first '+first)
                                                                                # print('sec '+second)
                                                                                new = new + first + ': ' + second + '; \n' 
                                                                            one_inflection = True 
                                                                    except:
                                                                        print("An exception occurred 2")
                                                                else:
                                                                    for divs in div_infs.find_all('div'):
                                                                        try:
                                                                            for i in divs.find_all('dl'):
                                                                                if(i.find('dt', class_='ListInfl') is None):
                                                                                    infs = ""
                                                                                    for span in i.find_all('span', class_='tooltip POS2'):
                                                                                        infs = infs + span.contents[0] + " "
                                                                                    li = infs.split(' ')
                                                                                    new2 = new2 +'('+li[0]+'): '+ li[1]+i.contents[-2]+'; \n'
                                                                                    two_inflections = True                   
                                                                                else:
                                                                                    first =  i.find('dt', class_='ListInfl').text
                                                                                    second = i.find('span', class_='POS2').contents[0].contents[0]
                                                                                    new3 = new3 + first + ': ' + second + '; \n'                                                                        
                                                                        except:
                                                                            print("An exception occurred 2")
                                                                if(one_inflection==True):
                                                                    dic["Word"].append(end_word)
                                                                    dic["Meaning"].append("null")
                                                                    dic["Speach"].append("null")
                                                                    dic["Example"].append("null")
                                                                    dic["Type"].append("null")
                                                                    dic["Transitive/Intransitive"].append("null")
                                                                    dic["Separable/Inseparable"].append("null")
                                                                    dic["Inflections"].append(new)
                                                                    one_inflection = False
                                                                elif(two_inflections == True):
                                                                    dic["Word"].append(end_word)
                                                                    dic["Meaning"].append("null")
                                                                    dic["Speach"].append("null")
                                                                    dic["Example"].append("null")
                                                                    dic["Inflections"].append(new2)
                                                                    dic["Type"].append("null")
                                                                    dic["Transitive/Intransitive"].append("null")
                                                                    dic["Separable/Inseparable"].append("null")
                                                                
                                                                    dic["Word"].append(end_word)
                                                                    dic["Meaning"].append("null")
                                                                    dic["Speach"].append("null")
                                                                    dic["Example"].append("null")
                                                                    dic["Type"].append("null")
                                                                    dic["Transitive/Intransitive"].append("null")
                                                                    dic["Separable/Inseparable"].append("null")
                                                                    dic["Inflections"].append(new3)
                                                                    two_inflections = False
                                                                if(new==""):
                                                                    new = "null"
                                                                    dic["Inflections"].append(new)
                                                                else:
                                                                    dic["Inflections"].append("null")
                                                                done = 'yes'
                                                            else:
                                                                dic["Inflections"].append('null')
                                                        else:
                                                            dic["Inflections"].append('null')


                                                        ls = word_type.split(" ")
                                                        length = len(ls)
                                                        # print(length)
                                                        
                                                        if(word_type not in parts_speach):
                                                            dic["Word"].append(text.replace("⇒", ""))
                                                            dic["Meaning"].append(meaning)
                                                            dic["Speach"].append(word_type)
                                                            dic["Type"].append("null")
                                                            dic["Transitive/Intransitive"].append("null")
                                                            dic["Separable/Inseparable"].append("null")
                                                        else:
                                                            if(length==2):
                                                                if(word_type=="verbal expression"):
                                                                    dic["Transitive/Intransitive"].append("null")
                                                                    dic["Word"].append(text.replace("⇒", ""))
                                                                    dic["Meaning"].append(meaning)
                                                                    dic["Separable/Inseparable"].append("null")
                                                                    dic["Speach"].append("verb")
                                                                    dic["Type"].append("verbal expression")
                                                                else:
                                                                    dic["Transitive/Intransitive"].append(ls[0])
                                                                    dic["Word"].append(text.replace("⇒", ""))
                                                                    dic["Meaning"].append(meaning)
                                                                    dic["Separable/Inseparable"].append("null")
                                                                    dic["Speach"].append(ls[1])
                                                                    dic["Type"].append("normal")
                                                            elif(length == 1):
                                                                dic["Transitive/Intransitive"].append(ls[0])
                                                                dic["Word"].append(text.replace("⇒", ""))
                                                                dic["Meaning"].append(meaning)
                                                                dic["Separable/Inseparable"].append("null")
                                                                dic["Speach"].append(word_type)
                                                                dic["Type"].append("normal")                                            
                                                            elif(length==3):
                                                                if(word_type=="vtr + prep"):
                                                                    dic["Word"].append(text.replace("⇒", ""))
                                                                    dic["Meaning"].append(meaning)
                                                                    dic["Separable/Inseparable"].append("null")
                                                                    dic["Speach"].append("verb")
                                                                    dic["Type"].append("prepositional")    
                                                                    dic["Transitive/Intransitive"].append('transistive')
                                                                elif(word_type=="vi + prep"):
                                                                    dic["Word"].append(text.replace("⇒", ""))
                                                                    dic["Meaning"].append(meaning)
                                                                    dic["Separable/Inseparable"].append("null")
                                                                    dic["Speach"].append("verb")
                                                                    dic["Type"].append("prepositional")    
                                                                    dic["Transitive/Intransitive"].append('intransitive')
                                                                elif(word_type=="vtr + adv"):
                                                                    dic["Word"].append(text.replace("⇒", ""))
                                                                    dic["Meaning"].append(meaning)
                                                                    dic["Separable/Inseparable"].append("null")
                                                                    dic["Speach"].append("verb")
                                                                    dic["Type"].append("phrasal")    
                                                                    dic["Transitive/Intransitive"].append('transistive')
                                                                elif(word_type=="vi + adv"):
                                                                    dic["Word"].append(text.replace("⇒", ""))
                                                                    dic["Meaning"].append(meaning)
                                                                    dic["Separable/Inseparable"].append("null")
                                                                    dic["Speach"].append("verb")
                                                                    dic["Type"].append("phrasal")    
                                                                    dic["Transitive/Intransitive"].append('intransitive')
                                                                elif(word_type=="adj + prep"):
                                                                    dic["Word"].append(text.replace("⇒", ""))
                                                                    dic["Meaning"].append(meaning)
                                                                    dic["Separable/Inseparable"].append("null")
                                                                    dic["Speach"].append("adjective plus preposition")
                                                                    dic["Type"].append("null")    
                                                                    dic["Transitive/Intransitive"].append('null')
                                                                else:
                                                                    dic["Word"].append(text.replace("⇒", ""))
                                                                    dic["Meaning"].append(meaning)
                                                                    dic["Separable/Inseparable"].append("null")
                                                                    dic["Speach"].append(ls[1].replace(',', ''))
                                                                    dic["Type"].append(ls[0])    
                                                                    dic["Transitive/Intransitive"].append(ls[2])
                                                            elif(length == 4):
                                                                dic["Word"].append(text.replace("⇒", ""))
                                                                dic["Meaning"].append(meaning)
                                                                dic["Separable/Inseparable"].append(ls[3])
                                                                dic["Speach"].append(ls[1].replace(',', ''))
                                                                dic["Type"].append(ls[0])    
                                                                dic["Transitive/Intransitive"].append(ls[2].replace(',', ''))
                                                            else:
                                                                dic["Transitive/Intransitive"].append("null")
                                                                dic["Word"].append(text.replace("⇒", ""))
                                                                dic["Meaning"].append(meaning)
                                                                dic["Separable/Inseparable"].append("null")
                                                                dic["Speach"].append(word_type)
                                                                dic["Type"].append("null")
                                                        
                                                        if(some.find('td', class_='FrEx') is not None):
                                                            dic["Example"].append(some.text)
                                                        else:
                                                            if(some.find_next('tr').find('td', class_='FrEx') is not None):
                                                                dic["Example"].append(some2.text)
                                                            elif(some2.find_next('tr').find('td', class_='FrEx') is not None):
                                                                dic["Example"].append(some3.text)
                                                            else:
                                                                dic["Example"].append('null')

                                    if(additional_trans == False):
                                        if(translation.find('span', class_='ph') is not None):
                                            if(translation.find('span', class_='ph').text == 'Additional Translations'):
                                                additional_trans = True
                                                ingles = translation.find_all('td', class_='FrWrd')
                                                for ingle in ingles:
                                                    for word in ingle.findAll("strong"):
                                                        # if word not in dic["Word"]:
                                                            text = word.text
                                                            meaning = word.find_next('td').text
                                                            if(word.find_next('em').get('class')[0] == 'POS2'):
                                                                word_type = word.find_next('em').text
                                                            else:
                                                                word_type = word.find_next('em').find_next('span').contents[0].text 

                                                            # list_word_type = list(word_type.split(", "))
                                                            # list_word = list(list_word_type[0].split(" "))
                                                            # length = len(list_word_type)
                                                            # print(text)
                                                            # print('word_type '+word_type)

                                                            some = word.parent.parent.find_next('tr')
                                                            some2 = some.find_next('tr')
                                                            some3 = some2.find_next('tr')

                                                            if(some.find('td', class_='FrEx') is not None):
                                                                dic["Example"].append(some.text)
                                                            else:
                                                                if(some.find_next('tr').find('td', class_='FrEx') is not None):
                                                                    dic["Example"].append(some2.text)
                                                                elif(some2.find_next('tr').find('td', class_='FrEx') is not None):
                                                                    dic["Example"].append(some3.text)
                                                                else:
                                                                    dic["Example"].append('null')
                                                            
                                                            new = ""
                                                            new2 = ""
                                                            new3 = ""
                                                            if(main is not None):
                                                                if(done == 'no'):
                                                                    div_infs = main.find('div', class_='inflectionsSection')
                                                                    # print(len(div_infs.find_all('div')))
                                                                    if(len(div_infs.find_all('div'))<2):
                                                                        # try:    
                                                                            for i in div_infs.find_all('dl'):
                                                                                first =  i.find('dt', class_='ListInfl').text
                                                                                second = i.find('span', class_='POS2').contents[0].contents[0]
                                                                                # print('first '+first)
                                                                                # print('sec '+second)
                                                                                new = new + first + ': ' + second + '; \n' 
                                                                                one_inflection = True 
                                                                        # except:
                                                                        #     print("An exception occurred 2")
                                                                    else:
                                                                        for divs in div_infs.find_all('div'):
                                                                            # try:
                                                                                for i in divs.find_all('dl'):
                                                                                    if(i.find('dt', class_='ListInfl') is None):
                                                                                        infs = ""
                                                                                        for span in i.find_all('span', class_='tooltip POS2'):
                                                                                            infs = infs + span.contents[0] + " "
                                                                                        li = infs.split(' ')
                                                                                        new2 = new2 +'('+li[0]+'): '+ li[1]+i.contents[-2]+'; \n'
                                                                                        two_inflections = True                   
                                                                                    else:
                                                                                        first =  i.find('dt', class_='ListInfl').text
                                                                                        second = i.find('span', class_='POS2').contents[0].contents[0]
                                                                                        new3 = new3 + first + ': ' + second + '; \n'                                                                        
                                                                            # except:
                                                                            #     print("An exception occurred 2")

                                                                    if(new==""):
                                                                        new = "null"
                                                                        dic["Inflections"].append(new)
                                                                    else:
                                                                        dic["Inflections"].append("null")
                                                                    done = 'yes'
                                                                else:
                                                                    dic["Inflections"].append('null')
                                                            else:
                                                                dic["Inflections"].append('null')


                                                            ls = word_type.split(" ")
                                                            length = len(ls)
                                                            # print(length)
                                                            
                                                            if(word_type not in parts_speach):
                                                                dic["Word"].append(text.replace("⇒", ""))
                                                                dic["Meaning"].append(meaning)
                                                                dic["Speach"].append(word_type)
                                                                dic["Type"].append("null")
                                                                dic["Transitive/Intransitive"].append("null")
                                                                dic["Separable/Inseparable"].append("null")
                                                            else:
                                                                if(length==2):
                                                                    if(word_type=="verbal expression"):
                                                                        dic["Transitive/Intransitive"].append("null")
                                                                        dic["Word"].append(text.replace("⇒", ""))
                                                                        dic["Meaning"].append(meaning)
                                                                        dic["Separable/Inseparable"].append("null")
                                                                        dic["Speach"].append("verb")
                                                                        dic["Type"].append("verbal expression")
                                                                    else:
                                                                        dic["Transitive/Intransitive"].append(ls[0])
                                                                        dic["Word"].append(text.replace("⇒", ""))
                                                                        dic["Meaning"].append(meaning)
                                                                        dic["Separable/Inseparable"].append("null")
                                                                        dic["Speach"].append(ls[1])
                                                                        dic["Type"].append("normal")
                                                                elif(length == 1):
                                                                    dic["Transitive/Intransitive"].append(ls[0])
                                                                    dic["Word"].append(text.replace("⇒", ""))
                                                                    dic["Meaning"].append(meaning)
                                                                    dic["Separable/Inseparable"].append("null")
                                                                    dic["Speach"].append(word_type)
                                                                    dic["Type"].append("normal")                                            
                                                                elif(length==3):
                                                                    if(word_type=="vtr + prep"):
                                                                        dic["Word"].append(text.replace("⇒", ""))
                                                                        dic["Meaning"].append(meaning)
                                                                        dic["Separable/Inseparable"].append("null")
                                                                        dic["Speach"].append("verb")
                                                                        dic["Type"].append("prepositional")    
                                                                        dic["Transitive/Intransitive"].append('transistive')
                                                                    elif(word_type=="vi + prep"):
                                                                        dic["Word"].append(text.replace("⇒", ""))
                                                                        dic["Meaning"].append(meaning)
                                                                        dic["Separable/Inseparable"].append("null")
                                                                        dic["Speach"].append("verb")
                                                                        dic["Type"].append("prepositional")    
                                                                        dic["Transitive/Intransitive"].append('intransitive')
                                                                    elif(word_type=="vtr + adv"):
                                                                        dic["Word"].append(text.replace("⇒", ""))
                                                                        dic["Meaning"].append(meaning)
                                                                        dic["Separable/Inseparable"].append("null")
                                                                        dic["Speach"].append("verb")
                                                                        dic["Type"].append("phrasal")    
                                                                        dic["Transitive/Intransitive"].append('transistive')
                                                                    elif(word_type=="vi + adv"):
                                                                        dic["Word"].append(text.replace("⇒", ""))
                                                                        dic["Meaning"].append(meaning)
                                                                        dic["Separable/Inseparable"].append("null")
                                                                        dic["Speach"].append("verb")
                                                                        dic["Type"].append("phrasal")    
                                                                        dic["Transitive/Intransitive"].append('intransitive')
                                                                    elif(word_type=="adj + prep"):
                                                                        dic["Word"].append(text.replace("⇒", ""))
                                                                        dic["Meaning"].append(meaning)
                                                                        dic["Separable/Inseparable"].append("null")
                                                                        dic["Speach"].append("adjective plus preposition")
                                                                        dic["Type"].append("null")    
                                                                        dic["Transitive/Intransitive"].append('null')
                                                                    else:
                                                                        dic["Word"].append(text.replace("⇒", ""))
                                                                        dic["Meaning"].append(meaning)
                                                                        dic["Separable/Inseparable"].append("null")
                                                                        dic["Speach"].append(ls[1].replace(',', ''))
                                                                        dic["Type"].append(ls[0])    
                                                                        dic["Transitive/Intransitive"].append(ls[2])
                                                                elif(length == 4):
                                                                    dic["Word"].append(text.replace("⇒", ""))
                                                                    dic["Meaning"].append(meaning)
                                                                    dic["Separable/Inseparable"].append(ls[3])
                                                                    dic["Speach"].append(ls[1].replace(',', ''))
                                                                    dic["Type"].append(ls[0])    
                                                                    dic["Transitive/Intransitive"].append(ls[2].replace(',', ''))
                                                                else:
                                                                    dic["Transitive/Intransitive"].append("null")
                                                                    dic["Word"].append(text.replace("⇒", ""))
                                                                    dic["Meaning"].append(meaning)
                                                                    dic["Separable/Inseparable"].append("null")
                                                                    dic["Speach"].append(word_type)
                                                                    dic["Type"].append("null")
                                        else:
                                            continue
                                except:
                                    print("An exception occurred")
                            df = pd.DataFrame(dic)
                            i = wks.rows+1
                            if(df.empty):
                                continue
                            else:
                                wks.set_dataframe(df, start=(i,1), extend=True, copy_head=False)
                            break
                        #else proceed
                        else:
                            for translation in all_translation:
                                try:
                                    if(principal_trans == False):
                                        if(translation.find('span', class_='ph') is not None):
                                            if(translation.find('span', class_='ph').text == 'Principal Translations'):
                                                principal_trans = True
                                                ingles = translation.find_all('td', class_='FrWrd')
                                                for ingle in ingles:
                                                    for word in ingle.findAll("strong"):
                                                            text = word.text
                                                            meaning = word.find_next('td').text
                                                            if(word.find_next('em').get('class')[0] == 'POS2'):
                                                                word_type = word.find_next('em').text
                                                            else:
                                                                word_type = word.find_next('em').find_next('span').contents[0].text 
                                                            # print(text)
                                                            # print('word_type '+word_type)

                                                            some = word.parent.parent.find_next('tr')
                                                            some2 = some.find_next('tr')
                                                            some3 = some2.find_next('tr')
                                                            
                                                            new = ""
                                                            new2 = ""
                                                            new3 = ""
                                                            if(main is not None):
                                                                if(done == 'no'):
                                                                    div_infs = main.find('div', class_='inflectionsSection')
                                                                    # print(len(div_infs.find_all('div')))
                                                                    if(len(div_infs.find_all('div'))<2):
                                                                        try:    
                                                                            for i in div_infs.find_all('dl'):
                                                                                if(i.find('dt', class_='ListInfl') is None):
                                                                                    first = text
                                                                                    if(i.find('dd') is not None):
                                                                                        second = i.find_all('dd')
                                                                                        if(len(second)<2):
                                                                                            sec1 = second[0].contents[0].contents[0]
                                                                                            new = new + first + ': ' + sec1 + '; \n'
                                                                                        elif(len(second)>1):
                                                                                            sec = ''
                                                                                            for c in range(len(second)):
                                                                                                sec = sec + first+': '+ second[c].contents[0].contents[0] + '\n'
                                                                                            new = sec
                                                                                    else:
                                                                                        new = new + first + '('+ i.find_all('span', class_='tooltip POS2')[0].contents[0] +'): '+ i.find_all('span', class_='tooltip POS2')[1].contents[0] + i.contents[-2].replace(':', '') +'; \n'
                                                                                else:    
                                                                                    first =  i.find('dt', class_='ListInfl').text
                                                                                    second = i.find('span', class_='POS2').contents[0].contents[0]
                                                                                    # print('first '+first)
                                                                                    # print('sec '+second)
                                                                                    new = new + first + ': ' + second + '; \n' 
                                                                                one_inflection = True 
                                                                        except:
                                                                            print("An exception occurred 2")
                                                                    else:
                                                                        for divs in div_infs.find_all('div'):
                                                                            try:
                                                                                for i in divs.find_all('dl'):
                                                                                    if(i.find('dt', class_='ListInfl') is None):
                                                                                        infs = ""
                                                                                        for span in i.find_all('span', class_='tooltip POS2'):
                                                                                            infs = infs + span.contents[0] + " "
                                                                                        li = infs.split(' ')
                                                                                        new2 = new2 +'('+li[0]+'): '+ li[1]+i.contents[-2]+'; \n'
                                                                                        two_inflections = True                   
                                                                                    else:
                                                                                        first =  i.find('dt', class_='ListInfl').text
                                                                                        second = i.find('span', class_='POS2').contents[0].contents[0]
                                                                                        new3 = new3 + first + ': ' + second + '; \n'                                                                        
                                                                            except:
                                                                                print("An exception occurred 2")
                                                                    if(one_inflection==True):
                                                                        dic["Word"].append(end_word)
                                                                        dic["Meaning"].append("null")
                                                                        dic["Speach"].append("null")
                                                                        dic["Example"].append("null")
                                                                        dic["Type"].append("null")
                                                                        dic["Transitive/Intransitive"].append("null")
                                                                        dic["Separable/Inseparable"].append("null")
                                                                        dic["Inflections"].append(new)
                                                                        one_inflection = False
                                                                    elif(two_inflections == True):
                                                                        dic["Word"].append(end_word)
                                                                        dic["Meaning"].append("null")
                                                                        dic["Speach"].append("null")
                                                                        dic["Example"].append("null")
                                                                        dic["Inflections"].append(new2)
                                                                        dic["Type"].append("null")
                                                                        dic["Transitive/Intransitive"].append("null")
                                                                        dic["Separable/Inseparable"].append("null")
                                                                    
                                                                        dic["Word"].append(end_word)
                                                                        dic["Meaning"].append("null")
                                                                        dic["Speach"].append("null")
                                                                        dic["Example"].append("null")
                                                                        dic["Type"].append("null")
                                                                        dic["Transitive/Intransitive"].append("null")
                                                                        dic["Separable/Inseparable"].append("null")
                                                                        dic["Inflections"].append(new3)
                                                                        two_inflections = False
                                                                    if(new==""):
                                                                        new = "null"
                                                                        dic["Inflections"].append(new)
                                                                    else:
                                                                        dic["Inflections"].append("null")
                                                                    done = 'yes'
                                                                else:
                                                                    dic["Inflections"].append('null')
                                                            else:
                                                                dic["Inflections"].append('null')


                                                            ls = word_type.split(" ")
                                                            length = len(ls)
                                                            # print(length)
                                                            
                                                            if(word_type not in parts_speach):
                                                                dic["Word"].append(text.replace("⇒", ""))
                                                                dic["Meaning"].append(meaning)
                                                                dic["Speach"].append(word_type)
                                                                dic["Type"].append("null")
                                                                dic["Transitive/Intransitive"].append("null")
                                                                dic["Separable/Inseparable"].append("null")
                                                            else:
                                                                if(length==2):
                                                                    if(word_type=="verbal expression"):
                                                                        dic["Transitive/Intransitive"].append("null")
                                                                        dic["Word"].append(text.replace("⇒", ""))
                                                                        dic["Meaning"].append(meaning)
                                                                        dic["Separable/Inseparable"].append("null")
                                                                        dic["Speach"].append("verb")
                                                                        dic["Type"].append("verbal expression")
                                                                    else:
                                                                        dic["Transitive/Intransitive"].append(ls[0])
                                                                        dic["Word"].append(text.replace("⇒", ""))
                                                                        dic["Meaning"].append(meaning)
                                                                        dic["Separable/Inseparable"].append("null")
                                                                        dic["Speach"].append(ls[1])
                                                                        dic["Type"].append("normal")
                                                                elif(length == 1):
                                                                    dic["Transitive/Intransitive"].append(ls[0])
                                                                    dic["Word"].append(text.replace("⇒", ""))
                                                                    dic["Meaning"].append(meaning)
                                                                    dic["Separable/Inseparable"].append("null")
                                                                    dic["Speach"].append(word_type)
                                                                    dic["Type"].append("normal")                                            
                                                                elif(length==3):
                                                                    if(word_type=="vtr + prep"):
                                                                        dic["Word"].append(text.replace("⇒", ""))
                                                                        dic["Meaning"].append(meaning)
                                                                        dic["Separable/Inseparable"].append("null")
                                                                        dic["Speach"].append("verb")
                                                                        dic["Type"].append("prepositional")    
                                                                        dic["Transitive/Intransitive"].append('transistive')
                                                                    elif(word_type=="vi + prep"):
                                                                        dic["Word"].append(text.replace("⇒", ""))
                                                                        dic["Meaning"].append(meaning)
                                                                        dic["Separable/Inseparable"].append("null")
                                                                        dic["Speach"].append("verb")
                                                                        dic["Type"].append("prepositional")    
                                                                        dic["Transitive/Intransitive"].append('intransitive')
                                                                    elif(word_type=="vtr + adv"):
                                                                        dic["Word"].append(text.replace("⇒", ""))
                                                                        dic["Meaning"].append(meaning)
                                                                        dic["Separable/Inseparable"].append("null")
                                                                        dic["Speach"].append("verb")
                                                                        dic["Type"].append("phrasal")    
                                                                        dic["Transitive/Intransitive"].append('transistive')
                                                                    elif(word_type=="vi + adv"):
                                                                        dic["Word"].append(text.replace("⇒", ""))
                                                                        dic["Meaning"].append(meaning)
                                                                        dic["Separable/Inseparable"].append("null")
                                                                        dic["Speach"].append("verb")
                                                                        dic["Type"].append("phrasal")    
                                                                        dic["Transitive/Intransitive"].append('intransitive')
                                                                    elif(word_type=="adj + prep"):
                                                                        dic["Word"].append(text.replace("⇒", ""))
                                                                        dic["Meaning"].append(meaning)
                                                                        dic["Separable/Inseparable"].append("null")
                                                                        dic["Speach"].append("adjective plus preposition")
                                                                        dic["Type"].append("null")    
                                                                        dic["Transitive/Intransitive"].append('null')
                                                                    else:
                                                                        dic["Word"].append(text.replace("⇒", ""))
                                                                        dic["Meaning"].append(meaning)
                                                                        dic["Separable/Inseparable"].append("null")
                                                                        dic["Speach"].append(ls[1].replace(',', ''))
                                                                        dic["Type"].append(ls[0])    
                                                                        dic["Transitive/Intransitive"].append(ls[2])
                                                                elif(length == 4):
                                                                    dic["Word"].append(text.replace("⇒", ""))
                                                                    dic["Meaning"].append(meaning)
                                                                    dic["Separable/Inseparable"].append(ls[3])
                                                                    dic["Speach"].append(ls[1].replace(',', ''))
                                                                    dic["Type"].append(ls[0])    
                                                                    dic["Transitive/Intransitive"].append(ls[2].replace(',', ''))
                                                                else:
                                                                    dic["Transitive/Intransitive"].append("null")
                                                                    dic["Word"].append(text.replace("⇒", ""))
                                                                    dic["Meaning"].append(meaning)
                                                                    dic["Separable/Inseparable"].append("null")
                                                                    dic["Speach"].append(word_type)
                                                                    dic["Type"].append("null")
                                                            
                                                            if(some.find('td', class_='FrEx') is not None):
                                                                dic["Example"].append(some.text)
                                                            else:
                                                                if(some.find_next('tr').find('td', class_='FrEx') is not None):
                                                                    dic["Example"].append(some2.text)
                                                                elif(some2.find_next('tr').find('td', class_='FrEx') is not None):
                                                                    dic["Example"].append(some3.text)
                                                                else:
                                                                    dic["Example"].append('null')
                                        else:
                                            continue
                                    if(additional_trans == False):
                                        if(translation.find('span', class_='ph') is not None):
                                            if(translation.find('span', class_='ph').text == 'Additional Translations'):
                                                additional_trans = True
                                                ingles = translation.find_all('td', class_='FrWrd')
                                                for ingle in ingles:
                                                    for word in ingle.findAll("strong"):
                                                        # if word not in dic["Word"]:
                                                            text = word.text
                                                            meaning = word.find_next('td').text
                                                            if(word.find_next('em').get('class')[0] == 'POS2'):
                                                                word_type = word.find_next('em').text
                                                            else:
                                                                word_type = word.find_next('em').find_next('span').contents[0].text 

                                                            # list_word_type = list(word_type.split(", "))
                                                            # list_word = list(list_word_type[0].split(" "))
                                                            # length = len(list_word_type)
                                                            # print(text)
                                                            # print('word_type '+word_type)

                                                            some = word.parent.parent.find_next('tr')
                                                            some2 = some.find_next('tr')
                                                            some3 = some2.find_next('tr')

                                                            if(some.find('td', class_='FrEx') is not None):
                                                                dic["Example"].append(some.text)
                                                            else:
                                                                if(some.find_next('tr').find('td', class_='FrEx') is not None):
                                                                    dic["Example"].append(some2.text)
                                                                elif(some2.find_next('tr').find('td', class_='FrEx') is not None):
                                                                    dic["Example"].append(some3.text)
                                                                else:
                                                                    dic["Example"].append('null')
                                                            
                                                            new = ""
                                                            new2 = ""
                                                            new3 = ""
                                                            if(main is not None):
                                                                if(done == 'no'):
                                                                    div_infs = main.find('div', class_='inflectionsSection')
                                                                    # print(len(div_infs.find_all('div')))
                                                                    if(len(div_infs.find_all('div'))<2):
                                                                        try:    
                                                                            for i in div_infs.find_all('dl'):
                                                                                first =  i.find('dt', class_='ListInfl').text
                                                                                second = i.find('span', class_='POS2').contents[0].contents[0]
                                                                                # print('first '+first)
                                                                                # print('sec '+second)
                                                                                new = new + first + ': ' + second + '; \n' 
                                                                                one_inflection = True 
                                                                        except:
                                                                            print("An exception occurred 2")
                                                                    else:
                                                                        for divs in div_infs.find_all('div'):
                                                                            try:
                                                                                for i in divs.find_all('dl'):
                                                                                    if(i.find('dt', class_='ListInfl') is None):
                                                                                        infs = ""
                                                                                        for span in i.find_all('span', class_='tooltip POS2'):
                                                                                            infs = infs + span.contents[0] + " "
                                                                                        li = infs.split(' ')
                                                                                        new2 = new2 +'('+li[0]+'): '+ li[1]+i.contents[-2]+'; \n'
                                                                                        two_inflections = True                   
                                                                                    else:
                                                                                        first =  i.find('dt', class_='ListInfl').text
                                                                                        second = i.find('span', class_='POS2').contents[0].contents[0]
                                                                                        new3 = new3 + first + ': ' + second + '; \n'                                                                        
                                                                            except:
                                                                                print("An exception occurred 2")

                                                                    if(new==""):
                                                                        new = "null"
                                                                        dic["Inflections"].append(new)
                                                                    else:
                                                                        dic["Inflections"].append("null")
                                                                    done = 'yes'
                                                                else:
                                                                    dic["Inflections"].append('null')
                                                            else:
                                                                dic["Inflections"].append('null')


                                                            ls = word_type.split(" ")
                                                            length = len(ls)
                                                            # print(length)
                                                            
                                                            if(word_type not in parts_speach):
                                                                dic["Word"].append(text.replace("⇒", ""))
                                                                dic["Meaning"].append(meaning)
                                                                dic["Speach"].append(word_type)
                                                                dic["Type"].append("null")
                                                                dic["Transitive/Intransitive"].append("null")
                                                                dic["Separable/Inseparable"].append("null")
                                                            else:
                                                                if(length==2):
                                                                    if(word_type=="verbal expression"):
                                                                        dic["Transitive/Intransitive"].append("null")
                                                                        dic["Word"].append(text.replace("⇒", ""))
                                                                        dic["Meaning"].append(meaning)
                                                                        dic["Separable/Inseparable"].append("null")
                                                                        dic["Speach"].append("verb")
                                                                        dic["Type"].append("verbal expression")
                                                                    else:
                                                                        dic["Transitive/Intransitive"].append(ls[0])
                                                                        dic["Word"].append(text.replace("⇒", ""))
                                                                        dic["Meaning"].append(meaning)
                                                                        dic["Separable/Inseparable"].append("null")
                                                                        dic["Speach"].append(ls[1])
                                                                        dic["Type"].append("normal")
                                                                elif(length == 1):
                                                                    dic["Transitive/Intransitive"].append(ls[0])
                                                                    dic["Word"].append(text.replace("⇒", ""))
                                                                    dic["Meaning"].append(meaning)
                                                                    dic["Separable/Inseparable"].append("null")
                                                                    dic["Speach"].append(word_type)
                                                                    dic["Type"].append("normal")                                            
                                                                elif(length==3):
                                                                    if(word_type=="vtr + prep"):
                                                                        dic["Word"].append(text.replace("⇒", ""))
                                                                        dic["Meaning"].append(meaning)
                                                                        dic["Separable/Inseparable"].append("null")
                                                                        dic["Speach"].append("verb")
                                                                        dic["Type"].append("prepositional")    
                                                                        dic["Transitive/Intransitive"].append('transistive')
                                                                    elif(word_type=="vi + prep"):
                                                                        dic["Word"].append(text.replace("⇒", ""))
                                                                        dic["Meaning"].append(meaning)
                                                                        dic["Separable/Inseparable"].append("null")
                                                                        dic["Speach"].append("verb")
                                                                        dic["Type"].append("prepositional")    
                                                                        dic["Transitive/Intransitive"].append('intransitive')
                                                                    elif(word_type=="vtr + adv"):
                                                                        dic["Word"].append(text.replace("⇒", ""))
                                                                        dic["Meaning"].append(meaning)
                                                                        dic["Separable/Inseparable"].append("null")
                                                                        dic["Speach"].append("verb")
                                                                        dic["Type"].append("phrasal")    
                                                                        dic["Transitive/Intransitive"].append('transistive')
                                                                    elif(word_type=="vi + adv"):
                                                                        dic["Word"].append(text.replace("⇒", ""))
                                                                        dic["Meaning"].append(meaning)
                                                                        dic["Separable/Inseparable"].append("null")
                                                                        dic["Speach"].append("verb")
                                                                        dic["Type"].append("phrasal")    
                                                                        dic["Transitive/Intransitive"].append('intransitive')
                                                                    elif(word_type=="adj + prep"):
                                                                        dic["Word"].append(text.replace("⇒", ""))
                                                                        dic["Meaning"].append(meaning)
                                                                        dic["Separable/Inseparable"].append("null")
                                                                        dic["Speach"].append("adjective plus preposition")
                                                                        dic["Type"].append("null")    
                                                                        dic["Transitive/Intransitive"].append('null')
                                                                    else:
                                                                        dic["Word"].append(text.replace("⇒", ""))
                                                                        dic["Meaning"].append(meaning)
                                                                        dic["Separable/Inseparable"].append("null")
                                                                        dic["Speach"].append(ls[1].replace(',', ''))
                                                                        dic["Type"].append(ls[0])    
                                                                        dic["Transitive/Intransitive"].append(ls[2])
                                                                elif(length == 4):
                                                                    dic["Word"].append(text.replace("⇒", ""))
                                                                    dic["Meaning"].append(meaning)
                                                                    dic["Separable/Inseparable"].append(ls[3])
                                                                    dic["Speach"].append(ls[1].replace(',', ''))
                                                                    dic["Type"].append(ls[0])    
                                                                    dic["Transitive/Intransitive"].append(ls[2].replace(',', ''))
                                                                else:
                                                                    dic["Transitive/Intransitive"].append("null")
                                                                    dic["Word"].append(text.replace("⇒", ""))
                                                                    dic["Meaning"].append(meaning)
                                                                    dic["Separable/Inseparable"].append("null")
                                                                    dic["Speach"].append(word_type)
                                                                    dic["Type"].append("null")
                                        else:
                                            continue
                                except:
                                    print("An exception occurred")
                        print('DONE')
                        # try:
                        df = pd.DataFrame(dic)
                        i = wks.rows+1
                        if(df.empty):
                            continue
                        else:
                            wks.set_dataframe(df, start=(i,1), extend=True, copy_head=False)
                        # except:
                        #     print("Good job")
        end = time.time()
        print("Time Taken: {:.6f}s".format(end-start))
    except:
        print('No Contents')
word_scrape()
