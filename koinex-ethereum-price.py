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
        iconpath = os.getcwd() + '/ethlogo.png'
        self.indicator = appindicator.Indicator.new(APPINDICATOR_ID, iconpath, appindicator.IndicatorCategory.APPLICATION_STATUS)
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self.build_menu())
        self.indicator.set_label('₹0', APPINDICATOR_ID)
        # Thread to update the price on the label
        self.update = Thread(target=self.get_current_price)
        self.update.setDaemon(True)
        self.update.start()

    def build_menu(self):
        menu = gtk.Menu()
        item_quit = gtk.MenuItem('Quit')
        item_quit.connect('activate', quit)
        menu.append(item_quit)
        menu.show_all()
        return menu

    def get_current_price(self):
        while True:
            reply = requests.get('https://koinex.in/api/ticker')
            if reply.status_code != 200:
                raise Exception('Cannot connect to Koinex Ticker API \- Check internet connection')
            else:
                price = ('₹' + reply.json().get("prices").get("ETH"))
                GObject.idle_add(
                        self.indicator.set_label,
                        price, APPINDICATOR_ID,
                        priority=GObject.PRIORITY_DEFAULT
                        )
            time.sleep(60)

    def quit(source):
        gtk.main_quit()


Indicator()
# To start the indicator
GObject.threads_init()
# ctrl+c exit
signal.signal(signal.SIGINT, signal.SIG_DFL)
gtk.main()
