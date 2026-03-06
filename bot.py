from automation import BrowserBot, write_message, open_app
from scraper import get_titles
import time

def run_bot():

    print("Starting Jarvis Bot")

    bot = BrowserBot()

    bot.open_site("https://google.com")

    time.sleep(2)

    bot.search_google("Latest AI news")

    time.sleep(5)

    titles = get_titles("https://news.ycombinator.com")

    print("Top titles:")

    for t in titles[:5]:
        print(t)

    open_app("notepad")

    time.sleep(2)

    write_message("Jarvis bot started successfully")

    bot.close()

if __name__ == "__main__":
    run_bot()