class User:

    def __init__(self, userid):
        self.userid = userid
        self.buff_watchlist = []  # item name
        self.stock_watchlist = []  # stock name
        self.buff_investments = []  # item name
        self.stock_investments = []  # stock name

    def buff_watchlist_add(self, item):
        self.buff_watchlist.append(item)
        return

    def stock_watchlist_add(self, item):
        self.stock_watchlist.append(item)
        return

    def buff_watchlist_remove(self, item):
        try:
            self.buff_watchlist.remove(item)
            return "Success"
        except Exception as e:
            return "Failed to remove item from Buff watchlist!"

    def stock_watchlist_remove(self, item):
        try:
            self.stock_watchlist.remove(item)
            return "Success"
        except Exception as e:
            return "Failed to remove item from Stock watchlist!"

    def buff_investment_add(self, item):
        self.buff_investments.append(item)
        return

    def buff_investment_remove(self, item):
        try:
            self.buff_investments.remove(item)
            return "Success"
        except Exception as e:
            return "Failed to remove item from Buff investments"

    def stock_investment_add(self, item):
        self.stock_investments.append(item)
        return

    def stock_investment_remove(self, item):
        try:
            self.stock_investments.remove(item)
            return "Success"
        except Exception as e:
            return "Failed to remove item from Stock investments"

    def get_buff_watchlist(self):
        return self.buff_watchlist

    def get_stock_watchlist(self):
        return self.stock_watchlist

    def get_buff_investments(self):
        return self.buff_investments

    def get_stock_investments(self):
        return self.stock_investments
