#!/usr/bin/ python3
# coding=utf-8                                  
# File Name: rpc_client.py                      
# Author: Bill Zhang                            
# Mail: zchcandid@gmail.com                     
# Created Time: Sat 08 Mar 2014 06:15:42 AM CST
import pika
import simplejson as json
from libUpdate import UpdateClass
import pymongo
import time
def mUpdate(r,k,id):
    T=0
    S=0
    if r is not 0:
        T=r["Tiered"]
        S=r["Stock"]
        
    uri="mongodb://hqjf:aa88OO00@172.168.16.104/hqchip"
    if r==0:
        return -1
    try:
        con=pymongo.MongoClient(uri)
        db=con.hqchip
        if k==2:
            data=db.mouser.update({"GoodsId":id},{"$set":{"Tiered":T,"Stock":S,"time":int(time.time())}})
        elif k==3:
            data=db.digikey.update({"GoodsId":id},{"$set":{"Tiered":T,"Stock":S,"time":int(time.time())}})
        elif k==4:
            data=db.future.update({"GoodsId":id},{"$set":{"Tiered":T,"Stock":S,"time":int(time.time())}})
        else:
            data=db.test.update({"GoodsId":id},{"$set":{"Tired":T,"Stock":S,"time":int(time.time())}})
        return 0 
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
    pass
connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='172.168.16.102'))

channel = connection.channel()

channel.queue_declare(queue='rpc_queue')
"""
to_update is for get the URL and update the price and quantity
the return value is the json data

"""
UC=UpdateClass()
def on_request(ch, method, props, body):
    body=body.decode('utf-8')
    IU=json.loads(body)
    print(IU)
  #  ch.basic_ack(delivery_tag = method.delivery_tag)
  #  return
    url=IU["URL"].replace("www.mouser.cn","cn.mouser.com")
    k=IU["k"]
    id=IU["ID"]
    print (" [.] ID(%s)"  % (id,))
    response =UC.toGetData(ID=id,url=url,k=k)
    print(response) 
    mUpdate(response,k,id)
    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body=json.dumps(response))
    ch.basic_ack(delivery_tag = method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(on_request, queue='rpc_queue')

print (" [x] Awaiting RPC requests to update the hqchip data!")
channel.start_consuming()

