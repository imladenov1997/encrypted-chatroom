import threading
import ast

from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA


class Consumer(threading.Thread):
    def __init__(self, client_name, channel, queue_name):
        threading.Thread.__init__(self)
        self.client_name = client_name
        self.channel = channel
        self.queue_name = queue_name

    def run(self):
        self.channel.basic_consume(self.callback, queue=self.queue_name)
        self.channel.start_consuming()

    def callback(self, ch, method, properties, body):
        encoded = ast.literal_eval(body.decode("utf-8"))
        (cipher_aes_nonce, tag, ciphertext, enc_session_key) = encoded

        private_key = RSA.import_key(open("keys/key.pem").read())

        # Decrypt the session key with the public RSA key
        cipher_rsa = PKCS1_OAEP.new(private_key)
        session_key = cipher_rsa.decrypt(enc_session_key)

        # Decrypt the data with the AES session key
        cipher_aes = AES.new(session_key, AES.MODE_EAX, cipher_aes_nonce)
        data = cipher_aes.decrypt_and_verify(ciphertext, tag)

        msg = data.decode("utf-8")

        if not msg.split(":")[0] == self.client_name:
            print(msg)