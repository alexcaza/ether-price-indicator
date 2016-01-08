#!/usr/bin/env python

#  ether-price-indicator
#--------------------------------------

import sys
import gtk
import appindicator
import requests
import OpenSSL
import cryptography
import pyasn1
import json
import os
from ndg import httpsclient
from os.path import expanduser

HOME = expanduser("~")
SETTINGSFILE = os.path.abspath(HOME+"/.local/share/applications/settingsEtherIndicator.dat")
BAD_RETRIEVE = 0xDEADBEEF

class EtherPriceIndicator:
    PING_FREQUENCY = 10 # seconds
    EXCHANGE = 'usdeth'
    ETHERICON = os.path.abspath(HOME + "/.local/share/applications/ethericon.png")
    APPDIR = HOME + "/.local/share/applications/"
    APPNAME = 'Ether Indicator';
    VERSION = '1.0'

    def __init__(self):
        self.initFromFile()
        self.ind = appindicator.Indicator("ether-indicator", 
                                          self.ETHERICON,
                                          appindicator.CATEGORY_APPLICATION_STATUS)
        self.ind.set_status(appindicator.STATUS_ACTIVE)
        self.menu_setup()
        self.ind.set_menu(self.menu)

    def main(self):
        self.updateStatsETH()
        gtk.timeout_add(self.PING_FREQUENCY * 1000, self.updateStatsETH)
        gtk.main()

    def menu_setup(self):
        self.menu = gtk.Menu()
        
        # Create exchange sub-menu.
        self.setExchangeMenu(self.menu)
       # self.menu.SeparatorMenuItem()

        # Create refresh rate sub-menu.
        self.setRefreshMenu(self.menu)
        
        # Add general munu options.
        self.about = gtk.MenuItem("About") 
        self.about.connect("activate",self.menu_about_response)
        self.about.show()
        self.menu.append(self.about)
        self.quit_item = gtk.MenuItem("Quit Indicator")
        self.quit_item.connect("activate", self.quit)
        self.quit_item.show()
        self.menu.append(self.quit_item)

    def setExchangeMenu(self, menuIn):
        exchangeMenu = gtk.Menu()
        exMenu = gtk.MenuItem("Set exchange:")
        exMenu.set_submenu(exchangeMenu)
        
        self.ETHtickers = None
        menuUSDETH = gtk.RadioMenuItem(self.ETHtickers,"USD / ETH"); 
        menuUSDETH.connect("activate", lambda x: self.toggleETHdisplay("usdeth")); 
        menuUSDETH.show()        
        self.ETHtickers = menuUSDETH;
        menuBTCETH = gtk.RadioMenuItem(self.ETHtickers,"BTC / ETH"); 
        menuBTCETH.connect("activate", lambda x: self.toggleETHdisplay("btceth")); 
        menuBTCETH.show()
        self.ETHtickers = menuBTCETH;
        menuETHUSD = gtk.RadioMenuItem(self.ETHtickers,"ETH / USD"); 
        menuETHUSD.connect("activate", lambda x: self.toggleETHdisplay("ethusd")); 
        menuETHUSD.show()
        self.ETHtickers = menuETHUSD;
        menuETHBTC = gtk.RadioMenuItem(self.ETHtickers,"ETH / BTC"); 
        menuETHBTC.connect("activate", lambda x: self.toggleETHdisplay("ethbtc")); 
        menuETHBTC.show()
        self.ETHtickers = menuETHBTC;

        exchangeMenu.append(menuUSDETH);
        exchangeMenu.append(menuBTCETH);        
        exchangeMenu.append(menuETHUSD);
        exchangeMenu.append(menuETHBTC);
        exMenu.show() 
        exchangeMenu.show()
        menuIn.append(exMenu)

    def setRefreshMenu(self, menuIn):
        refreshmenu = gtk.Menu()
        refMenu = gtk.MenuItem("Set refresh rate:")
        refMenu.set_submenu(refreshmenu)

        self.refreshRates = None
        menuRefresh1 = gtk.RadioMenuItem(self.refreshRates,"30s"); 
        menuRefresh1.connect("activate",lambda x: self.setPing(30)); 
        menuRefresh1.show()
        self.refreshRates = menuRefresh1
        menuRefresh2 = gtk.RadioMenuItem(self.refreshRates,"1m"); 
        menuRefresh2.connect("activate",lambda x: self.setPing(60)); 
        menuRefresh2.show()
        self.refreshRates = menuRefresh2
        menuRefresh3 = gtk.RadioMenuItem(self.refreshRates,"5m"); 
        menuRefresh3.connect("activate",lambda x: self.setPing(300)); 
        menuRefresh3.show()
        self.refreshRates = menuRefresh3
        menuRefresh4 = gtk.RadioMenuItem(self.refreshRates,"10m"); 
        menuRefresh4.connect("activate",lambda x: self.setPing(600)); 
        menuRefresh4.show()
        self.refreshRates = menuRefresh4

        refreshmenu.append(menuRefresh1)
        refreshmenu.append(menuRefresh2)
        refreshmenu.append(menuRefresh3)
        refreshmenu.append(menuRefresh4)
        refMenu.show() 
        refreshmenu.show()
        menuIn.append(refMenu)

    def setPing(self, newTime):
        self.PING_FREQUENCY = newTime

    def toggleETHdisplay(self, exch):
        self.EXCHANGE = exch

    def updateStatsETH(self):
        dataOut = ""
        data = BAD_RETRIEVE

        data = self.getEtherChainData()
        if data == BAD_RETRIEVE or data["status"] != 1:
            dataOut = "TempDown"
        else:
            dataOut = {
               'usdeth': '$ ' + str(data['data']['price']['usd']),
               'btceth': u'\u0243' + str(data['data']['price']['btc']),
               'ethusd': u'\u039E' + str(1 / data['data']['price']['usd']) + ' / $',
               'ethbtc': u'\u039E' + str(1 / data['data']['price']['btc']) + ' / ' + u'\u0243',
               }.get(self.EXCHANGE, str(9)) 

        self.ind.set_label(dataOut)

    def getEtherChainData(self):
        try :
            r = requests.get("https://etherchain.org/api/basic_stats", verify=True)
            print r.json()['data']['price']['usd']
        except requests.exceptions.RequestException as e:
            print e

        return r.json()


    #############################################
    ##########Settings###File####################
    #############################################
	# grab settings from file
    def initFromFile(self):
        try:
            with open(SETTINGSFILE): pass
        except IOError:
            print 'Need to make new file.'
            file = open(SETTINGSFILE, 'w')
            file.write(os.getcwd()+'\n')
            file.write('10 \n')
            file.close()
        f = open(SETTINGSFILE, 'r')
        lines = f.readlines()
        currDir = (lines[0].strip())
        if ".local/share/applications" not in currDir:
            self.setAppDir(currDir)
        print "App Directory : " + self.APPDIR
        print "Refresh rate:",int(lines[1]),"seconds"
        self.PING_FREQUENCY = int(lines[1])
#        self.EXCHANGE = str(lines[2])
        f.close()

    def setAppDir(self,currDir):
        self.ETHERICON = os.path.abspath(currDir+"/res/ethericon.png")
        self.APPDIR = currDir

	# save settings at quit and kill indicator
    def quit(self, widget):
        try:
            print 'Saving Last State.'
            file = open(SETTINGSFILE, 'w')
            file.write(str(self.APPDIR) + '\n')
            file.write(str(self.PING_FREQUENCY) + '\n')
            file.write(str(self.EXCHANGE) + '\n')
            file.close()
        except IOError:
            print " ERROR WRITING QUIT STATE"
        gtk.main_quit()
        sys.exit(0)

    def menu_about_response(self,widget):
        self.menu.set_sensitive(False)
        widget.set_sensitive(False)
        ad=gtk.AboutDialog()
        ad.set_name(self.APPNAME)
        ad.set_version(self.VERSION)
        ad.set_comments("An Ethereum ticker indicator")
        ad.set_license(''+
        'This program is free software: you can redistribute it and/or modify it\n' +
        'under the terms of the GNU General Public License as published by the\n' +
        'Free Software Foundation, either version 3 of the License, or (at your option)\n' +
        'any later version.\n\n' +
        'This program is distributed in the hope that it will be useful, but\n' +
        'WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY\n' +
        'or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for\n' +
        'more details.\n\n' +
        'You should have received a copy of the GNU General Public License along with\n' +
        'this program.  If not, see <http://www.gnu.org/licenses/>.')
        ad.set_website('https://github.com/RichHorrocks/ether-price-indicator')
        ad.set_authors(['Written by RichHorrocks, based on code by jj9: \n' +
                        'Tips appreciated! \n' +
                        'BTC: 1HCAo4UeQjQrtxCBUzatYxzt8u1UyafPi5  \n ' +
                        'ETH: I should really get a wallet... \n ' ])
        ad.run()
        ad.destroy()
        self.menu.set_sensitive(True)
        widget.set_sensitive(True)

if __name__ == "__main__":
    indicator = EtherPriceIndicator()
    indicator.main()
