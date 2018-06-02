# encrypted-chatroom
Chatroom implementing RabbitMQ and RSA Encryption

This application uses RabbitMQ implementation in the following way: 

Clients are connected to a specific server that runs RabbitMQ application. Each client is a Consumer and a Producer and has its own Queue.

Queues store messages from other clients in the same chatroom. One queue is required per one client in one chatroom. For instance, 
if a client wants to join 2 chatrooms, it is perfectly possible as this client will have two queues, one for each chatroom. 

When clients send messages they act as Producers and send their message to each client's queue related to this chatroom. When clients 
receive messages, they act as Consumers on their own queues. 

The idea behind such a chatroom is to decouple multiple clients and enable them to view messages even if they are not connected at the moment messages are sent to them.

In order to improve security, an RSA encryption is used for all messages. A user needs to have public and private keys of the room (which 
are actually stored in two files). This ensures that conversation remains encrypted and cannot be seen by anyone who joins the chatroom accidentally. 
