"""
Jarvis Bot — Your personal assistant.
Responds to text commands: open sites, search, get news, open apps, type text, launch workspace.
"""
import random
import re
import time
from automation import BrowserBot, write_message, open_app
from scraper import get_titles
from workspace_launcher import open_workspace

# "open X" → treat as app (Windows) when X matches these; value = what to type in Start
KNOWN_APPS = {
    "code": "code",
    "vscode": "code",
    "vs code": "code",
    "notepad": "notepad",
    "chrome": "chrome",
    "brave": "brave",
    "edge": "microsoft edge",
    "tlauncher": "tlauncher",
    "t launcher": "t launcher",
    "file": "file explorer",
    "file explorer": "file explorer",
    "explorer": "file explorer",
}

# Jarvis-style responses
REPLIES = {
    "greeting": [
        "At your service.",
        "Yes, sir?",
        "How may I assist you?",
    ],
    "ack": [
        "Right away.",
        "Done.",
        "Consider it done.",
    ],
    "goodbye": [
        "Goodbye, sir.",
        "Shutting down. Until next time.",
    ],
    "unknown": [
        "I'm not sure how to do that. Try: start, open, search, news, type, close, or exit.",
    ],
}


def say(key, custom=None):
    if custom:
        print(f"  Jarvis: {custom}")
        return
    print(f"  Jarvis: {random.choice(REPLIES[key])}")


def parse_command(line):
    line = line.strip().lower()
    if not line:
        return None, None
    # exit / goodbye
    if line in ("exit", "quit", "goodbye", "close jarvis", "shut down"):
        return "exit", None
    # close browser only
    if line in ("close", "close browser"):
        return "close_browser", None
    # start = full workspace launch (VS Code + Chrome/Brave sites)
    if line == "start":
        return "workspace", None
    # open <site or app>
    m = re.match(r"^open\s+(.+)$", line)
    if m:
        target = m.group(1).strip().lower()
        if target in ("workspace", "my workspace"):
            return "workspace", None
        if target in KNOWN_APPS:
            return "open_app", KNOWN_APPS[target]
        return "open_site", m.group(1).strip()
    # search <query>
    m = re.match(r"^search\s+(.+)$", line)
    if m:
        return "search", m.group(1).strip()
    # news / hacker news / get news
    if re.match(r"^(get\s+)?(news|hacker\s*news)$", line):
        return "news", None
    # type <message> or write <message>
    m = re.match(r"^(?:type|write)\s+(.+)$", line)
    if m:
        return "type", m.group(1).strip()
    return "unknown", None


def run_jarvis():
    print("\n  ———————————————————————————")
    print("  JARVIS  —  At your service.")
    print("  ———————————————————————————")
    print("  Commands: start | open <site|app|workspace> | search <query> | news | type <text> | close | exit")
    print("  start = launch workspace (VS Code + Chrome: kalvium | Brave: youtube, instagram, linkedin, github, leetcode)")
    print("  Apps: code, notepad, chrome, brave, edge, tlauncher, file explorer\n")

    bot = None

    while True:
        try:
            line = input("  You: ").strip()
        except (EOFError, KeyboardInterrupt):
            say("goodbye")
            if bot:
                try:
                    bot.close()
                except Exception:
                    pass
            break

        cmd, arg = parse_command(line)
        if cmd is None:
            continue

        if cmd == "exit":
            say("goodbye")
            if bot:
                try:
                    bot.close()
                except Exception:
                    pass
            break

        if cmd == "close_browser":
            if bot:
                try:
                    bot.close()
                except Exception:
                    pass
                bot = None
                say("ack")
            else:
                say("ack", "Browser is not open.")
            continue

        def is_browser_dead(e):
            s = str(e).lower()
            return "invalid session" in s or "session deleted" in s or "disconnected" in s

        if cmd == "open_site":
            try:
                if bot is None:
                    bot = BrowserBot()
                bot.open_site(arg)
                say("ack")
            except Exception as e:
                if bot and is_browser_dead(e):
                    bot = None
                    say("ack", "Browser was closed. Say 'open <site>' or 'search' again and I'll open a new one.")
                else:
                    say("ack", "Could not open site. Try again or say 'close' then retry.")

        elif cmd == "search":
            try:
                if bot is None:
                    bot = BrowserBot()
                bot.open_site("https://google.com")
                time.sleep(1.5)
                bot.search_google(arg)
                say("ack")
            except Exception as e:
                if bot and is_browser_dead(e):
                    bot = None
                    say("ack", "Browser was closed. Say 'search <query>' again and I'll open a new one.")
                else:
                    say("ack", "Search failed. Try again or say 'close' then retry.")

        elif cmd == "news":
            try:
                say("ack", "Fetching Hacker News front page...")
                titles = get_titles("https://news.ycombinator.com")
                print()
                for i, t in enumerate(titles[:10], 1):
                    print(f"    {i}. {t}")
                print()
            except Exception as e:
                say("ack", f"Could not fetch news: {e}")

        elif cmd == "open_app":
            try:
                open_app(arg)
                say("ack")
            except Exception as e:
                say("ack", f"Could not open app: {e}")

        elif cmd == "workspace":
            try:
                open_workspace()
                say("ack")
            except Exception as e:
                say("ack", f"Could not launch workspace: {e}")

        elif cmd == "type":
            try:
                say("ack", "Typing in 2 seconds — focus the target window.")
                write_message(arg, delay_before=2)
            except Exception as e:
                say("ack", f"Typing failed: {e}")

        else:
            say("unknown")


if __name__ == "__main__":
    run_jarvis()
