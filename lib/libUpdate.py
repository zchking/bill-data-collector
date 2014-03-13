#!/usr/bin/python3
#coding=utf-8
#utf-8
# Filename : UpdateDigkey.py
#Author:Bill Zhang
#Email:zchv@msn.com
#Digkey collection thread
#crawl web data
import getWeb as gw
#import the BeautifulSoup which parse the html
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
#from bs4.diagnose import diagnose
#import the database pymongo and random number
#import python's reguler expression lib
import re
#import os
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
        pass
   # @functools.lru_cache(maxsize=None)
    def getCode(self,keyword=0,k=0,url=0):    
        """The function getCode is to get the source code of the webpages"""
        if url is not 0:
            self.url=url
        #headers
        s=gw.get(self.url)
        if s.status_code is not 200:
            print("The html code is wrong!")
            return 0
        self.HtmlCode=s.text 
        return 'Y'
        ##parse the html by using the BeautifulSoup
        ##f = open(URL[-7:], 'w') # open for 'w'riting
        ##f.write(HtmlCode) # write text to file
        ##f.close() # close the file
    
   # @functools.lru_cache(maxsize=None)
    def toGetData(self,url,ID,k):
        """We use the BeautifulSoup to parse the html code.
        Some conversion as follow:
            L : list
            D : dict

        The supplier map as follow:
            "世平集团" :1
            "Mouser"   :2
            "Digikey"  :3
            "future"   :4
            "verical"  :5
        The data format as follow:
            list[goods_quantity,quantity1,price1,quantity2,price2......]
        """
        self.url=url
        check=self.getCode(k=k)
        #re extract content digkey patternu 
        if check is not 'Y' or len(self.HtmlCode)<20:
            log=open("log/libupdate.log","w")
            log.write("Can not open the pages:have no data in node")
            log.close()
            return 0
        #k=2 search mouser

        if k is 2:
            self.getMouser(ID)
        #k=3 search digikey
        elif k is 3:
            self.getDigikey(ID)
        #k=4 search future
        elif k is 4:
            self.getFuture(ID)
        elif k is 5:
            self.getVerical(ID)
        else:
            self.getAll(ID)
        return self.PI
    #get data from Verical
    def getDigikey(self,ID):
        parse_only=SoupStrainer("table",class_="product-details-table")   
        try:
            SourceCode=BeautifulSoup(self.HtmlCode,"lxml", parse_only=parse_only)
            #print(SourceCode)
            #SourceCode=SourceCode.find(id="product-details")
            #SC1 the part of productdetail-box1
            SC1=SourceCode.find("tr",class_="product-details-basic").find("table",class_="product-details")
            PI={}
            #Price Tired
            S=SC1.find("td",class_="catalog-pricing").find("table",id="pricing")
            TieredNo=[]
            TieredPrice=[]
            for Tired in S.find_all("td",align="center"):
                if '电' in str(Tired.get_text()):
                    TieredNo.append(0)
                    TieredPrice.append(0)
                    break
                TieredNo.append(Tired.get_text().replace(',',''))
                TieredPrice.append(float(str(Tired.next_sibling.string).replace(',','')))
            PI['Tiered']=self.combine(TieredNo,TieredPrice) 
            pq=SC1.find("td",id="quantityavailable").get_text()
            if 'Digi' not in pq:
                PI["Stock"]=[0,TieredNo[0]]
                PI['ID']=ID
                self.PI=PI
                return(PI)
            pq=re.search(r"\d+,*\d*",pq).group(0) 
            PI["Stock"]    =[int(pq.replace(',','')),TieredNo[0]]   
            PI['ID']=ID
            self.PI=PI
            return(PI)
        except AttributeError:
            print("...........%s............" % AttributeError)
            self.PI=0
            return 0
    #get data from mouser        
    def getMouser(self,ID):
        parse_only=SoupStrainer(id="product-details")    
        try:
            SourceCode=BeautifulSoup(self.HtmlCode,"lxml", parse_only=parse_only)
            
            #SC1 the part of productdetail-box1
            PI={}
            #SC2 the part of price and quantity
            
            SC2            =SourceCode.find("table",id="productdetail-box2")
            if SC2 is None:
                self.PI=0
                return 0
            #Price Tired
            S=SC2.find("div",id="ctl00_ContentMain_BoxPricing").find("div",id="ctl00_ContentMain_divPricing")
            if S is None:
                self.PI=0
                return 0
            TieredNo=[]
            for text in S.find_all("td",class_="PriceBreakQuantity"):
                if ':' not in text.get_text():
                    continue
                TieredNo.append(int(self.clear(text.get_text().replace(',','').replace(':','')))) 
            TieredPrice=[]
            for text in S.find_all("td",class_="PriceBreakPrice"):
                text=text.get_text().replace(',','')
                if '$' not in text:
                    TieredNo.pop()
                    break
                TieredPrice.append(float(text.replace('$','')))                        
            PI['Tiered']=self.combine(TieredNo,TieredPrice) 
            S           =SC2.find("table",id="ctl00_ContentMain_availability_tbl1").td.get_text()
            Stock=list(filter(str.isdigit,S)) 
            PI['Stock']=[0,TieredNo[0]]
            if Stock:
                PI['Stock'] =[int("".join(Stock)),TieredNo[0]]
            PI['ID']=ID
            self.PI=PI
            return(PI)
        except AttributeError:
            print("...........%s............" % AttributeError)
            self.PI=0
            return 0

    def getFuture(self,ID):
        parse_only=SoupStrainer(id="product-prices")    
        try:
            SourceCode=BeautifulSoup(self.HtmlCode,"lxml", parse_only=parse_only)
            
            #SC1 the part of productdetail-box1
            PI={}
            #SC2 the part of price and quantity
            
            SC2            =SourceCode.find("div",id="product-prices-content").find("table",class_="product-prices")
            if SC2 is None:
                self.PI=0
                return 0
            #Price Tired
            TieredNo=[]
            TieredPrice=[]
            for text in SC2.find_all("tr",class_="price-break"):
                TN=text.th.get_text()
                print(TN)
                try:
                    No=re.search(r"\d+,*\d*",TN).group(0) 
                except AttributeError:
                    No=0
                TieredNo.append(int(No))
                TP=text.td.get_text()
                TieredPrice.append(float(TP.replace('$','')))                        
            PI['Tiered']=self.combine(TieredNo,TieredPrice) 
            S=SourceCode.find("div",id="product-qty-content").find("tr",class_="qtyInStock").get_text()
            Stock=list(filter(str.isdigit,S)) 
            PI['Stock']=[0,TieredNo[0]]
            if Stock:
                PI['Stock'] =[int("".join(Stock)),TieredNo[0]]
            PI['ID']=ID
            self.PI=PI
            return(PI)
        except AttributeError:
            print("...........%s............" % AttributeError)
            self.PI=0
            return 0

    def clear(self,text):
        text=text.replace('\r','')
        text=text.replace('\n','')
        text=text.replace('\t','')
        text=text.replace('  ','')
        return text

    def combine(self,number,price):
        tiered=[]
        for i in range(0,len(number)):
            temp=[]
            temp=[number[i],float('%.4f' % price[i])]
            tiered.append(temp)
        return tiered

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
    url="http://cn.mouser.com/ProductDetail/Aries/40-6518-10/?qs=sGAEpiMZZMs%2fSh%2fkjph1tvt1%2fmEPT%2fXoJGpdLEIRM8M%3d"
    a.toGetData(url,123,k=2)
    print(a.PI)




