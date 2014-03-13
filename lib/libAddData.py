#!/usr/bin/python3
# coding=utf-8
# Filename : UpdateDigkey.py
#Author:Bill Zhang
#Email:zchv@msn.com
#Digkey collection thread

from socket import timeout
import urllib.request
import http.cookiejar
#import the BeautifulSoup which parse the html
from bs4 import BeautifulSoup
#from bs4.diagnose import diagnose
#import the database pymongo and random number
import pymongo
import random
#import python's reguler expression lib
#import re
import os
import time
import functools

class UpdateClass:
    """The UpdateClass:
        This class has the follow's method:
        1.getCode(self,url)
        2.toUpdate(self,HtmlCode,spplier)
    
        The detail of function is as follows:
            getCode:
                return the html code string
                or wrong code number when failed
            toUpdate:
                return the data list
    
    """
    def __init__(self, cookiefile='cache/cookies.txt',proxy=0):
        
        '''通过 cookie 保持一个 HTTP 会话'''

        '''
        proxy 为 True，使用环境变量，为 dict，作为代理，为假值，不使用代理
        默认使用环境变量
                  ''''''
        '''
        self.CPIA=0
        self.cookie = http.cookiejar.MozillaCookieJar(cookiefile)
        UserAgent ="Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36"
        if os.path.exists(cookiefile):
            self.cookie.load()
        if UserAgent is not None:
            self.UserAgent = UserAgent
        if proxy is True:
          self.urlopener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookie),
            urllib.request.ProxyHandler(),
          )
        elif isinstance(proxy, dict):
          self.urlopener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookie),
            urllib.request.ProxyHandler(proxy),
          )
        elif not proxy:
          self.urlopener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookie),
          )
        else:
          return 'W'
    @functools.lru_cache(maxsize=None)
    def getCode(self,keyword=0,k=0,url=0):    
        """The function getCode is to get the source code of the webpages"""
        if url is 0:
            url='http://www.ickey.cn/getData_res.php?kw=%s&k=%s&j=%s&w_id=3118987' % (keyword,k,int(round(random.random()*10000)))
        else:
            url=url
        #headers
        headers = {'Referer':url ,'User-agent':self.UserAgent,'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8','Accept-Language':'q=0.8,en-US;q=0.6,en;q=0.4'}
        req = urllib.request.Request(url=url,headers=headers)
        #HtmlCode save the source code of the webpages
        try:
            response = self.urlopener.open(req,timeout=20)
            if response is None:
                return(666,0)
        except urllib.error.HTTPError as e:   
            print('Error code:',e.code)
            return (666,e.code)
        except urllib.error.URLError as e:   
            print('Reason',e.reason) 
            return (666,e.reason)
        except timeout:
            return (666,0)
        HtmlCode=response.read().decode('utf-8') 
        self.HtmlCode= HtmlCode 
        return 'Y'
        ##parse the html by using the BeautifulSoup

        ##f = open(URL[-7:], 'w') # open for 'w'riting
        ##f.write(HtmlCode) # write text to file
        ##f.close() # close the file
    
    @functools.lru_cache(maxsize=None)
    def toGetData(self,k):
        """We use the BeautifulSoup to parse the html code.
        Some conversion as follow:
            eFind:the useful pattern in html code 
            qFind:the html's div specifier of price info
            qFind:the html's div specifier of quantity info
            pRE: the reguler pattern of Price
            qRE: the regular pattern of quantity
       The supplier map as follow:
            "Digikey"   :1
            "Mouser"    :2
            "future"    :3
        The data format as follow:
            list[goods_quantity,quantity1,price1,quantity2,price2......]
        """
        #re extract content digkey patternu 
        if(len(self.HtmlCode)>20):
            SourceCode=BeautifulSoup(self.HtmlCode,"lxml")
       # SourceCode=BeautifulSoup(html,"lxml")
        #if can't get the return code 
        #the quantity will be -1
        #if(html):
        #    SourceCode=BeautifulSoup(html,"lxml")
       
        else:
            log=open("log/libupdate.log","w")
            log.write("Can not open the pages:have no data in node")
            log.close()
            return 1
        SIH=SourceCode.find("dd").find("div").find("a") 
        if SIH is None:
            return 1
        #all the info about the provider 
        PA={}
        PA['PUrl']=SIH.get('href')
        PIUrl=SIH.find("img").get('src')[6:]
        PA['PIUrl']="/Public/img%s" % PIUrl
        PA['status']=0
        SI=SourceCode.find("div",class_="minicar_list") 
        SI=SI.table
        PP=SI.find_all('tr')
        if PP is None:
            return 1
        PIA=[]
        for i in range(0,len(list(PP))-1):
            PI={}
            if i is not 0:
                PD=PP[i].find_all('td')
                if(len(PD)<9):
                    return 1
                PI['ModelName']=self.clear(PD[0].get_text())
                if '(' in PI['ModelName']:
                    continue
                PI['BrandName']=self.clear(PD[1].get_text())
                PI['Desc']=self.clear(PD[2].get_text())
                PI['Stock']=[text for text in PD[3].stripped_strings]
                SI1=PI["Stock"][0].find(':')+1
                if SI1 is not -1:
                    PI['Stock'][0]=int(PI['Stock'][0][SI1:])
                else:
                    PI['Stock'][0]=int(PI['Stock'][0])
                if len(PI['Stock']) is 1:
                    PI['Stock'].append(0)
                else:
                    SI2=str(PI["Stock"][1]).find(':')+1
                    PI['Stock'][1]=int(PI['Stock'][1][SI2:])
                #tiered price and quantity
                TieredNo=[int(text.replace('+','')) for text in PD[4].stripped_strings] 
                CheckPrice=PD[5].get_text()
                if 'HK$' in CheckPrice:
                    TieredPrice=[float(text.replace("HK$",""))*0.13 for text in PD[5].stripped_strings]
                    check=0
                elif '￥' in CheckPrice:
                    continue
                   # TieredPrice=[float(text.replace("￥",""))*1 for text in PD[5].stripped_strings]
                   # check=1
                elif '$' in CheckPrice:
                    TieredPrice=[float(text.replace("$","")) for text in PD[5].stripped_strings]
                    check=0
                else:
                    continue
                PI['Tiered']=self.combine(TieredNo,TieredPrice,check)
                PI['DT'] =[text for text in PD[8].stripped_strings]
               # pC=[str(ord(text)) for text in PA['PUrl'][7:]]
               # pC=''.join(pC)
                PI['GoodsId']='%03d%s%03d' % (int(k),int(time.time())%10000,int(i))
                #docurl
                #DocUrl=PD[9]
                DocUrl=PD[9].find('a',class_="hSea_down2")
                #provider name
                PI['PN']=(PA['PUrl'].split(sep='.'))[1]
                if DocUrl:
                    PI['DocUrl']=DocUrl.get('href')
                else:
                    PI['DocUrl']='www.hqchip.com'
                #print(GoodsId)
                PI['buy_url']='/Product_%s.html' % PI['GoodsId']
                #print(PI)
                PIA.append(PI)
                #print(PIA)
        PA['PD']=PIA
        self.CPIA=PIA
       # self.PA=PA
       # self.saving()
        #print(PA)
        return PA
    def clear(self,text):
        text=text.replace('\r','')
        text=text.replace('\n','')
        text=text.replace('\t','')
        text=text.replace('  ','')
        return text
    def combine(self,number,price,check=0):
        tiered=[]
        for i in range(0,len(number)):
            temp=[]
            if check is 0:
                temp=[number[i],float('%.4f' % price[i]),float('%.4f' % (price[i]*1.05)),float('%.4f' % (price[i]*7.6))]
            else:
                temp=[number[i],price[i],0,float('%.4f' % (price[i]*7.6))]
            tiered.append(temp)
        return tiered

    def saving(self):
        if self.CPIA:
            data=self.CPIA
        else:
            return "W"
        uri="mongodb://hqjf:aa88OO00@172.168.16.98/hqchip"
        try:
            con=pymongo.MongoClient(uri)
            db=con.hqchip
            db.update.insert(data)
        except pymongo.errors.ConnectionFailure:
            print("fail to connect mongodb,try after 3s")
            time.sleep(3)
            con=pymongo.MongoClient(uri)
        except pymongo.errors.ConfigurationError:
            print("Your password config is not right,fail to connect mongodb!")
            print("The formate should be 'mongodb://user:password@example.com/the_database'")
            print("Please try again!")
        except pymongo.errors.InvalidURI:
            print("Your uri is not write,fail to connect mongodb!")
            print("The formate should be 'mongodb://user:password@example.com/the_database'")
            print("Please try again!")
        except pymongo.errors.AutoReconnect(message='Lose connection,reconnect.....', errors=None):
            print("reconnect .......")

if __name__=="__main__":
    """
    ---if __name=="__main__"-----
    This is for debug this moudle,
    When run this moudle as the main 
    the code below will run
    """
   # url="http://www.mouser.com/ProductDetail/STMicroelectronics/STF25N80K5/?qs=sGAEpiMZZMvplms98TlKY4UF1xiBXHhHzRWqrKmsv9g%3d"
   # url="http://www.ickey.cn/searchIndex2.php?keyword=lm358"
    #url="http://www.digikey.com/product-detail/en/650025-2/650025-2-ND/297680"
    a=UpdateClass()
   # kw="IRAMX20"
   # url1="http://www.ickey.cn/searchIndex2.php?keyword=%s" % kw
   # url2="http://www.ickey.cn/searchIndex.php?kw=%s" %kw
   # a.getCode(url1)
   # a.getCode(url2)
   # time.sleep(0.05)
   # a.getCode(url1)
   # for i in range(1,50):
   #     fileHandle = open ('result3.html','a') 
   #     url='http://www.ickey.cn/getData_res.php?kw=%s&k=%s' % (kw,i)
   #     b=a.getCode(url)
   # #type(abc)
   #     fileHandle.write("-------------k=%s-------------------" % i)
   #     fileHandle.write(a.HtmlCode) 
   #     fileHandle.close() 
    sf=open("result.html")
    sh=sf.read()
    sf.close()
    a.toGetData(sh)




