import logging


class Logger:
    class __Logger:
        def __init__(self):
            self._logger = logging.getLogger()
            self._logger.setLevel(logging.INFO)
            formatter = logging.Formatter(
                '[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s')

            streamHandler = logging.StreamHandler()
            streamHandler.setFormatter(formatter)
            self._logger.addHandler(streamHandler)

    instance = None

    def __init__(self):
        if not Logger.instance:
            Logger.instance = Logger.__Logger()

    def get_logger(self):
        return self.instance._logger
