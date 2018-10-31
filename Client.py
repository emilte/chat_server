# -*- coding: utf-8 -*-
import socket
from MessageReceiver import MessageReceiver
from MessageParser import MessageParser
import json
import time

class Client:
    """
    This is the chat client class
    """

    def __init__(self, host, server_port):
        "This method is run when creating a new Client object"
        # Set up the socket connection to the server
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.settimeout(0.1)
        # TODO: Finish init process with necessary code
        self.host = host
        self.server_port = server_port
        self.MessageParser = MessageParser()
        self.disconnected = False
        self.run()

    def run(self):
        # Initiate the connection to the server
        self.connection.connect( (self.host, self.server_port) )
        self.MessageReceiver = MessageReceiver(self, self.connection)
        self.MessageReceiver.start()

        while not self.disconnected:
            # Lager tom pakke som skal sendes til server:
            self.data = {'request': None, 'content': None}

            # Henter request fra bruker:
            self.request = input(" > ")
            if (self.request == ""):
                continue

            elif (self.request == "login"):
                self.data['request'] = self.request
                self.data['content'] = input("username: ")

            elif (self.request in ["names", "logout", "help"]):
                self.data['request'] = self.request

            else: #Bare vanlig msg:
                self.data['request'] = "msg"
                self.data['content'] = self.request

            # Gjør om pakken til JSON:
            self.data_json = json.dumps(self.data)
            # Sender pakken til serveren:
            self.connection.send(self.data_json.encode())
            # Sleep så man rekker å disconnecte
            time.sleep(0.5)

    def disconnect(self):
        self.disconnected = True
        MessageReceiver.stop()
        self.connection.close()

    def receive_message(self, message):
        self.payload = message

        self.data_string = self.MessageParser.parse(self.payload)
        print(self.data_string)

        message = json.loads(message)
        if ("Logout successful" == message['content'] and "info" == message['response']):
            self.disconnect()

if __name__ == '__main__':
    """
    This is the main method and is executed when you type "python Client.py"
    in your terminal.

    No alterations are necessary
    """
    # Min ntnu.no IP: 129.241.150.216   9998
    # Halvor: 129.241.222.168   9994)
    client = Client('localhost', 9998)
