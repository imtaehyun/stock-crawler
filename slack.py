import os
from slacker import Slacker

slack_token = os.environ.get('SLACK_API_TOKEN', '')
slack = Slacker(slack_token)

def send_message(msg, channel="#general"):
    slack.chat.post_message(channel, msg)
