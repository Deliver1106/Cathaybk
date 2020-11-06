#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
from bs4 import BeautifulSoup
import math
from requests.cookies import RequestsCookieJar
import numpy as np
from pymongo import MongoClient


# In[2]:


AllURLUser = []
for pages in ["1","3"]:
    cookie_jar = RequestsCookieJar()
    cookie_jar.set("urlJumpIp",pages)
    res = requests.get("https://rent.591.com.tw/?kind=0&firstRow=0",cookies=cookie_jar)
    soup = BeautifulSoup(res.text, 'html.parser')
    soupitems = soup.select("div.pull-left.hasData")
    soupitems = int(''.join([n for n in soupitems[0].text if n.isdigit()]))
    print("Page "+pages+" started.")

    for Row in [i*30 for i in range((soupitems // 30)+1)]:
        res = requests.get("https://rent.591.com.tw/?kind=0&firstRow="+str(Row),cookies=cookie_jar)
        soup = BeautifulSoup(res.text, 'html.parser')

        selectedsoup = soup.select("div#content h3 a")
        allURL = ["https:"+i['href'] for i in selectedsoup]
        allUserType = [i.text.split(" ")[0] for i in soup.select("div#content li.pull-left.infoContent p:nth-of-type(3) em:nth-of-type(1)")]

        allURLUser = [(i, v) for (i, v) in zip(allURL, allUserType)]
        AllURLUser.extend(allURLUser)
        print(Row)


# In[3]:


AllURLUser


# In[4]:


AllData = []
client = MongoClient('localhost', 27017)
db = client['Web591']
collection = db['RentInfo']

for item in range(len(AllURLUser)):
    try:
        print(AllURLUser[item][0])
        res = requests.get(AllURLUser[item][0])
        soup = BeautifulSoup(res.text, 'html.parser')

        FilterSex = [i.text.replace(" ","") == "性別要求" for i in soup.select("ul.clearfix.labelList.labelList-1 div.one")]
        ListSex = [i.text.replace(" ","") for i in soup.select("ul.clearfix.labelList.labelList-1 div.two")]
        if np.sum(FilterSex) == 0:
            SexReq = np.nan
        else:
            SexReq = [i for (i, v) in zip(ListSex, FilterSex) if v][0].replace("：","").strip()

        AllInfo = [[item.strip() for item in j.text.split(":")] for j in soup.select("div.detailInfo.clearfix ul li")]
        Current = [i[1] for i in AllInfo if i[0] == "現況"]
        if len(Current) == 0:
            Current = np.nan
        else:
            Current = Current[0]

        Types = [i[1] for i in AllInfo if i[0] == "型態"]
        if len(Types) == 0:
            Types = np.nan
        else:
            Types = Types[0]

        Data = {
            "出租者":soup.select("div.avatarRight i")[0].text,
            "出租者身分":AllURLUser[item][1],
            "聯絡電話":soup.select("div.userInfo span.dialPhoneNum")[0]["data-value"],
            "型態":Types,
            "現況":Current,
            "性別需求": SexReq
        }

        AllData.append(Data)
        if len(AllData) == 10:
            collection.insert_many(AllData)
            AllData = []
            print("There is 10 dict import to Mongodb.")
    except:
        print(AllURLUser[item][0]+' 發生錯誤')
        
collection.insert_many(AllData)
print("There is "+str(len(AllData))+" dict import to Mongodb.")


# In[5]:


AllData

