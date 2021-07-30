import re
from bs4 import BeautifulSoup
import json
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import pprint

opts = Options()
opts.add_argument(" --headless")
browser=driver = webdriver.Chrome(ChromeDriverManager().install(),options=opts)
driver.set_page_load_timeout(200)
driver.maximize_window()
driver.implicitly_wait(10)

def get_last_months(m):
    m_dict={
        1:'31',
        2:'28',
        3:'31',
        4:'30',
        5:'31',
        6:'30',
        7:'31',
        8:'31',
        9:'30',
        10:'31',
        11:'30',
        12:'31'
    }
    return m_dict[m]

def striphtml(data):
    p = re.compile(r'<.*?>')
    s=p.sub('', data)
    if s:
        return s
    else:
        return ''

def convert_k_number(num):
    if 'K' in num:
        dig=float(re.split('K',num)[0])*1000
    elif 'M' in num:
        dig=float(re.split('M',num)[0])*1000*1000
    else:
        dig=float(num)
    return int(dig)


def get_page(url):
    new_url='https://twitter.com/search?q=%22bitcoin%22%20min_replies%3A100%20min_faves%3A2000%20min_retweets%3A1000%20until%3A2020-12-31%20since%3A2020-01-01&src=typed_query'
    safafas='https://twitter.com/search?q=%22bitcoin%22%20min_replies%3A10%20min_faves%3A20%20min_retweets%3A10%20until%3A2020-01-31%20since%3A2020-01-01&src=typed_query'
    #driver.get('https://twitter.com/search?q=%22bitcoin%22%20min_replies%3A500%20min_faves%3A2000%20min_retweets%3A1000&src=typed_query')
    
    delay = 10 # seconds
    page=0
    
    try:
        driver.execute_script("window.scrollBy(0, window.innerHeight);")
        time.sleep(2)
        myElem = WebDriverWait(browser, delay).until(EC.visibility_of_element_located((By.XPATH,'//*[@data-testid="tweet"]')))
    except:
        print("Loading took too much time!")
        
    return driver.page_source
    

def get_tweets(query):
    base_url="https://twitter.com/search"
    data=[]
    term_in=input('enter search term  : ')
    replies_in=int(input('enter min replies  : '))
    retweets_in=int(input('enter min retweets  : '))
    likes_in=int(input('enter min likes  : '))
    year=input('enter year: yyyy : ')
    total_months=int(input('enter number of months: '))
    output_file = input('enter output file path : ')
    

    for month in range(1,total_months+1):
        if month<10:
            m='0'+str(month)
        else:
            m=str(month)
        
        query={
        "term":term_in,
        "replies":replies_in,
        "retweets":retweets_in,
        "likes":likes_in,
        "start":year+"-"+m+"-"+get_last_months(month),
        "end":year+"-"+m+"-01"
        }
        identity=1
        
        custom_url = base_url+f'?q=%22{query["term"]}%22%20min_replies%3A{query["replies"]}%20min_faves%3A{query["likes"]}%20min_retweets%3A{query["retweets"]}%20until%3A{query["start"]}%20since%3A{query["end"]}&src=typed_query'
        #print(custom_url)
        unique_tweets=set()

        p=1
        flag=True
        prev=0
    
        driver.get(custom_url)
        while identity < 100:   
            try:
                prev=identity
                response=get_page(custom_url)
                soup = BeautifulSoup(response,'lxml')
                tweets= soup.findAll("div",{"data-testid":"tweet"})
                
                #print(f'page: {p},  number of tweets {len(tweets)}')
                for tweet in tweets:
                    lang=tweet.find("div",{"lang":True})
                    if lang:
                        uid=lang.get("id")
                        language=lang.get('lang')
                        raw= tweet.findAll("span")
                        username=raw[2].contents[0][1:]
                        text=""

                        for line in raw[4:-6]:
                            for t in line.contents:
                                text+=striphtml(str(t))
                        text=text.replace("\n"," ")
                        replies = striphtml(str(raw[-6].contents[0]))
                        retweets = striphtml(str(raw[-4].contents[0]))
                        likes = striphtml(str(raw[-2].contents[0]))
                        if uid in unique_tweets:
                            #print('no more unique tweets')
                            pass
                        if uid not in unique_tweets and language=="en":
                            unique_tweets.add(uid)
                            data.append({
                                    "id":str(identity)+"-term-"+m+"-"+year,
                                    "username":username,
                                    "tweet":text,
                                    "time":tweet.find("time").get("datetime"),
                                    "replies":convert_k_number(replies),
                                    "retweets":convert_k_number(retweets),
                                    "likes":convert_k_number(likes)
                                })
                            identity+=1
                p+=1
            except:
                pass
        print(len(data),' tweets fetched for month ',month)
        #driver.close()       
    with open(output_file,'w') as fp:
        json.dump(data,fp)
        print('number of tweets : ',len(data))
        
    
get_tweets("crypto")
driver.quit()