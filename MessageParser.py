import json

class MessageParser():

    def __init__(self):
        self.possible_responses = {
            'error': self.parse_error,
            'info': self.parse_info,
            'message': self.parse_message,
            'history': self.parse_history,
	    # More key:values pairs are needed
        }

    def parse(self, payload):
        # decode the JSON object
        payload = json.loads(payload)

        if payload['response'] in self.possible_responses:
            return self.possible_responses[payload['response']] (payload)

    def parse_error(self, payload):
        error_string = ""
        error_string += "(" + payload['timestamp'] + ") "
        error_string += payload['sender'] + ": "
        error_string += payload['content']
        return error_string

    def parse_info(self, payload):
        info_string = ""
        info_string += "(" + payload['timestamp'] + ") "
        info_string += payload['sender'] + ": "
        info_string += payload['content']
        return info_string

    def parse_message(self, payload):
        message_string = "\n"
        message_string += "(" + payload['timestamp'] + ") "
        message_string += payload['sender'] + ": "
        message_string += payload['content']
        return message_string + "\n"

    def parse_history(self, payload):
        logger = payload['content']
        if (logger == []):
            return ""

        history_string = "\n"
        history_string += "(" + payload['timestamp'] + ") "
        history_string += payload['sender'] + ": "
        history_string += "History:"


        for msgPayload in logger:
            msgPayload = json.loads(msgPayload)
            time = msgPayload['timestamp']
            sender = msgPayload['sender']
            msg = msgPayload['content']
            history_string += "\n"
            history_string += "- (" + time + ") "
            history_string += sender + ": "
            history_string += msg

        return history_string + "\n"
