# -*- coding: utf-8 -*-
import socketserver
import time
import re
import json
clients = {}
connections = []
logger = []
#-------------------------------------------------------------------------------
def getTime():
    return time.strftime("%H:%M:%S", time.localtime())
#-------------------------------------------------------------------------------
def broadcast(payload):
    global connections
    payload = json.dumps(payload)
    for connection in connections:
        connection.send(payload.encode())
#-------------------------------------------------------------------------------
def send(DICT_payload, connection):
    payload = json.dumps(DICT_payload)
    connection.send(payload.encode())
#-------------------------------------------------------------------------------
def not_logged_in(port):
    global clients
    if (port in clients):
        return False
    else:
        return True
#-------------------------------------------------------------------------------
def login(received_data, port, connection):
    global clients
    global connections
    global logger
    # Lager log først logger
    log = {
                'timestamp': getTime(),
                'sender': "server",
                'response': "history",
                'content': logger
    }

    # Lager pakke til login
    response = {
                'timestamp': getTime(),
                'sender': "server",
                'response': "error",
                'content': None
    }
    username = received_data['content']
    # Sjekker om username er gyldig:
    if (re.match("^[A-Za-z0-9]+$", username)):
        # Sjekker at username ikke er opptatt:
        if (username not in clients.values()):
            clients[port] = username
            response['response'] = "info"
            response['content'] = "Login successful"
            # Sender derfor log:
            send(log, connection)
        else:
            response['content'] = "Username is already taken"
    else:
        response['content'] = "Invalid username"
    # response pakken er laget, og skal nå sendes:
    send(response, connection)

    # Nødvendig timeout så ikke pakker kommer for fort til MessageReceiver
    time.sleep(0.05)

    # Broadcaster hvis login successful:
    if (response['response'] != 'error'):
        response = {
                    'timestamp': getTime(),
                    'sender': "server",
                    'response': "message",
                    'content': username + " has logged in!"
        }
        #logger.append(json.dumps(response))
        broadcast(response)
#-------------------------------------------------------------------------------
def logout(received_data, port, connection):
    global clients
    # Bekreftelse på logout
    response = {
                'timestamp': getTime(),
                'sender': "server",
                'response': "info",
                'content': "Logout successful"
    }
    send(response, connection)
    # Broadcaster logout
    response = {
                'timestamp': getTime(),
                'sender': "server",
                'response': "message",
                'content': clients[port] + " has logged out..."
    }
    broadcast(response)

#-------------------------------------------------------------------------------
def names(received_data, port, connection):
    global clients
    allNames = "Connected users: "
    for username in clients.values():
        allNames += username + ", "
    response = {
                'timestamp': getTime(),
                'sender': "server",
                'response': "info",
                'content': allNames
    }
    send(response, connection)
#-------------------------------------------------------------------------------
def help(received_data, port, connection):
    response = {
                'timestamp': getTime(),
                'sender': "server",
                'response': "info",
                'content': """help:
Possible requests (type in request and hit 'ENTER'):
- login (content = <username>)
- logout
- names (lists all connected users)
- (Just type in wanted message)
PS: You need to be logged in before other requests become available"""
    }
    send(response, connection)
#-------------------------------------------------------------------------------
def msg(received_data, port, connection):
    global clients
    response = {
                'timestamp': getTime(),
                'sender': clients[port],
                'response': "message",
                'content': received_data['content']
    }
    logger.append(json.dumps(response))
    broadcast(response)
#-------------------------------------------------------------------------------
def unknown_request(connection):
    response = {
                'timestamp': getTime(),
                'sender': "server",
                'response': "error",
                'content': "Unknown request"
    }
    send(response, connection)
#-------------------------------------------------------------------------------
def disconnect(connection, port):
    global clients
    global connections
    print(str(port) + " disconnected")
    del clients[port]
    connections.remove(connection)
    connection.close()
#-------------------------------------------------------------------------------
"""
Variables and functions that must be used by all the ClientHandler objects
must be written here (e.g. a dictionary for connected clients)
"""

class ClientHandler(socketserver.BaseRequestHandler):
    """
    This is the ClientHandler class. Everytime a new client connects to the
    server, a new ClientHandler object will be created. This class represents
    only connected clients, and not the server itself. If you want to write
    logic for the server, you must write it outside this class
    """
    global clients
    global connections
    global logger

    def handle(self):
        global clients
        global connections
        global logger
        """
        This method handles the connection between a client and the server.
        """
        self.ip = self.client_address[0]
        self.port = self.client_address[1]
        self.connection = self.request
        self.run = True

        connections.append(self.connection)
        print(str(self.port) + " connected")

        # Loop that listens for messages from the client
        while self.run:
            try:
                received_string = self.connection.recv(4096).decode()
                print(received_string)
                received_data = json.loads(received_string)
                # TODO: Add handling of received payload from client
                # Må logge inn først:
                if ( not_logged_in(self.port) ):
                    if (received_data['request'] == 'login'):
                        login(received_data, self.port, self.connection)
                    elif (received_data['request'] == 'help'):
                        help(received_data, self.port, self.connection)
                    else: # Hvis man prøver på annet uten å ha logget inn:
                        response = {
                                    'timestamp': getTime(),
                                    'sender': "server",
                                    'response': "error",
                                    'content': "Only login or help allowed!"
                        }
                        send(response, self.connection)
                else: # Hvis man er logget inn:
                    if (received_data['request'] == 'msg'):
                        msg(received_data, self.port, self.connection)
                    elif (received_data['request'] == 'names'):
                        names(received_data, self.port, self.connection)
                    elif (received_data['request'] == 'help'):
                        help(received_data, self.port, self.connection)
                    elif (received_data['request'] == 'logout'):
                        logout(received_data, self.port, self.connection)
                        self.run = False
                        disconnect(self.connection, self.port)
                    else:
                        unknown_request(self.connection)
            except Exception as e: # Terminate clientHandler if ctrl+C:
                self.run = False
                disconnect(self.connection, self.port)

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """
    This class is present so that each client connected will be ran as a own
    thread. In that way, all clients will be served by the server.

    No alterations are necessary
    """
    allow_reuse_address = True

if __name__ == "__main__":
    """
    This is the main method and is executed when you type "python Server.py"
    in your terminal.

    No alterations are necessary
    """
    HOST, PORT = 'localhost', 9998
    print ('Server running...')

    # Set up and initiate the TCP server
    server = ThreadedTCPServer((HOST, PORT), ClientHandler)
    server.serve_forever()
