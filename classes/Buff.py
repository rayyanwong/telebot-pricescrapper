import requests
from dotenv import load_dotenv
import os

load_dotenv()

with open('./utils/buffids.txt', "r", encoding="utf-8") as f:
    raw = f.readlines()
    data = []
    for l in raw:
        data.append(l.strip().split(';'))


COOKIES = os.getenv("COOKIES")


class Buff:
    def __init__(self):
        self.name = "Rayyan buff telebot"

    def getIdByName(self, itemname):
        for row in data:
            if (itemname.lower() in row[1].lower()):
                return row[0]
        return None

    def getNameById(self, itemid):
        for row in data:
            if (int(itemid) == int(row[0])):
                return row[1]
        return None

    def getPriceByName(self, itemname):
        itemid = self.getIdByName(itemname)
        if (itemid != None):
            try:
                return self.getPriceById(itemid=itemid, itemname=itemname)
            except Exception as e:
                return "Error 404"
        return "Unable to find item"

    def getPriceById(self, itemid, itemname=""):
        URL = "https://buff.163.com/api/market/goods/buy_order?game=csgo&goods_id="
        r = requests.get(URL+str(itemid))
        items = r.json()
        data = items["data"]["items"][0]
        price = float(data['price'])

        # Get buff's exact item name instead of from user input
        itemname = self.getNameById(itemid)
        if itemname == None:
            # item does not exist
            return None

        ret = {
            "itemid": itemid,
            "itemname": itemname,
            "price": price
        }
        return ret
