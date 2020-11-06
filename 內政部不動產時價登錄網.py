#!/usr/bin/env python
# coding: utf-8

# In[1]:


from urllib.request import urlopen
from xml.etree.ElementTree import parse
import pandas as pd
import time, random
import numpy as np
import re


# In[2]:


URL_a = "https://plvr.land.moi.gov.tw//Download?fileName=a_lvr_land_a.xml"
URL_b = "https://plvr.land.moi.gov.tw//Download?fileName=b_lvr_land_a.xml"
URL_e = "https://plvr.land.moi.gov.tw//Download?fileName=e_lvr_land_a.xml"
URL_f = "https://plvr.land.moi.gov.tw//Download?fileName=f_lvr_land_a.xml"
URL_h = "https://plvr.land.moi.gov.tw//Download?fileName=h_lvr_land_a.xml"
URLs = [URL_a,URL_b,URL_e,URL_f,URL_h]
URLs


# In[3]:


xmldoc = parse(urlopen(URLs[0]))
xroot = xmldoc.getroot()
ColName = [i.tag for i in xroot[0]]


# In[4]:


df_all = pd.DataFrame(columns = ColName)
for URL in URLs:
    time.sleep(random.randrange(1, 4))
    xmldoc = parse(urlopen(URL))
    xroot = xmldoc.getroot()
    df_temp = pd.DataFrame([[i.text for i in xroot[j]] for j in range(len(xroot))],columns = ColName)
    df_all = df_all.append(df_temp,ignore_index=True)
    print(URL.split("//")[2].split("=")[1],"finished.")


# In[5]:


df_all.head()


# In[6]:


filter_a = df_all[(df_all["主要用途"] == "住家用") & 
                  [bool(re.search("住宅大樓",i)) if i is not None else False for i in df_all["建物型態"]] & 
                  [bool(re.search("^十[^一二]層|[一二三四五六七八九]十[一二三四五六七八九]?層",j)) 
                   if j is not None else False 
                   for j in df_all["總樓層數"]]
                 ]


# In[7]:


filter_a.to_csv("filter_a.csv",index=False,encoding='utf_8_sig')


# In[36]:


filter_b = df_all.copy()
filter_b["車位"] = [int(re.search("車位(\\d+)",i).group(1)) if i is not None else 0 for i in df_all["交易筆棟數"]]
filter_b["總價元"] = pd.to_numeric(filter_b["總價元"])
filter_b["車位總價元"] = pd.to_numeric(filter_b["車位總價元"])
filter_b = filter_b[["土地區段位置建物區段門牌","車位","總價元","車位總價元"]]
filter_b["車位總價元"] = filter_b["車位總價元"].replace(0,np.nan)
filter_b["車位平均價元"] = filter_b["車位總價元"]/filter_b["車位"]
filter_b


# In[37]:


filter_b = filter_b.aggregate({"土地區段位置建物區段門牌":'count','車位': 'sum','總價元': 'mean','車位總價元':'mean','車位平均價元':'mean'}).reset_index().T
filter_b = filter_b[1:]
filter_b.columns = ["總件數","總車位數","平均總價位","平均總車位總價元","車位平均價元"]
filter_b


# In[38]:


filter_b.to_csv("filter_b.csv",index=False,encoding='utf_8_sig')

