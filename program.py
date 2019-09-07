import Bot
from time import sleep
from selenium.common.exceptions import ElementClickInterceptedException
import sys


def main():
    if sys is None or len(sys.argv) < 3:
        print("You did not write the correct system variables")
        return

    username = sys.argv[1]
    password = sys.argv[2]
    url = "http://bgmafia.com/auth/login"
    url_search = "http://bgmafia.com/matchmaker"
    min_level = "21"
    max_level = ""
    max_respect = "30000000"

    bot = Bot.GameBot(url, username, password, min_level, max_level, max_respect, url_search)
    try:
        bot.start()
        bot.login()
        bot.check_status()
        bot.submit()
    except ElementClickInterceptedException:
        print(ElementClickInterceptedException)
        bot.submit_error()
    sleep(1)


if __name__ == "__main__":
    main()
