import os
import time

def open_workspace():

    print("Starting your workspace...")

    os.system("code")

    time.sleep(2)

    os.system("start chrome https://kalvium.community")

    time.sleep(1)

    os.system("start brave https://youtube.com")

    os.system("start brave https://instagram.com")

    os.system("start brave https://linkedin.com")

    os.system("start brave https://github.com")

    print("Workspace launched successfully")


def main():

    while True:

        command = input("Command: ").lower()

        if command == "start":
            open_workspace()

        elif command == "exit":
            print("Exiting launcher")
            break

        else:
            print("Unknown command")


if __name__ == "__main__":
    main()