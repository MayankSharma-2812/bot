"""
Jarvis Bot — Your personal assistant.
Responds to text commands: open sites, search, get news, open apps, type text, launch workspace.
Uses OpenClaw AI for natural-language questions when OpenClaw gateway is running.
"""
import os
import random
import re
import subprocess
import time
import requests
from automation import BrowserBot, write_message, open_app
from scraper import get_titles
from workspace_launcher import open_workspace

# OpenClaw: set OPENCLAW_BASE_URL (default http://127.0.0.1:18789) and optionally OPENCLAW_GATEWAY_TOKEN
OPENCLAW_BASE_URL = os.environ.get("OPENCLAW_BASE_URL", "http://127.0.0.1:18789").rstrip("/")
OPENCLAW_TOKEN = os.environ.get("OPENCLAW_GATEWAY_TOKEN") or os.environ.get("OPENCLAW_TOKEN") or "556169250df6ecc690d82c22506b22aa0df844e0dbc64112"
OPENCLAW_CHAT_URL = f"{OPENCLAW_BASE_URL}/v1/chat/completions"
OPENCLAW_AGENT = os.environ.get("OPENCLAW_AGENT", "main")

# Check if OpenClaw gateway is running
def is_openclaw_running():
    """Check if OpenClaw gateway is responsive"""
    try:
        import requests
        # Try the health endpoint first, then fallback to chat completions
        try:
            response = requests.get(f"{OPENCLAW_BASE_URL}/health", timeout=5)
            return response.status_code == 200
        except:
            # Fallback: try the chat completions endpoint
            headers = {"Content-Type": "application/json"}
            if OPENCLAW_TOKEN:
                headers["Authorization"] = f"Bearer {OPENCLAW_TOKEN}"
            response = requests.post(
                f"{OPENCLAW_CHAT_URL}",
                json={"model": f"openclaw:{OPENCLAW_AGENT}", "messages": [{"role": "user", "content": "test"}]},
                headers=headers,
                timeout=5,
            )
            return response.status_code == 200
    except:
        return False

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
        "I'm not sure how to do that. Try: start, open, search, news, type, close, exit — or ask a question for AI.",
    ],
}


def say(key, custom=None):
    if custom:
        print(f"  Jarvis: {custom}")
        return
    print(f"  Jarvis: {random.choice(REPLIES[key])}")


def get_openclaw_response(query: str, timeout: int = 120) -> str | None:
    """Send query to OpenClaw gateway (OpenAI-compatible). Returns reply text or None on failure."""
    headers = {"Content-Type": "application/json"}
    if OPENCLAW_TOKEN:
        headers["Authorization"] = f"Bearer {OPENCLAW_TOKEN}"
    payload = {
        "model": f"openclaw:{OPENCLAW_AGENT}",
        "messages": [{"role": "user", "content": query}],
    }
    try:
        r = requests.post(
            OPENCLAW_CHAT_URL,
            json=payload,
            headers=headers,
            timeout=timeout,
        )
        r.raise_for_status()
        data = r.json()
        choice = data.get("choices") and data["choices"][0]
        if not choice:
            return None
        msg = choice.get("message") or {}
        return (msg.get("content") or "").strip() or None
    except requests.exceptions.RequestException:
        return None
    except (KeyError, IndexError, TypeError):
        return None


def parse_command(line):
    raw = line.strip()
    line_lower = raw.lower()
    if not raw:
        return None, None
    # exit / goodbye
    if line_lower in ("exit", "quit", "goodbye", "close jarvis", "shut down"):
        return "exit", None
    # close browser only
    if line_lower in ("close", "close browser"):
        return "close_browser", None
    # openclaw gateway = launch OpenClaw gateway in background
    if line_lower in ("openclaw start", "start openclaw", "openclaw gateway", "gateway openclaw"):
        return "openclaw_start", None
    # openclaw status = check if OpenClaw is running
    if line_lower in ("openclaw status", "status openclaw", "check openclaw"):
        return "openclaw_status", None
    # start = full workspace launch (VS Code + Chrome/Brave sites)
    if line_lower == "start":
        return "workspace", None
    # open <site or app>
    m = re.match(r"^open\s+(.+)$", line_lower)
    if m:
        target = m.group(1).strip().lower()
        rest = raw[5:].strip()  # preserve casing after "open "
        if target in ("workspace", "my workspace"):
            return "workspace", None
        if target in KNOWN_APPS:
            return "open_app", KNOWN_APPS[target]
        return "open_site", rest
    # search <query>
    m = re.match(r"^search\s+(.+)$", line_lower)
    if m:
        return "search", raw[7:].strip()  # preserve casing after "search "
    # news / hacker news / get news
    if re.match(r"^(get\s+)?(news|hacker\s*news)$", line_lower):
        return "news", None
    # type <message> or write <message>
    m = re.match(r"^(?:type|write)\s+(.+)$", line_lower)
    if m:
        return "type", raw[m.start(1):].strip()
    # anything else → ask OpenClaw AI
    return "ask", raw


def run_jarvis():
    print("\n  ———————————————————————————")
    print("  JARVIS  —  At your service.")
    print("  ———————————————————————————")
    print("  Commands: start | open <site|app|workspace> | search <query> | news | type <text> | close | exit")
    print("  OpenClaw: 'openclaw start' | 'openclaw status' | ask any question for AI response")
    print("  start = launch workspace (VS Code + Chrome: kalvium | Brave: youtube, instagram, linkedin, github, leetcode)")
    print("  Apps: code, notepad, chrome, brave, edge, tlauncher, file explorer")
    print("  Ask anything else for AI assistance via OpenClaw.\n")

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

        elif cmd == "openclaw_start":
            try:
                if os.name == "nt":
                    # Use cmd.exe so we don't hit PowerShell script execution policy
                    subprocess.Popen(
                        "cmd /c npx openclaw gateway",
                        creationflags=subprocess.CREATE_NEW_CONSOLE,
                        stdin=subprocess.DEVNULL,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                else:
                    subprocess.Popen(
                        ["npx", "openclaw", "gateway"],
                        stdin=subprocess.DEVNULL,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                say("ack", "Starting OpenClaw gateway in a new window. Give it a few seconds, then ask your question.")
            except FileNotFoundError:
                say("ack", "npx not found. Install Node.js or run 'openclaw gateway' in another terminal.")
            except Exception as e:
                say("ack", f"Could not start OpenClaw: {e}")

        elif cmd == "openclaw_status":
            if is_openclaw_running():
                say("ack", f"OpenClaw gateway is running at {OPENCLAW_BASE_URL}")
            else:
                say("ack", f"OpenClaw gateway is not running. Say 'openclaw start' to launch it.")

        elif cmd == "type":
            try:
                say("ack", "Typing in 2 seconds — focus the target window.")
                write_message(arg, delay_before=2)
            except Exception as e:
                say("ack", f"Typing failed: {e}")

        elif cmd == "ask":
            # Check if OpenClaw is running before making request
            if not is_openclaw_running():
                say("ack", "OpenClaw gateway is not running. Starting it now...")
                # Auto-start OpenClaw
                try:
                    if os.name == "nt":
                        subprocess.Popen(
                            "cmd /c npx openclaw gateway",
                            creationflags=subprocess.CREATE_NEW_CONSOLE,
                            stdin=subprocess.DEVNULL,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                        )
                    else:
                        subprocess.Popen(
                            ["npx", "openclaw", "gateway"],
                            stdin=subprocess.DEVNULL,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                        )
                    say("ack", "OpenClaw gateway starting. Please wait 10 seconds, then ask your question again.")
                    continue
                except Exception as e:
                    say("ack", f"Could not start OpenClaw: {e}")
                    continue
            
            reply = get_openclaw_response(arg)
            if not reply:
                say("ack", "Connecting to OpenClaw...")
                for _ in range(3):
                    time.sleep(3)
                    reply = get_openclaw_response(arg)
                    if reply:
                        break
            if reply:
                print("  Jarvis: " + reply.replace("\n", "\n  "))
            else:
                say(
                    "ack",
                    "OpenClaw isn't responding. Check: (1) Gateway window opened and shows no errors. "
                    "(2) In OpenClaw config, set gateway.http.endpoints.chatCompletions.enabled = true. "
                    "(3) OPENCLAW_BASE_URL (default http://127.0.0.1:18789) and OPENCLAW_GATEWAY_TOKEN if you use auth. "
                    "To start it manually: openclaw gateway",
                )

        else:
            say("unknown")


if __name__ == "__main__":
    run_jarvis()
