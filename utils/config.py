import os


class Config:
    class __Config:
        def __init__(self):
            self.slack = {'token': os.environ.get('SLACK_API_TOKEN', '')}

    instance = None

    def __init__(self):
        if not Config.instance:
            Config.instance = Config.__Config()

    def __getattr__(self, name):
        return getattr(self.instance, name)