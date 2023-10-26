from connect import engine
from sqlalchemy.orm import Session
from models import UserDB
from sqlalchemy import update

session = Session(bind=engine)


def errormsg(function_name: str):
    print(f"Error has occured while executing {function_name}")


class User:
    def __init__(self):
        self.name = "Rayyan tele bot"

    def buff_watchlist_add(self, userid, item):
        try:
            selected = session.query(UserDB).filter_by(
                userid=userid).first()
            templist = selected.buff_watchlist
            print("Initial: ", templist)
            templist.append(item)
            print("After: ", templist)
            session.execute(update(UserDB).where(UserDB.userid ==
                            userid).values(buff_watchlist=templist))
            session.commit()
        except Exception as e:
            errormsg("buff_watchlist_add")
        return

    def get_buff_watchlist(self, userid):
        try:
            ret = session.query(UserDB).filter(
                UserDB.userid == userid).one().buff_watchlist
            return ret
        except Exception as e:
            errormsg("get_buff_watchlist")
            return

    def stock_watchlist_add(self, userid: int, item: object):
        try:
            selected = session.query(UserDB).filter_by(
                userid=userid).first()
            templist = selected.stock_watchlist
            print("Initial: ", templist)
            templist.append(item)
            print("After: ", templist)
            session.execute(update(UserDB).where(UserDB.userid ==
                            userid).values(stock_watchlist=templist))
            session.commit()
        except Exception as e:
            errormsg("stock_watchlist_add")

    def get_stock_watchlist(self, userid: int, item: object):
        try:
            ret = session.query(UserDB).filter(
                UserDB.userid == userid).one().stock_watchlist
            return ret
        except Exception as e:
            errormsg("get_stock_watchlist")

    def buff_investments_add(self, userid: int, item: object):
        try:
            selected = session.query(UserDB).filter_by(userid=userid).first()
            templist = selected.buff_investments
            print("Initial: ", templist)
            templist.append(item)
            print("After: ", templist)
            session.execute(update(UserDB).where(UserDB.userid ==
                            userid).values(buff_investments=templist))
            session.commit()
        except Exception as e:
            errormsg("buff_investments_add")

    def get_buff_investments(self, userid: int):
        try:
            ret = session.query(UserDB).filter(
                UserDB.userid == userid).one().buff_investments
            return ret
        except Exception as e:
            errormsg("get_buff_investments")

    def stock_investments_add(self, userid: int, item: object):
        try:
            selected = session.query(UserDB).filter_by(userid=userid).first()
            templist = selected.stock_investments
            print("Initial: ", templist)
            templist.append(item)
            print("After: ", templist)
            session.execute(update(UserDB).where(UserDB.userid ==
                            userid).values(stock_investments=templist))
            session.commit()
        except Exception as e:
            errormsg("stock_investments_add")

    def get_stock_investments(self, userid: int):
        try:
            ret = session.query(UserDB).filter(
                UserDB.userid == userid).one().stock_investments
            return ret
        except Exception as e:
            errormsg("get_stock_investments")

    def buff_watchlist_remove(self, userid: int, item: object):
        try:
            selected = session.query(UserDB).filter_by(userid=userid).first()
            templist = selected.buff_watchlist
            print("Initial: ", templist)
            templist.remove(item)
            print("After: ", templist)
            session.execute(update(UserDB).where(UserDB.userid ==
                            userid).values(buff_watchlist=templist))
            session.commit()
        except Exception as e:
            errormsg("buff_watchlist_remove")

    def buff_investments_remove(self, userid: int, item: object):
        try:
            selected = session.query(UserDB).filter_by(userid=userid).first()
            templist = selected.buff_investments
            print("Initial: ", templist)
            templist.remove(item)
            print("After: ", templist)
            session.execute(update(UserDB).where(UserDB.userid ==
                            userid).values(buff_investments=templist))
            session.commit()
        except Exception as e:
            errormsg("buff_investments_remove")
