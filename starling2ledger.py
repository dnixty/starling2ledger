#!/usr/bin/env python3

import wx
import os
import csv
import datetime
import re

class ConverterPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        text_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.csv_ctrl = wx.TextCtrl(self, 1, style=wx.TE_MULTILINE)
        self.ldg_ctrl = wx.TextCtrl(self, 2, style=wx.TE_MULTILINE | wx.TE_READONLY)
        text_sizer.Add(self.csv_ctrl, 1, wx.ALL | wx.EXPAND, 1)
        text_sizer.Add(self.ldg_ctrl, 1, wx.ALL | wx.EXPAND, 1)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        openButton = wx.Button(self, label = "Open")
        openButton.Bind(wx.EVT_BUTTON, self.on_open)
        convertButton = wx.Button(self, label = "Convert")
        convertButton.Bind(wx.EVT_BUTTON, self.on_convert)
        button_sizer.Add(openButton, 1, wx.ALL)
        button_sizer.Add(convertButton, 1, wx.ALL)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(text_sizer, 1, wx.ALL | wx.EXPAND, 5)
        main_sizer.Add(button_sizer, 0, wx.ALL | wx.CENTER, 5)

        self.SetSizer(main_sizer)


    def load_csv(self, path):
        filehandle = open(path, 'r')
        self.csv_ctrl.SetValue(filehandle.read())
        filehandle.close()

    def on_open(self, event):
        title = "Choose a csv file:"
        dlg = wx.FileDialog(self, title, wildcard="*.csv")
        if dlg.ShowModal() == wx.ID_OK:
            self.load_csv(dlg.GetPath())
        dlg.Destroy()

    def on_convert(self, e):
        data = self.csv_ctrl.GetValue()
        output = Parser().parse(data)
        self.ldg_ctrl.SetValue(output)


class ConverterFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Starling CSV converter', size=(800, 600))
        self.panel = ConverterPanel(self)
        self.create_menu()
        self.Show()

    def create_menu(self):
        menu_bar = wx.MenuBar()
        file_menu = wx.Menu()
        open_menu_item = file_menu.Append(
            wx.ID_ANY, 'Open',
            'Open a csv file to convert'
        )
        menu_bar.Append(file_menu, '&File')
        self.Bind(
            event=wx.EVT_MENU,
            handler=self.panel.on_open,
            source=open_menu_item,
        )
        self.SetMenuBar(menu_bar)


class Parser():
    def parse_datetime(self, date_time_str):
        """
        Parses datetime string in 01-01-2000 format.
        """
        try:
            date_time_obj = datetime.datetime.strptime(date_time_str, "%d/%m/%Y")
        except ValueError as error:
            print(error)
        return date_time_obj.date()


    def parse(self, raw_data):
        output = ""
        csv_reader = csv.reader(raw_data.splitlines())
        next(csv_reader, None)
        for row in csv_reader:
            if row[0] == "":
                continue
            date = self.parse_datetime(row[0]).strftime("%Y/%m/%d")
            payee = row[1]
            description = re.sub("\s\s+", " ", row[2])
            amount = row[4]
            output += "{} {}\n".format(date, payee)
            if (float(amount) >= 0):
                output += "  Assets:Monzo:Checking  £{}\n".format(amount)
                output += "  X:X\n"
            else:
                output += "  Expenses:X  £{}\n".format(amount[1:])
                output += "  Assets:Monzo:Checking\n"
            output += "  ;; Reference: {}\n\n".format(description)
        return output


if __name__ == '__main__':
    app = wx.App(False)
    frame = ConverterFrame()
    app.MainLoop()
