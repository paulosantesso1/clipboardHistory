import globalPluginHandler
import tones
import wx
import gui
import api
import ui
import time
import threading

import addonHandler
addonHandler.initTranslation()

MAX_HISTORY = 50

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    def __init__(self):
        super().__init__()
        self.history = []
        self.lastContent = ""
        self.monitoring = True
        self.monitorThread = threading.Thread(target=self.monitorClipboard, daemon=True)
        self.monitorThread.start()
        ui.message(_("Histórico da área de transferência ativado"))

    def monitorClipboard(self):
        while self.monitoring:
            try:
                content = api.getClipData()
                if content and content != self.lastContent:
                    self.lastContent = content
                    if content not in self.history:
                        self.history.insert(0, content)
                        if len(self.history) > MAX_HISTORY:
                            self.history.pop()
            except:
                pass
            time.sleep(1)

    def script_showClipboardHistory(self, gesture):
        if not self.history:
            ui.message(_("Histórico vazio."))
            return

        def show():
            dlg = ClipboardDialog(self.history)
            dlg.ShowModal()
            dlg.Destroy()

        wx.CallAfter(show)

    __gestures = {
        "kb:NVDA+shift+v": "showClipboardHistory"
    }

class ClipboardDialog(wx.Dialog):
    def __init__(self, history):
        super().__init__(gui.mainFrame, title=_("Histórico da Área de Transferência"), size=(600, 400))
        self.history = history

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.listBox = wx.ListBox(panel, choices=history, style=wx.LB_SINGLE)
        sizer.Add(self.listBox, 1, wx.EXPAND | wx.ALL, 10)

        self.Bind(wx.EVT_LISTBOX_DCLICK, self.onSelect, self.listBox)
        self.Bind(wx.EVT_CHAR_HOOK, self.onKeyPress)

        panel.SetSizer(sizer)

    def onSelect(self, event):
        self.copySelected()

    def onKeyPress(self, event):
        if event.GetKeyCode() == wx.WXK_RETURN:
            self.copySelected()
        else:
            event.Skip()

    def copySelected(self):
        index = self.listBox.GetSelection()
        if index != wx.NOT_FOUND:
            selected = self.history[index]
            api.copyToClip(selected)
            ui.message(_("Item copiado para a área de transferência."))
            self.Close()
