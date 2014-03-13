#!/usr/bin/env python
# coding=utf-8
# File Name: ServerData.py
# Author: Bill Zhang
# Mail: zchcandid@gmail.com 
# Created Time: Thu 14 Nov 2013 03:00:42 PM CST
#python3 compatible
from __future__ import unicode_literals  
from __future__ import print_function 
#tornado server
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options
import tornado.gen
#import random
#json 
import json
import lib.libPush as libPush
define("port", default=8888, help="run on the given port", type=int)
class DisData(tornado.web.RequestHandler):
  #accept request from hqchip.com 
  #argument ?keyword=lm358&&k=1
  #json formate:{"item_id":"[1243,244]","priority":"1"}
  #异步
    def get(self):
       # self.write("Welcome to here!!")
        keyword= self.get_argument('keyword','nodata')
        k= self.get_argument('k','0')
        cb=self.get_argument("callback",'')
        if(keyword=='nodata'):
            self.write('something wrong!! nodata input!!!')
        if(k==0):
            self.write("NODE WRONG!!")
        html=libPush.getID(int(k),keyword)
        if html is 1:
            html={'status':1}
        html = json.dumps(html)
        html ="%s(%s)" % (str(cb),html)
        self.write(html)
if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=[(r"/", DisData)])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    print("The web service is runing")
    tornado.ioloop.IOLoop.instance().start()
