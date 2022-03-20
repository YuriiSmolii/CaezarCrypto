import wx


class DigitOnlyValidator(wx.Validator):
    def __init__(self):
        wx.Validator.__init__(self)
        self.Bind(wx.EVT_CHAR, self.OnChar)

    """
    Note that every validator must implement the Clone() method.
    """
    def Clone(self):
        return DigitOnlyValidator()

    def Validate(self, win):
        return True

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True

    def OnChar(self, evt):
        key = chr(evt.GetKeyCode())
        if key.isdigit():
            evt.Skip()
            return
