from threading import Thread
from typing import Union
import wx

from enrypter import Encrypter, Language

EVT_RESULT_ID = wx.NewIdRef(count=1)


class EncrypterThread(Thread):
    def __init__(self,
                 notify_window,
                 lang: Language,
                 text: str,
                 encrypt: bool,
                 key: int):
        Thread.__init__(self)
        self._notify_window = notify_window
        self._encrypter = Encrypter(lang)
        self._text = text
        self._encrypt = encrypt
        self._key = key

        # don't wait for thread to finish on app terminatino
        self.setDaemon(True)

    def run(self):
        try:
            result = None
            if (self._encrypt):
                result = self._encrypter.encrypt(self._text, self._key)
            else:
                result = self._encrypter.decrypt(self._text, self._key)
            wx.PostEvent(self._notify_window, ResultEvent(result))
        except Exception as e:
            print(e)
            wx.PostEvent(self._notify_window,
                         ResultEvent(
                            None,
                            'failed to process data')
                         )


class ResultEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""
    def __init__(self,
                 data: Union[str, None],
                 error_message: str = ''):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data
        self.error_message = error_message
