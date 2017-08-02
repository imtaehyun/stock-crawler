import os
from slackclient import SlackClient

slack_token = os.environ["SLACK_API_TOKEN"]
sc = SlackClient(slack_token)


def send_message(msg, channel="#general"):
    sc.api_call(
        "chat.postMessage",
        channel=channel,
        text=msg
    )