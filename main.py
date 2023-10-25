import telebot as tb
import os
from dotenv import load_dotenv
from typing import Final
from classes.Buff import Buff
from classes.User import User
from telebot import types, util
from sqlalchemy.orm import Session
from connect import engine

session = Session(bind=engine)
load_dotenv()

BOT_API: Final = os.getenv("BOT_API")
BUFF_USER: Buff = Buff()

bot = tb.TeleBot(BOT_API, parse_mode=None)

with open('./utils/buffids.txt', "r", encoding="utf-8") as f:
    raw = f.readlines()
    BUFF_DATA = []
    for l in raw:
        BUFF_DATA.append(l.strip().split(';'))


def buff_print_datalist(data_lst):
    output = ''
    for row in data_lst:
        output += "[" + row[0] + "]" + " " + row[1] + '\n'
    return output


USER = User(None)


@bot.message_handler(commands=['start'])
def bot_start(message):
    global USER
    USER = User(message.chat.id)
    bot.reply_to(message=message, text="Waddup waddup?!")


@bot.message_handler(commands=['buff'])
def bot_handle_buff(message):
    try:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=2)
        markup.add("Find price of item by name",
                   "Find price of item by id",
                   "Get Watchlist",
                   "Get Investments",
                   "Generate Items List"
                   )
        msg = bot.reply_to(
            message, "What would you like to do?", reply_markup=markup)
        bot.register_next_step_handler(msg, bot_handle_buff_query)
    except Exception as e:
        bot.reply_to(message, "An error has occured")


def bot_handle_buff_query(message):
    global USER
    userid = message.chat.id
    args = {"userid": userid}

    if (message.text == "Find price of item by name"):
        args["search_by_choice"] = 1
        msg = bot.send_message(
            userid, "Please send the name of the item you would like to search for!\n\nFor example:\nKarambit | Lore (Factory New)\nAK-47 | Frontside Misty (Minimal Wear)\nSticker | Fnatic | Atlanta 2017")
        bot.register_next_step_handler(msg, bprocess_search_by_handler, args)

    elif (message.text == "Find price of item by id"):
        args["search_by_choice"] = 2
        msg = bot.send_message(
            userid, "Please send the item id of the item you would like to search for!\n\nFor example:\n38169\n39544\n40189")
        bot.register_next_step_handler(msg, bprocess_search_by_handler, args)

    elif (message.text == "Get Watchlist"):
        curWatchlist = USER.get_buff_watchlist()
        print(curWatchlist)
        return

    elif (message.text == "Get Investments"):
        msg = bot.send_message(userid, "Get investments")
        args["choice"] = 4
    elif (message.text == "Generate Items List"):
        # allow user to filter by item type
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=2)
        markup.add("Get list of ALL items", "Filter list with name")
        msg = bot.send_message(
            userid, "Would you like to \nGet list of all items\nFilter list with name of item", reply_markup=markup)
        bot.register_next_step_handler(msg, process_get_buff_list, args)
    else:
        bot.reply_to(message, "Unknown Input. Please try again.")
        return


def process_get_buff_list(message, args):
    userid = args["userid"]
    if (message.text == "Get list of ALL items"):
        datastr = buff_print_datalist(BUFF_DATA)
        splitted_text = util.split_string(datastr, 3000)
        for t in splitted_text:
            bot.send_message(userid, t)
    elif (message.text == "Filter list with name"):
        msg = bot.send_message(
            userid, "Enter the name of item you would like to search for\nand we will generate a list of\nrelevant items!")
        bot.register_next_step_handler(msg, process_filter_buff_list, args)


def process_filter_buff_list(message, args):
    userid = args["userid"]
    output_list = []
    for obj in BUFF_DATA:
        if (message.text.lower() in obj[1].lower()):
            output_list.append(obj)
    output_str = buff_print_datalist(output_list)
    splitted_text = util.split_string(output_str, 3000)
    for t in splitted_text:
        bot.send_message(userid, t)


def bprocess_search_by_handler(message, args: object):

    userid = args["userid"]
    choice = args["search_by_choice"]

    if (choice == 1):
        try:
            to_find_name = message.text
            ret: object = BUFF_USER.getPriceByName(to_find_name)
            if ret == None:
                msg = bot.send_message(
                    userid, ret+". Please enter another name!")
                bot.register_next_step_handler(
                    msg, bprocess_search_by_handler, args)
        except Exception as e:
            print(e)
            bot.send_message(
                userid, "Error has occured! Please contact admin!")

    elif (choice == 2):
        try:
            to_find_id = int(message.text)
            ret: object = BUFF_USER.getPriceById(to_find_id)
            if ret == None:
                msg = bot.send_message(
                    userid, ret+". Please enter another id!")
                bot.register_next_step_handler(
                    msg, bprocess_search_by_handler, args)
        except Exception as e:
            print(e)
            bot.send_message(
                userid, "Error has occured! Please contact admin!")
    args["data_obj"] = ret
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=1)
    markup.add("⭐ Add to BUFF watchlist",
               "💰 Add to Investments list",
               "🔍 Search for another item",
               "👋 Exit")
    msg = bot.send_message(
        userid, f"You have selected {ret['itemname']}\n\n Item ID: {ret['itemid']}\n\nIts current price is ¥{ret['price']}\n\n\nWhat would you like to do next?\n\n1. Add to BUFF watchlist\n\n2.Add to Investments list\n\n3.Search for another item\n\n4.Exit", reply_markup=markup)
    bot.register_next_step_handler(msg, bprocess_get_result_handler, args)


def bprocess_get_result_handler(message, args: object):
    global USER
    userid = args['userid']
    itemname = args["data_obj"]["itemname"]
    itemid = args["data_obj"]["itemid"]
    itemObj = {
        'itemname': itemname,
        'itemid': itemid
    }
    print("Item Object is: ", itemObj)
    if (message.text == "⭐ Add to BUFF watchlist"):
        USER.buff_watchlist_add(itemObj)
        bot.send_message(
            userid, "BUFF Watchlist has been updated. Select '/buff' -> 'Get Watchlist' to view your BUFF Watchlist")

    elif (message.text == "💰 Add to Investments list"):
        USER.buff_investment_add(itemObj)
        bot.send_message(
            userid, "BUFF Investments has been updated. Select '/buff' -> 'Get Investments' to view your BUFF Investments")

    elif (message.text == "🔍 Search for another item"):
        msg = bot.send_message(
            userid, "You have selected search for another item...")
        bot.register_next_step_handler(msg, bprocess_search_by_handler, args)

    elif (message.text == "👋 Exit"):
        bot.send_message(userid, "Exiting BUFF service...")

    else:
        pass


####################################################
################   DRIVER CODE #####################
####################################################
print("Starting bot...")
print("Bot is running")
bot.infinity_polling()
