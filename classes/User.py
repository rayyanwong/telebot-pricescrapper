from connect import engine
from sqlalchemy.orm import Session
from models import UserDB
from sqlalchemy import update

session = Session(bind=engine)


class User:
    def __init__(self):
        self.name = "Rayyan tele bot"

    def buff_watchlist_add(self, userid, item):
        selected = session.query(UserDB).filter_by(
            userid=userid).first()
        templist = selected.buff_watchlist
        print("Initial: ", templist)
        templist.append(item)
        print("After: ", templist)
        session.execute(update(UserDB).where(UserDB.userid ==
                        userid).values(buff_watchlist=templist))
        session.commit()

    def get_buff_watchlist(self, userid):
        ret = session.query(UserDB).filter(
            UserDB.userid == userid).one().buff_watchlist
        return ret

    # def stock_watchlist_add(self, item):
    #     self.stock_watchlist.append(item)
    #     return

    # def buff_watchlist_remove(self, item):
    #     try:
    #         self.buff_watchlist.remove(item)
    #         return "Success"
    #     except Exception as e:
    #         return "Failed to remove item from Buff watchlist!"

    # def stock_watchlist_remove(self, item):
    #     try:
    #         self.stock_watchlist.remove(item)
    #         return "Success"
    #     except Exception as e:
    #         return "Failed to remove item from Stock watchlist!"

    # def buff_investment_add(self, item):
    #     self.buff_investments.append(item)
    #     return

    # def buff_investment_remove(self, item):
    #     try:
    #         self.buff_investments.remove(item)
    #         return "Success"
    #     except Exception as e:
    #         return "Failed to remove item from Buff investments"

    # def stock_investment_add(self, item):
    #     self.stock_investments.append(item)
    #     return

    # def stock_investment_remove(self, item):
    #     try:
    #         self.stock_investments.remove(item)
    #         return "Success"
    #     except Exception as e:
    #         return "Failed to remove item from Stock investments"

    # def get_stock_watchlist(self):
    #     return self.stock_watchlist

    # def get_buff_investments(self):
    #     return self.buff_investments

    # def get_stock_investments(self):
    #     return self.stock_investments
