import telebot as tb
import os
from dotenv import load_dotenv
from typing import Final
from classes.Buff import Buff
from classes.User import User
from telebot import types, util
from sqlalchemy.orm import Session
from connect import engine
from models import UserDB
import logging

# logger = tb.logger
# tb.logger.setLevel(logging.DEBUG)


#################### INITIALISATION #############################

session = Session(bind=engine)
load_dotenv()

BOT_API: Final = os.getenv("BOT_API")
BUFF_USER: Buff = Buff()
USER: User = User()


bot = tb.TeleBot(BOT_API, parse_mode=None)

with open('./utils/buffids.txt', "r", encoding="utf-8") as f:
    raw = f.readlines()
    BUFF_DATA = []
    for l in raw:
        BUFF_DATA.append(l.strip().split(';'))

callback_args = {
    "userid": None,
    "init": None,
    "prev_call": None,
    "list": None,
}

LEAVE_CALLBACK_TEXT = "You have exitted /view!\n\nTo explore BUFF items, type /buff!\nTo explore STOCK items, type /stock\n\nIf you have any enquiries or faced any issues, please raise it up on the github repository: https://github.com/rayyanwong/telebot-pricescrapper/ "
################ HELPER FUNCTIONS ###############################


def buff_print_datalist(data_lst):
    output = ''
    for row in data_lst:
        output += "[" + row[0] + "]" + " " + row[1] + '\n'
    return output


def check_if_user_exists(userid):
    res = session.query(UserDB).where(UserDB.userid == userid).all()
    if (len(res) == 0):
        return False
    return True


def insert_new_user(userid):
    if not check_if_user_exists(userid):
        try:
            user_insertobj = UserDB(
                userid=userid,
                buff_watchlist=[],
                buff_investments=[],
                stock_watchlist=[],
                stock_investments=[],
            )
            session.add(user_insertobj)
            session.commit()
            print(f"Successfully added userid: {userid} into the database!")
        except Exception as e:
            print(f"Inserting of userid: {userid} into database has failed!")
    else:
        print(f"User of userid: {userid} already exists in the database!")


def get_items_withPricesArr(arr: list[object]) -> list[object]:
    global BUFF_USER
    retArr = []
    for item in arr:
        # item: {'itemname': __, 'itemid': __}
        retArr.append(BUFF_USER.getPriceById(
            itemid=item["itemid"], itemname=item['itemname']))
    return retArr


def format_watchlist(arr: list[object], typeOfWatchlist: str):
    command = "buff" if typeOfWatchlist.lower() == "buff" else "stocks"
    ret = f"[    YOUR {typeOfWatchlist} WATCHLIST    ]\n\n\n"
    count = 1
    if len(arr) == 0:
        ret = f"Your {typeOfWatchlist} watchlist is empty!\n\nTo add your {typeOfWatchlist} watchlist, type /view to start adding your first item OR\n/{command} and search for your first item to add!"
    else:
        for item in arr:
            # item: {'itemname': ___ , 'itemid': ____ , 'price': ____ }
            ret += f'{count}. {item["itemid"]} | {item["itemname"]} \n\tCurrent Price: {item["price"]}\n\n'
            count += 1
    return ret


def format_investments(arr: list[object], typeOfInvesments: str) -> str:
    command = "buff" if typeOfInvesments.lower() == "buff" else "stocks"
    ret = f"[    YOUR {typeOfInvesments} PORTFOLIO    ]\n\n\n"
    count = 1
    if len(arr) == 0:
        ret = f"Your {typeOfInvesments} portfolio is empty!\n\nTo add your {typeOfInvesments} portfolio, type /view to start adding your first item OR\n/{command} and search for your first item to add!"
    else:
        for item in arr:
            # item : {'itemname', 'itemid', 'buyprice', 'totalcost', 'quantity', 'price'}
            if 'quantity' not in item.keys():
                item["quantity"] = 1
            itemCurPricing = round(
                BUFF_USER.getBuyPriceById(item["itemid"]), 2)
            afterTaxCurPricing = round(itemCurPricing * 0.975, 2)
            getDiff = (
                (afterTaxCurPricing * item["quantity"]) - item['totalcost'])
            profit = True if getDiff >= 0 else False
            getPercentageDiff = getDiff/item['totalcost'] * 100
            firstline = f'{count}. {item["itemid"]} | {item["itemname"]}\n'
            seperatorline = '-'*len(firstline)*2+'\n'
            pricingline = f'\tBuy price / quantity: {item["buyprice"]}\t\t|\t\tQuantity bought: {item["quantity"]}\t\t|\t\tTotal spent: {item["totalcost"]}\n\n'
            analysisline = f'\tCur price / quantity: {itemCurPricing}\t\t|\t\tAmount received after tax / quantity: {afterTaxCurPricing}\t\t|\t\tTotal amount received after tax / all: {afterTaxCurPricing*item["quantity"]}\n\n'
            percentageline = f'Percentage increased: {round(getPercentageDiff,2)}%' if profit else f'Percentage decreased: {round(getPercentageDiff,2)}%'
            itemline = firstline+seperatorline+pricingline + \
                analysisline+percentageline+'\n\n\n'
            ret += itemline
            count += 1
    return ret
################### MARKUP INIT ##############################

# /view
# allow user to choose BUFF or STOCKS
# allow user to choose Watchlist or Investments
# allow user to remove item or delete completely


exitMarkupButton = types.InlineKeyboardButton(
    text="Exit", callback_data="exit"
)
InlineMarkup1 = types.InlineKeyboardMarkup(row_width=1)
m1_btn1 = types.InlineKeyboardButton(text="🕹️ Buff", callback_data="buff")
m2_btn2 = types.InlineKeyboardButton(text="📊 Stocks", callback_data="stocks")
InlineMarkup1.add(m1_btn1, m2_btn2, exitMarkupButton)

InlineMarkup2 = types.InlineKeyboardMarkup(row_width=1)
m2_btn1 = types.InlineKeyboardButton(
    text="📝 View Watchlist", callback_data="watchlist")
m2_btn2 = types.InlineKeyboardButton(
    text="📈 View Investments", callback_data="investments")
InlineMarkup2.add(m2_btn1, m2_btn2, exitMarkupButton)

InlineMarkup3 = types.InlineKeyboardMarkup(row_width=1)
m3_btn1 = types.InlineKeyboardButton(
    text="➕ Add item", callback_data="additem")
m3_btn2 = types.InlineKeyboardButton(
    text="❌ Remove item", callback_data="removeitem")
m3_btn3 = types.InlineKeyboardButton(
    text="🗑️ Delete List", callback_data="deletelist")

InlineMarkup3.add(m3_btn1, m3_btn2, m3_btn3, exitMarkupButton)

################## BOT HANDLERS ###############################


@bot.message_handler(commands=['start'])
def bot_start(message):
    insert_new_user(message.chat.id)
    bot.reply_to(message=message, text="Waddup waddup?!")


@bot.message_handler(commands=['DEBUG'])
def bot_handle_debug(message):
    global USER
    USER.buff_investments_remove(message.chat.id,  {
                                 'itemid': 43743, 'itemname': '★ StatTrak™ Karambit | Lore (Factory New)', 'price': 20600.0, 'buyprice': 1.0})


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
        curWatchlist = USER.get_buff_watchlist(userid)
        curWatchlist = get_items_withPricesArr(curWatchlist)
        formatted_str = format_watchlist(curWatchlist, "BUFF")
        bot.send_message(userid, formatted_str)
        return

    elif (message.text == "Get Investments"):
        curInvestments = USER.get_buff_investments(userid)
        print("Cur: ", curInvestments)
        formatted_str = format_investments(curInvestments, "BUFF")
        bot.send_message(userid, formatted_str)
        return
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
    # ret = {'itemname', 'itemid', 'price'}
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
        USER.buff_watchlist_add(userid, itemObj)
        bot.send_message(
            userid, "BUFF Watchlist has been updated. Select '/buff' -> 'Get Watchlist' to view your BUFF Watchlist")

    elif (message.text == "💰 Add to Investments list"):
        msg = bot.send_message(
            userid, f"Please enter the quantity bought for {itemObj['itemname']}")
        bot.register_next_step_handler(
            msg, process_add_to_investment_buyprice, args)

    elif (message.text == "🔍 Search for another item"):
        del args["data_obj"]
        msg = bot.send_message(
            userid, "You have selected search for another item...")
        bot.register_next_step_handler(msg, bprocess_search_by_handler, args)

    elif (message.text == "👋 Exit"):
        del args["data_obj"]
        bot.send_message(userid, "Exiting BUFF service...")

    else:
        return


def process_add_to_investment_buyprice(message, args: object):
    userid = args["userid"]
    data_obj = args['data_obj']

    try:
        quantity = int(message.text)
        data_obj["quantity"] = quantity
        args["data_obj"] = data_obj
        msg = bot.send_message(
            userid, f"Please enter the buy price per item for {data_obj['itemname']}")
        bot.register_next_step_handler(
            msg, process_add_to_investment_final, args)
    except Exception as e:
        msg = bot.send_message(
            userid, f"Error! Please enter a valid quantity!")
        bot.register_next_step_handler(
            msg, process_add_to_investment_buyprice, args)


def process_add_to_investment_final(message, args: object):
    userid = args["userid"]
    data_obj = args['data_obj']

    try:
        buyprice = float(message.text)
        data_obj["buyprice"] = buyprice
        totalcost = round(buyprice*data_obj["quantity"], 2)
        data_obj["totalcost"] = totalcost
        args["data_obj"] = data_obj
        USER.buff_investments_add(userid=userid, item=data_obj)
        bot.send_message(
            userid, f"✅ You have successfully added {data_obj['itemname']} into your portfolio\n\nTo view your investments, type /view or /buff -> View Investments!\n")
        return
    except Exception as e:
        msg = bot.send_message(userid, f'Error! Please enter a valid price!')
        bot.register_next_step_handler(
            msg, process_add_to_investment_final, args)


@bot.message_handler(commands=['view'])
def callback_handler(message):
    global InlineMarkup1
    keyboard = InlineMarkup1
    bot.send_message(message.chat.id, "Welcome to /view,\n\nThis function is designed to allow you to manage your Buff/Stock Watchlists and Investments. \n\n To proceed, choose which service you would like to access!",
                     reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_line(call):
    global InlineMarkup2
    global InlineMarkup3
    global callback_args
    if call.message:
        callback_args["userid"] = call.message.chat.id
        print("Call is: ", call.data)
        if call.data == "buff":
            callback_args['prev_call'] = "buff"
            callback_args["init"] = "buff"
            # get buff data and formatted text for output
            bot.edit_message_text(
                chat_id=call.message.chat.id, message_id=call.message.message_id, text="Which would you like to view?", reply_markup=InlineMarkup2)
        elif call.data == "stocks":
            callback_args["init"] = "stocks"
            callback_args['prev_call'] = 'stocks'
            # get stocks data and formatted text for output
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id, text="stocks")
        elif call.data == "watchlist":
            callback_args['prev_call'] = 'watchlist'
            txt = f"Your current {callback_args['init'].upper()} watchlist"
            # get watchlist from class
            if callback_args['init'] == 'buff':
                curWatchlist = USER.get_buff_watchlist(callback_args["userid"])
                curWatchlist = get_items_withPricesArr(curWatchlist)
                formatted_str = format_watchlist(curWatchlist, "BUFF")
                formatted_str += "\nWhat would you like to do?\n\n"
                bot.edit_message_text(
                    chat_id=call.message.chat.id, message_id=call.message.message_id, text=formatted_str, reply_markup=InlineMarkup3)

        elif call.data == "investments":
            if callback_args['init'] == 'buff':
                curInvestments = USER.get_buff_investments(
                    callback_args['userid'])
                print("Cur: ", curInvestments)
                formatted_str = format_investments(curInvestments, "BUFF")
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=formatted_str, reply_markup=InlineMarkup3)

        elif call.data == "exit":
            global LEAVE_CALLBACK_TEXT
            bot.send_message(chat_id=call.message.chat.id,
                             text=LEAVE_CALLBACK_TEXT)

        elif call.data == "additem":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=f"To add a new item, please type /{callback_args['init']} -> Find item you would like to add\n -> Add to your Watchlist or Portfolio\n\nIf you encounter any problems or have any enquiries, visit the github repository: https://github.com/rayyanwong/telebot-pricescrapper/ to raise an issue.\n\n Thank you!")
            return


####################################################
################   DRIVER CODE #####################
####################################################
print("Starting bot...")
print("Bot is running")
bot.infinity_polling()
