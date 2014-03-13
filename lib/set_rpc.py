#!/usr/bin/ python3
# coding=utf-8                                  
# File Name: rpc_client.py                      
# Author: Bill Zhang                            
# Mail: zchcandid@gmail.com                     
# Created Time: Sat 08 Mar 2014 06:15:42 AM CST
import pika
import uuid
class UpdateRpcClient(object):
    """
    This class is for distribute the data to update!
    Function:
    get_data(id)--push id and get the new data

    """
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                host='172.168.16.102'))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def get_data(self, id):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                                   routing_key='rpc_queue',
                                   properties=pika.BasicProperties(
                                         reply_to = self.callback_queue,
                                         correlation_id = self.corr_id,
                                         ),
                                   body=str(id))
        while self.response is None:
            self.connection.process_data_events()
        return self.response

if __name__=="__main__":
	update_rpc = UpdateRpcClient()
	print (" [x] Requesting fib(30)")
	response = update_rpc.get_data(30)
	print (" [.] Got %r" % (response,))
