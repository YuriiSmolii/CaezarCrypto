import wx
import os

from encrypterThread import EVT_RESULT_ID, EncrypterThread, ResultEvent
from enrypter import Language
from validator import DigitOnlyValidator

wildcard = "Text files (*.txt)|*.txt|" \
           "Encrypted files (*.enc)|*.enc|"


def EVT_RESULT(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_RESULT_ID, func)


class MainFrame(wx.Frame):
    def __init__(self, text_content='', enable_encrypt=True):
        super().__init__(parent=None, title='Cryptography')

        self._configure_menubar(enable_encrypt)

        self.status = self.CreateStatusBar(1)
        self.worker = None
        self.selected_path = None

        # textbox to display file content
        self.text_box = wx.TextCtrl(self, wx.ID_ANY, text_content, size=(-1, -1), style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.key_box = wx.TextCtrl(self, validator=DigitOnlyValidator())
        self.key_box.SetHint('encryption key (int)')

        # vertical container for textbox
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.text_box, 10, wx.EXPAND | wx.ALL, border=0)
        vbox.Add(self.key_box, 1, wx.EXPAND, border=0)

        self.SetSizerAndFit(vbox)

        self.Centre()

        # Set up event handler for any worker thread results
        EVT_RESULT(self, self.OnResult)

    def OnQuit(self, e):
        self.Close()

    def OnResult(self, event: ResultEvent):
        """Show Result status."""
        if event.data is None:
            # Thread aborted (using our convention of None return)
            self.status.SetStatusText(event.error_message, 0)
        else:
            # Process results here
            frame = MainFrame(text_content=event.data, enable_encrypt=False)
            frame.Show()
        # In either event, the worker is done
        self.worker = None

    def OnPrint(self, e):
        data = wx.PrintDialogData()
        data.EnableSelection(True)
        data.EnablePrintToFile(True)
        data.EnablePageNumbers(True)

        with wx.PrintDialog(self, data) as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                data = dialog.GetPrintDialogData()
                print('GetAllPages: %d\n' % data.GetAllPages())
                # todo: implement printing

    def OnOpenFile(self, e):
        self.DoOpenFile()

    def DoOpenFile(self):
        with wx.FileDialog(self,
                           message="Choose a file",
                           defaultDir=os.getcwd(),
                           defaultFile="",
                           wildcard=wildcard,
                           style=wx.FD_OPEN |
                           wx.FD_CHANGE_DIR |
                           wx.FD_FILE_MUST_EXIST |
                           wx.FD_PREVIEW) as open_dlg:

            if open_dlg.ShowModal() == wx.ID_OK:
                path = open_dlg.GetPath()

                try:
                    with open(path, 'r') as file:
                        text = file.read()
                        if self.text_box.GetLastPosition():
                            self.text_box.Clear()
                        self.text_box.WriteText(text)
                        self.selected_path = path

                except IOError as error:
                    dlg = wx.MessageDialog(self, 'Error opening file\n' + str(error))
                    dlg.ShowModal()

                except UnicodeDecodeError as error:
                    dlg = wx.MessageDialog(self, 'Error opening file\n' + str(error))
                    dlg.ShowModal()

        open_dlg.Destroy()

    def OnAbout(self, event):
        with wx.MessageDialog(self,
                               '\tEditor\t\n'\
                               '\n'\
                               'Another Tutorial\n'\
                               'Jan Bodnar 2005-2006\n'\
                               'Updated by Ecco 2020.',
                               'About Editor',
                               wx.OK |
                               wx.ICON_INFORMATION) as dlg:
            dlg.ShowModal()

    def EncryptUa(self, e):
        self.Encrypt(Language.UKRAINIAN)

    def EncryptEn(self, e):
        self.Encrypt(Language.ENGLISH)

    def DecryptUa(self, e):
        self.Decrypt(Language.UKRAINIAN)

    def DecryptEn(self, e):
        self.Decrypt(Language.ENGLISH)

    def Encrypt(self, lang: Language):
        if not self.text_box.LastPosition:
            wx.MessageBox(message='You need to open a file to encrypt!')
            return

        if not self.key_box.LastPosition:
            wx.MessageBox(message='You need to specify encryption key')
            return

        if self.worker:
            wx.MessageBox(message='There is an operation in progress, wait for it to finish')
            return

        self.worker = EncrypterThread(self, lang=lang, text=self.text_box.GetValue(), key=int(self.key_box.GetValue()), encrypt=True)
        self.worker.start()

    def Decrypt(self, lang: Language):
        if not self.text_box.LastPosition:
            wx.MessageBox(message='You need to open a file to encrypt!')
            return

        if not self.key_box.LastPosition:
            wx.MessageBox(message='You need to specify encryption key')
            return

        if self.worker:
            wx.MessageBox(message='There is an operation in progress, wait for it to finish')
            return

        self.worker = EncrypterThread(self, lang=lang, text=self.text_box.GetValue(), key=int(self.key_box.GetValue()), encrypt=False)
        self.worker.start()

    def _configure_menubar(self, enable_encrypt: bool):
        file_menu = wx.Menu()
        # todo? do we even need this
        new_item = file_menu.Append(wx.ID_ANY, '&New\tCtrl+N', 'Creates a new document.')
        open_item = file_menu.Append(wx.ID_ANY, '&Open\tCtrl+O', 'Open an existing file.')
        print_item = file_menu.Append(wx.ID_ANY, '&Print\tCtrl+p', 'Print a file')
        file_menu.AppendSeparator()
        quit_item = file_menu.Append(wx.ID_ANY, item='Exit', helpString='Exit application')

        encrypt_decrypt_menu = wx.Menu()
        encrypt_ua_item = encrypt_decrypt_menu.Append(
            wx.ID_ANY,
            item='Encrypt ukrainian',
            helpString='Encrypt file in ukrainian language')
        encrypt_en_item = encrypt_decrypt_menu.Append(wx.ID_ANY, item='Encrypt english', helpString='Encrypt file in english language')
        decrypt_ua_item = encrypt_decrypt_menu.Append(
            wx.ID_ANY,
            item='Decrypt ukrainian',
            helpString='Decrypt file in ukrainian language')
        decrypt_en_item = encrypt_decrypt_menu.Append(wx.ID_ANY, item='Decrypt english', helpString='Decrypt file in english language')

        about_menu = wx.Menu()
        about_item = about_menu.Append(wx.ID_ANY, item='About', helpString='About')

        menubar = wx.MenuBar()
        menubar.Append(file_menu, '&File')
        if (enable_encrypt):
            menubar.Append(encrypt_decrypt_menu, '&Encrypt/Decrypt')
        menubar.Append(about_menu, '&About')

        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.OnQuit, quit_item)
        self.Bind(wx.EVT_MENU, self.OnOpenFile, open_item)
        self.Bind(wx.EVT_MENU, self.OnAbout, about_item)
        self.Bind(wx.EVT_MENU, self.OnPrint, print_item)
        self.Bind(wx.EVT_MENU, self.EncryptUa, encrypt_ua_item)
        self.Bind(wx.EVT_MENU, self.EncryptEn, encrypt_en_item)
        self.Bind(wx.EVT_MENU, self.DecryptUa, decrypt_ua_item)
        self.Bind(wx.EVT_MENU, self.DecryptEn, decrypt_en_item)
