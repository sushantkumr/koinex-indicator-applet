# -*- coding: utf-8 -*-
import signal
import requests
import gi
import os
import time
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import GObject
from threading import Thread


APPINDICATOR_ID = 'koinex_indicator'


class Indicator():
    def __init__(self):
        # Indicator logic
        iconpath = os.getcwd() + '/ethlogo.svg'
        self.indicator = appindicator.Indicator.new(APPINDICATOR_ID, iconpath, appindicator.IndicatorCategory.APPLICATION_STATUS)
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self.build_menu())
        self.indicator.set_label('₹ 0 | $ 0', APPINDICATOR_ID)
        # Thread to update the price on the label
        self.update = Thread(target=self.get_current_price_koinex)
        # self.update.setDaemon(True)
        self.update.start()

    def build_menu(self):
        self.menu = gtk.Menu()
        menu_item_quit = gtk.MenuItem('Quit')
        menu_item_quit.connect('activate', quit)
        self.menu.append(menu_item_quit)
        self.menu.show_all()
        return self.menu

    def get_current_price_koinex(self):
        while True:
            # API requests to Koinex
            try:
                reply_from_koinex = requests.get('https://koinex.in/api/ticker')

                price_INR = ('₹ ' + reply_from_koinex.json().get("prices").get('inr').get('ETH'))
                price_USD = self.get_current_price_coinbase()
                price = price_INR + ' | ' + price_USD
                GObject.idle_add(
                        self.indicator.set_label,
                        price, APPINDICATOR_ID,
                        priority=GObject.PRIORITY_DEFAULT
                        )
            except:
                pass
            time.sleep(60)

    def get_current_price_coinbase(self):
        # API requests to Coinbase
        try:
            reply_from_coinbase = requests.get('\
            https://api.coinbase.com/v2/prices/ETH-USD/spot')
            price_USD = ('$' + reply_from_coinbase.json().get("data").get("amount"))
            return price_USD

        except:
            pass

        # # Check for successfull reply
        # except:
        #     print('Cannot connect to Coinbase Ticker API')

    def quit(source):
        gtk.main_quit()


Indicator()

# To start the indicator
GObject.threads_init()

# Ctrl+c exit
signal.signal(signal.SIGINT, signal.SIG_DFL)
gtk.main()
