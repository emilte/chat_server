# -*- coding: utf-8 -*-
from threading import Thread

class MessageReceiver(Thread):
    """
    This is the message receiver class. The class inherits Thread, something that
    is necessary to make the MessageReceiver start a new thread, and it allows
    the chat client to both send and receive messages at the same time
    """

    def __init__(self, client, connection):
        """
        This method is executed when creating a new MessageReceiver object
        """
        Thread.__init__(self)
        # Flag to run thread as a deamon
        self.daemon = True
        # TODO: Finish initialization of MessageReceiver
        self.connection = connection
        self.client = client
        self.thread = Thread(target=self.client, args=(self.connection), daemon=self.daemon)
        self.running = True

    def stop():
        self.running = False

    def run(self):
        # TODO: Make MessageReceiver receive and handle payloads
        while self.running:
            try:
                payload, serverAddress = self.connection.recvfrom(32768)
                payload = payload.decode()
                self.client.receive_message(payload)
            except:
                # socket timeout:
                pass
