#!/usr/bin/env python
# coding=utf-8
#	> Author: Bill Zhang
#	> Mail: zchcandid@gmail.com 
#	> Created Time: Thu 06 Mar 2014 06:54:54 PM PST

# test.py
def application(env, start_response):
        start_response('200 OK', [('Content-Type','text/html')])
        return b"Hello World"
