from email_reader import EmailReader
from bot import Bot
import json


def main():

    with open('config.json') as json_data_file:
        data = json.load(json_data_file)
    mail_reader = EmailReader(data['mail'])
    bot = Bot(data['bot'], mail_reader)
    bot.start()


if __name__ == "__main__":
    main()
