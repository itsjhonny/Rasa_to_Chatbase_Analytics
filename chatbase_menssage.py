import json
import requests
import time


class ChatBaseMessage(object):
    """Base Message.
    Define attributes present on all variants of the Message Class.
    """

    def __init__(self,
                 api_key="",
                 platform="",
                 message="",
                 intent="",
                 version="",
                 user_id="",
                 type=None,
                 not_handled=False,
                 time_stamp=None):
        self.api_key = api_key
        self.platform = platform
        self.message = message
        self.intent = intent
        self.version = version
        self.user_id = user_id
        self.not_handled = not_handled
        self.feedback = False
        self.time_stamp = time_stamp
        self.type = type

    @staticmethod
    def get_current_timestamp():
        """Returns the current epoch with MS precision."""
        return int(round(time.time() * 1e3))

    @staticmethod
    def get_content_type():
        """Returns the content-type for requesting against the Chatbase API"""
        return {'Content-type': 'application/json', 'Accept': 'text/plain'}

    def to_json(self):
        """Return a JSON version for use with the Chatbase API"""
        return json.dumps(self, default=lambda i: i.__dict__)

    def send(self):
        """Send the message to the Chatbase API."""
        url = "https://chatbase.com/api/message"

        return requests.post(url,
                             data=self.to_json(),
                             headers=ChatBaseMessage.get_content_type())
