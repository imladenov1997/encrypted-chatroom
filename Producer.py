import datetime
import hashlib
import hmac
import threading

from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP


class Producer(threading.Thread):
    def __init__(self, client_name, channel, room_name, private_key):
        threading.Thread.__init__(self)
        self.client_name = client_name
        self.channel = channel
        self.exchange_name = hmac.new(private_key, room_name.encode(), hashlib.sha256).hexdigest()


    def run(self):

        recipient_key = RSA.import_key(open("keys/receiver.pem").read())
        session_key = get_random_bytes(16)

        # Encrypt the session key with the public RSA key
        cipher_rsa = PKCS1_OAEP.new(recipient_key)
        enc_session_key = cipher_rsa.encrypt(session_key)

        cipher_aes = AES.new(session_key, AES.MODE_EAX)

        initial_msg = self.client_name + " has just entered the room at " + str(datetime.datetime.utcnow())
        initial_msg = initial_msg.encode("utf-8")

        ciphertext, tag = cipher_aes.encrypt_and_digest(initial_msg)
        encoded = [x for x in (cipher_aes.nonce, tag, ciphertext, enc_session_key)]
        self.channel.basic_publish(exchange=self.exchange_name, routing_key='', body=str(encoded))

        while True:
            msg = self.client_name + ": " + input('')
            msg = msg.encode("utf-8")

            cipher_aes = AES.new(session_key, AES.MODE_EAX)
            ciphertext, tag = cipher_aes.encrypt_and_digest(msg)
            encoded = [x for x in (cipher_aes.nonce, tag, ciphertext, enc_session_key)]

            self.channel.basic_publish(exchange=self.exchange_name, routing_key='', body=str(encoded))