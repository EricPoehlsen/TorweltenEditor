# coding=utf-8
import xml.etree.ElementTree as et
import tkinter as tk
import config
import re

msg = config.Messages()

class Improve(tk.Toplevel):
    def __init__(self,app):
        tk.Toplevel.__init__(self)
        self.app = app
        self.char = app.char

        # tk variables ... 
        self.xp_var = tk.IntVar()
        self.event_name = tk.StringVar()
        self.money_amount = tk.StringVar()
        self.selected_account = tk.StringVar()

        # build screen
        self.title(msg.IW_TITLE)

        # event name
        self.event_frame = tk.LabelFrame(self, 
                                         text = msg.IW_EVENT)
        self.event_text = tk.Entry(self.event_frame, 
                                   textvariable = self.event_name, 
                                   width = 50)
        self.event_text.pack(fill = tk.X)
        self.event_frame.pack(fill = tk.X)

        # xp frame
        self.xp_frame = tk.LabelFrame(self, 
                                      text=msg.IW_XP)
        self.xp_spinbox = tk.Spinbox(self.xp_frame, 
                                     textvariable=self.xp_var, 
                                     from_=-100, to=100, 
                                     width=4,
                                     font="Arial 12 bold")
        self.xp_spinbox.pack(fill = tk.X)
        self.xp_frame.pack(fill=tk.X)
        
        # money frame
        self.money_frame = tk.LabelFrame(self, text=msg.IW_MONEY)
        money = msg.MONEYFORMAT % 0
        money = money.replace(".", msg.MONEYSPLIT)
        self.money_amount.set(money)
        self.money_amount.trace("w", lambda n,e,m: self._ValidateField(check="money"))
        self.money_entry = tk.Entry(self.money_frame, 
                                    textvariable = self.money_amount,
                                    font="Arial 12 bold")
        self.money_entry.pack(fill = tk.X)
        self.account_label = tk.Label(self.money_frame, text = msg.IW_ACCOUNT)
        accounts = self.buildAccountList()
        width = 0
        for account in accounts:
            if len(account) >= width: width = len(account)
        self.selected_account.set(accounts[0])
        account_selector = tk.OptionMenu(self.money_frame,self.selected_account,*accounts)
        account_selector.config(width = width)
        account_selector.pack(fill = tk.X)
        self.money_frame.pack(fill = tk.X)

        # submit button
        self.submit = tk.Button(self,
                                          text = msg.IW_ADD,
                                          height = 4,
                                          command = self._addEvent)
        self.submit.pack(fill = tk.X)


    def buildAccountList(self):
        """ building the account list for the OptionMenu 

        returns : [string,...]
            string: "accountname (balance)"
            
        """

        # build list for characters accounts 
        accounts = self.char.getAccounts()
        account_list = []
        for account in accounts: 
            account_name = account.get("name")
            if account_name == '0': account_name = msg.AC_PRIMARY_NAME
            balance = float(account.get("balance"))
            pretty_balance = msg.MONEYFORMAT % balance
            pretty_balance = pretty_balance.replace(".", msg.MONEYSPLIT)
            display_string = account_name + " (" + pretty_balance + ")"
            account_list.append(display_string)
        
        # append an entry for the characters cash
        items = self.char.getItems(item_type=config.ItemTypes.MONEY)
        value = 0
        for item in items:
            item_quantity = item.get("quantity")
            item_value = item.get("price")
            value += int(item_quantity) * float(item_value)
        value_string = msg.MONEYFORMAT % value
        value_string = value_string.replace(".", msg.MONEYSPLIT)
        display_string = msg.IW_CASH + " (" + value_string + ")"
        account_list.append(display_string)

        return account_list

    # validating the contents of the entry fields
    def _ValidateField(self, check):
        """ this method validates the entry fields. 
        
        check (str): valid: xp, money
            to determine which field to check

        This method will highlight the fields if the entered
        values do not match specific regex strings. 
        Additionally the submit button will be disabled
        to prevent passing of bad input into further processing. 
        """

        # setup for xp field
        if check == "xp":
            var_value = self.xp_var.get()
            regex = "^[+-]?\d*"
            widget = self.xp_spinbox
        # setup for money field
        if check == "money":
            var_value = self.money_amount.get()
            regex = "^[+-]?\d*[\.,]?[0-9]?[0-9]?"
            widget = self.money_entry
        
        # pattern matching and comparison 
        result = re.findall(regex,var_value)
        if result and result[0] == var_value:
            widget.config(foreground="#000000")
            self.submit.config(state = tk.NORMAL)
        else:
            widget.config(foreground="#ff0000")
            self.submit.config(state = tk.DISABLED)

    # initiate the character improvments 
    def _addEvent(self):
        event_name = self.event_name.get()
        xp = int(self.xp_var.get())
        money = float(self.money_amount.get().replace(",","."))
        account = self.selected_account.get()
        account = re.sub(" \(.*\)","",account)
        if account == msg.AC_PRIMARY_NAME:
            account = "0"
        self.char.addXP(xp,reason=event_name)
        self.char.updateAccount(money,reason=event_name)
        self.app._switchWindow(msg.TOOLBAR_CHAR_DATA)
        self.close()

    def close(self):
        # TODO UPDATE LIST OF OPEN WINDOWS # #
        self.app.open_windows["improve"] = 0
        self.destroy()