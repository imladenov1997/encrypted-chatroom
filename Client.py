import datetime
import hashlib
import hmac
import random
import string
import threading
import pika
import sys

from Consumer import Consumer
from Producer import Producer


class Client():
    def __init__(self, address):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(address))
        self.channel = self.connection.channel()

    def run(self):
        roomName = input('Please enter the name of the room: \n')
        clientName = input('Please enter the name of the client: \n')
        privateKey = bytearray(123)
        res = self.enterRoom(roomName, clientName, privateKey)

        if (res):
            print('Entered')
            self.consumer = Consumer(clientName, self.channel, self.queue_name)
            self.consumer.start()
            self.producer = Producer(clientName, self.channel, roomName, privateKey)
            self.producer.start()


    def enterRoom(self, room_name, name, privateKey):
        # Hash the room name and client name with private key
        room_name = hmac.new(privateKey, room_name.encode(), hashlib.sha256).hexdigest()
        name = hmac.new(privateKey, name.encode(), hashlib.sha256).hexdigest()

        # Generate a random unique key for the queue name
        unique_key = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(64))

        # set queue names
        self.queue_name = room_name + ":" + name
        self.exchange = self.channel.exchange_declare(exchange=room_name, exchange_type='fanout')
        self.queue = self.channel.queue_declare(queue=self.queue_name)
        self.channel.queue_bind(exchange=room_name, queue=self.queue_name)
        return True

address = sys.argv[1]
cl = Client(address)
cl.run()