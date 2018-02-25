#!/usr/bin/env python

from __future__ import print_function

import time
import datetime
from colorclass import Color, Windows
from terminaltables import SingleTable
import argparse
import requests
import sys
import signal
from textwrap import wrap

parser = argparse.ArgumentParser(description="MINING POOL HUB Information Gatherer 2018 Orhan Gazi Hafif WTFPL Licence")
parser.add_argument('-a', metavar='api_key', required=True, help='API KEY from \'Edit Account\' page.\n')
parser.add_argument('-i', metavar='id', help='USER ID from \'Edit Account\' page\n')
parser.add_argument('-c', metavar='crypto_currency', default='BTC', help='Which exchange currency to display total in (default BTC).\n')
parser.add_argument('-f', metavar='fiat_currency', help=' Not needed, extra column for displaying other fiat currency total.\n')
parser.add_argument('-n', metavar='non_stop', help=' Not needed, if equals \'YES\', run the application continuously, default, in every 2 minutes.\n')
parser.add_argument('-d', metavar='dashboard_coin', help='For displaying that coin\'s dashboard info, name must be same at website, for example, for zcash.miningpoolhub.org, it must be zcash.\n')
parser.add_argument('-r', metavar='reload_time', default='120', help='Reload time in seconds. Must be between 10 and 1800, (default 120)')
args = parser.parse_args()

def handler(signum, frame):
    print (Color('\n{autogreen}Bye bye!{/autogreen}'))
    exit()

signal.signal(signal.SIGINT, handler)

class MphInfo:
    def __init__(self, api_key, id, currency, fiat_currency, mining_coin, reload_time):
        Windows.enable(auto_colors=True, reset_atexit=True)  # For just Windows
        self.key_            = api_key
        self.id_             = id
        self.cur_            = currency
        self.fcur_           = fiat_currency
        self.coin_           = mining_coin
        self.reload_time_    = int(reload_time)
        self.crypto_symbols_ = {}

        if self.reload_time_ > 1800 or int(reload_time) < 15:
            print('reload_time argument must be between 10 and 1800. For more info, run $ python3 display.py --help' )
            exit()


        self.setSymbols()

        print(Color('{autoyellow}benafleck{/autoyellow}')) # lol ;)

        self.time_str_ = 'Hello world, What time is it?'

        self.dot_count_ = 0

        self.other_cur = False
        self.dashb_    = False
        if args.f != None:
            self.other_cur = True
        if args.d != None:
            self.dashb_ = True

        self.balances_table_data_ = []
        self.balances_table_     = SingleTable([])

        if self.dashb_:
            self.dashb_table_data_ = []
            self.dashb_table_      = SingleTable([])

        self.printDotInfo('Getting values and converting to currencies')
        self.getBalances()
        self.printTables()

        if args.n == 'YES':
            self.displayNonStop()
        else:
            exit()

    def displayNonStop(self):
        while True:
            time.sleep(self.reload_time_)
            self.clearLastLine()
            self.printDotInfo(str(Color(self.time_str_)))
            self.getBalances()
            self.printTables()

    def clearScreen(self):
        print("\033[H\033[J")

    def clearLastLine(self):
        sys.stdout.write("\033[F")  # back to previous line
        #sys.stdout.write("\033[K")  # Clear to the end of line

    def strI0(self, value): # returns integer's str or '0.0'
        try:
            return str(int(value))
        except:
            return '0'

    def strF0(self, value, perc=None): # returns float's str or '0.0'
        try:
            if perc == None:
                return str(float(value))
            else:
                return str(perc % float(value))
        except:
            return '0.0'

    def printTables(self):
        self.clearScreen()
        self.makeTables()
        print(self.balances_table_.table)
        if self.dashb_:
            print(self.dashb_table_.table)
        self.time_str_ = time.strftime('Last update: {autoyellow}%d/%m/%Y{/autoyellow} {autocyan}%H:%M:%S {/autocyan}',
                                       datetime.datetime.now().timetuple())
        print(Color(self.time_str_))

    def makeTables(self):
        self.balances_table_ = SingleTable(self.balances_table_data_)
        self.balances_table_.inner_heading_row_border = False
        self.balances_table_.inner_row_border = True
        self.balances_table_.justify_columns = {0: 'center', 1: 'center', 2: 'center', 3: 'center'}

        if self.dashb_:
            self.dashb_table_ = SingleTable(self.dashb_table_data_)
            self.dashb_table_.inner_heading_row_border = False
            self.dashb_table_.inner_row_border = True
            self.dashb_table_.justify_columns = {0: 'center', 1: 'center'}

    def getMphJsonDict(self, method, coin=None, id=None):
        url = "https://{}miningpoolhub.com/index.php?page=api&action={}&api_key={}&id={}"

        if coin == None and id == None:
            url=url.format("", method, self.key_, "")

        elif coin != None and id != None:
            url=url.format(coin + '.', method, self.key_, id)

        response = requests.get(url, timeout=10)
        json_dict = response.json()
        return json_dict

    def getValueInOtherCurrency(self, curency, amount, other_currency, use_dot=None):
        if curency.upper() == other_currency.upper(): # No need to convert
            return amount
        url = "https://min-api.cryptocompare.com/data/price?fsym={}&tsyms={}".format(curency.upper(), other_currency.upper())
        response = requests.get(url, timeout=10)
        json_dict = response.json()
        price = json_dict[other_currency.upper()]
        value = float(price) * float(amount)
        if use_dot != None:
            self.printDotInfo()
        return value

    def printDotInfo(self, info=None):
        """ ⠋ ⠙ ⠹ ⠸ ⠼ ⠴ ⠦ ⠧ ⠇ ⠏ """
        if info == None:
            if self.dot_count_ == 0:
                sys.stdout.write('\b\b\b ⠙ \b ')
                sys.stdout.flush()
                self.dot_count_ += 1
            elif self.dot_count_ == 1:
                sys.stdout.write('\b\b\b ⠹ \b ')
                sys.stdout.flush()
                self.dot_count_ += 1
            elif self.dot_count_ == 2:
                sys.stdout.write('\b\b\b ⠹ \b ')
                sys.stdout.flush()
                self.dot_count_ += 1
            elif self.dot_count_ == 3:
                sys.stdout.write('\b\b\b ⠸ \b ')
                sys.stdout.flush()
                self.dot_count_ += 1
            elif self.dot_count_ == 4:
                sys.stdout.write('\b\b\b ⠼ \b ')
                sys.stdout.flush()
                self.dot_count_ += 1
            elif self.dot_count_ == 5:
                sys.stdout.write('\b\b\b ⠴ \b ')
                sys.stdout.flush()
                self.dot_count_ += 1
            elif self.dot_count_ == 6:
                sys.stdout.write('\b\b\b ⠦ \b ')
                sys.stdout.flush()
                self.dot_count_ += 1
            elif self.dot_count_ == 7:
                sys.stdout.write('\b\b\b ⠧ \b ')
                sys.stdout.flush()
                self.dot_count_ += 1
            elif self.dot_count_ == 8:
                sys.stdout.write('\b\b\b ⠇ \b ')
                sys.stdout.flush()
                self.dot_count_ += 1
            elif self.dot_count_ == 9:
                sys.stdout.write('\b\b\b ⠏ \b ')
                sys.stdout.flush()
                self.dot_count_ += 1
            else:
                sys.stdout.write('\b\b\b ⠋ \b ')
                sys.stdout.flush()
                self.dot_count_ = 0
        else:
            sys.stdout.write(info + ' ⠋ \b ')
            sys.stdout.flush()
            self.dot_count_ = 0

    def getBalances(self):
        sign = ""
        if self.other_cur:
            if self.fcur_ == 'TRY':
                sign = '₺'
            elif self.fcur_ == 'EUR':
                sign = '€'
            elif self.fcur_ == 'AZN':
                sign = '₼'
            elif self.fcur_ == 'GBP':
                sign = '£'
            elif self.fcur_ == 'CNY' or self.fcur_ == 'JPY' :
                sign = '¥'
            elif self.fcur_ == 'AUD':
                sign = '$'
            elif self.fcur_ == 'ALL':
                sign = 'L'
            else:
                sign = self.fcur_

        if self.cur_ == 'BTC':
            fave_crypto_sign = 'Ƀ'
        elif self.cur_ == 'ETH':
            fave_crypto_sign = '⧫'
        else:
            fave_crypto_sign = self.cur_

        balances_dict  = self.getMphJsonDict("getuserallbalances")

        coins = {}
        total_fave_crypto = 0.0

        for coin in balances_dict["getuserallbalances"]["data"]:
            symbol = self.crypto_symbols_[coin["coin"]]
            balance = sum([
                coin["confirmed"],
                coin["unconfirmed"]
             ])
            balance_ex = sum([
                coin["ae_confirmed"],
                coin["ae_unconfirmed"],
                coin["exchange"]
             ])
            coins[symbol + "_balance"] = balance
            coins[symbol + "_exchange"] = balance_ex
            coin_total_balance = balance + balance_ex

            total_fave_crypto += self.getValueInOtherCurrency(symbol, coin_total_balance, self.cur_, True)
            coins[symbol + "_fiat_usd"] = self.getValueInOtherCurrency(symbol, balance, 'USD', True)
            if self.other_cur:
                coins[symbol + "_fiat_my_cur"] = self.getValueInOtherCurrency(symbol, balance, self.fcur_, True)


        total_usd = self.getValueInOtherCurrency(self.cur_, total_fave_crypto, 'USD', True)

        self.balances_table_data_ = []

        title =[
            Color('{autoyellow}Total Balance{/autoyellow}\n'+ fave_crypto_sign +'{autocyan}' + str("%.6f" % total_fave_crypto) + '{/autocyan}'),
            Color('{autoyellow}Confirmed+{/autoyellow}\n{autoyellow}Unconfirmed{/autoyellow}'),
            Color('{autoyellow}Exchange+{/autoyellow}\n{autoyellow}AE_All{/autoyellow}'),
            Color('{autoyellow}Total{/autoyellow}\n${autocyan}' + str("%.2f" % total_usd) + '{/autocyan}'),
        ]

        if self.other_cur:
            total_fiat = self.getValueInOtherCurrency(self.cur_, total_fave_crypto, self.fcur_, True)
            title.append(Color('{autoyellow}Total{/autoyellow}\n' + sign + '{autocyan}' + str("%.2f" % total_fiat) + '{/autocyan}'))

        self.balances_table_data_.append(title)

        for coin in balances_dict["getuserallbalances"]["data"]:
            symbol = self.crypto_symbols_[coin["coin"]]

            coin_line = [
                Color('{autocyan}' + coin["coin"].title() + '{/autocyan}'),
                Color( str("%.9f" % coins[symbol + '_balance'])),
                Color('{autored}' + str("%.6f" % coins[symbol + '_exchange']) + '{/autored}'),
                Color('${autogreen}' + str("%.2f" % coins[symbol + '_fiat_usd']) + '{/autogreen}'),
            ]

            if self.other_cur:
                coin_line.append(Color(sign + '{autogreen}' + str("%.2f" % coins[symbol + '_fiat_my_cur']) + '{/autogreen}'))

            self.balances_table_data_.append(coin_line)



        if self.dashb_:
            worker_dict    = self.getMphJsonDict("getuserworkers", self.coin_, self.id_)
            dashboard_dict = self.getMphJsonDict("getdashboarddata", self.coin_, self.id_)

            dashb_str = ''
            symbol = self.crypto_symbols_[self.coin_]
            last24 = float(dashboard_dict["getdashboarddata"]["data"]["recent_credits_24hours"]["amount"])
            last24_usd = self.getValueInOtherCurrency(symbol, last24, 'USD', True)
            last24_btc = self.getValueInOtherCurrency(symbol, last24, 'BTC', True)
            dashb_str+= Color('{autoyellow}Last 24h {/autoyellow} {autocyan}' + str("%.8f" % last24) + '{/autocyan} ' + symbol + '\n')
            dashb_str+= Color('{autoyellow}Est. 30d:{/autoyellow}\n'
                              + 'Ƀ{autocyan}'  + str("%.8f" % (30 * last24_btc)) + '{/autocyan}\n'
                              + '${autogreen}' + str("%.2f" % (30 * last24_usd)) + '{/autogreen}')

            if self.other_cur:
                last24_fiat = self.getValueInOtherCurrency(symbol, last24, self.fcur_, True)
                dashb_str+= Color('\n' + sign + '{autogreen}' + str("%.2f" % (30 * last24_fiat)) + '{/autogreen}')

            self.dashb_table_data_ = []
            total_hashrate = 0.0
            workers_str = ''
            for worker in worker_dict["getuserworkers"]["data"]:
                workers_str += Color('{autoyellow}' + worker["username"] + '{/autoyellow} {autocyan}' + str("%.3f" % float(self.strF0(worker["hashrate"]))) + '{/autocyan} KH/s\n')
                total_hashrate += float(self.strF0(worker["hashrate"]))
            workers_str += Color('\n{autoyellow}Total{/autoyellow} {autocyan}' + str("%.3f" % total_hashrate) + '{/autocyan} KH/s')

            dashboard_info = [workers_str, dashb_str]
            self.dashb_table_data_.append(dashboard_info)





    def setSymbols(self):
        self.crypto_symbols_ = {
            "adzcoin": "ADZ",
            "auroracoin": "AUR",
            "bitcoin": "BTC",
            "bitcoin-cash": "BCH",
            "bitcoin-gold": "BTG",
            "dash": "DSH",
            "digibyte": "DGB",
            "digibyte-groestl": "DGB",
            "digibyte-skein": "DGB",
            "digibyte-qubit": "DGB",
            "ethereum": "ETH",
            "ethereum-classic": "ETC",
            "expanse": "EXP",
            "feathercoin": "FTC",
            "gamecredits": "GAME",
            "geocoin": "GEO",
            "globalboosty": "BSTY",
            "groestlcoin": "GRS",
            "litecoin": "LTC",
            "maxcoin": "MAX",
            "monacoin": "MONA",
            "monero": "XMR",
            "musicoin": "MUSIC",
            "myriadcoin": "XMY",
            "myriadcoin-skein": "XMY",
            "myriadcoin-groestl": "XMY",
            "myriadcoin-yescrypt": "XMY",
            "sexcoin": "SXC",
            "siacoin": "SC",
            "startcoin": "START",
            "verge": "XVG",
            "vertcoin": "VTC",
            "zcash": "ZEC",
            "zclassic": "ZCL",
            "zcoin": "XZC",
            "zencash": "ZEN"
        }

def main():
    m = MphInfo(args.a, args.i, args.c, args.f, args.d, args.r)

if __name__ == '__main__':
    main()
