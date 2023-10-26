from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///telebot.db", echo=False)
