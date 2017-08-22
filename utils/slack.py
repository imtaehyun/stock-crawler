from slacker import Slacker

from utils.config import Config


class Slack:
    class __Slack:
        def __init__(self):
            config = Config()
            self.slack = Slacker(config.slack.get('token', ''))

    instance = None

    def __init__(self):
        if not Slack.instance:
            Slack.instance = Slack.__Slack()

    def send_message(self, msg, channel="#general"):
        self.instance.slack.chat.post_message(channel, msg)


if __name__ == '__main__':
    slack = Slack()
    slack.send_message('test')
