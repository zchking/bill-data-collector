#!/usr/bin/env python
# coding=utf-8
#	> Author: Bill Zhang
#	> Mail: zchcandid@gmail.com 
#	> Created Time: Fri 07 Mar 2014 12:08:25 AM PST
import simplejson as json
import lib.getWeb as getWeb
import pymongo
import time
from lib.set_rpc import UpdateRpcClient

def getID(k=0,keyword=0):
    url="http://ic.elecfans.net/Search_supplier?k=%s&keyword=%s" % (k,keyword)
    r=getWeb.get(url)
    if r.status_code is not 200:
        return 1
    jIDs=json.loads(r.text)
    if jIDs["status"] is -1:
        return 1
    #combine the json data front need
    PA={}
    PIA=[]
    if k==2:
        PA['PUrl']="http://cn.mouser.com"
        PA['PIUrl']="/Public/img/proxy/mouser.gif" 
        PA['status']=0
    elif k==3:
        PA['PUrl']="http://www.digikey.cn"
        PA['PIUrl']="/Public/img/proxy/digikey.gif" 
        PA['status']=0
    elif k==4:
        PA['PUrl']="http://www.future.com"
        PA['PIUrl']="/Public/img/proxy/future.gif" 
        PA['status']=0
    else:
        return 1
    IDs=jIDs['id']
    print(IDs)
    allData=getData(IDs,k)
    for data in allData:
        data['_id']=k
        if (int(time.time())-data['time'])>172800:
        # 过期，下达更新任务
            print("get here again")
            setUpdate=UpdateRpcClient()
            url={"ID":data['GoodsId'],"URL":data['url'],"k":k}
            url=json.dumps(url)
            newData=setUpdate.get_data(url)
            newData=json.loads(newData)
            if newData==0:
                continue
            data['Tiered']=newData['Tiered']
            data['Stock']=newData['Stock']
        T=combine(data["Tiered"])
        if T==-1:
            continue
        data["Tiered"]=T
        PIA.append(data)
    PA["PD"]=PIA
    return PA

def getData(IDs=0,k=0):
    uri="mongodb://hqjf:aa88OO00@172.168.16.104/hqchip"
    try:
        con=pymongo.MongoClient(uri)
        db=con.hqchip
        if k==2:
            data=db.mouser.find({"GoodsId":{"$in":IDs}})
        elif k==3:
            data=db.digikey.find({"GoodsId":{"$in":IDs}})
        elif k==4:
            data=db.future.find({"GoodsId":{"$in":IDs}})
        else:
            data=db.test.find_one()
            print(data)
        return data
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
def combine(tiered):
    if not tiered:
        return -1
    T=[]
    for i in tiered:
        temp=[]
        price=float(i[1])
        temp=[i[0],float('%.4f' % price),float('%.4f' % (price*1.05)),float('%.4f' % (price*7.6))]
        T.append(temp)
    return T
if __name__=="__main__":
    getID()

