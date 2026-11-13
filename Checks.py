# Checks.py - minimal version
# Only required checks: internet and PHP.
# ngrok is managed manually by the user, not by this tool.
from os import system
from time import sleep

RED, WHITE, CYAN, GREEN, DEFAULT, YELLOW = '\033[91m', '\033[46m', '\033[36m', '\033[1;32m', '\033[0m', '\033[1;33m'


def net():
    print("\n{0}[{2}#{0}] {2}Checking for internet connection...{4}".format(RED, WHITE, CYAN, GREEN, DEFAULT, YELLOW))
    if system('wget -q --spider http://google.com') == 0:
        print("{0}[{2}#{0}] {3}INTERNET {0}- {3}[{2}CONNECTED{3}]{4}".format(RED, WHITE, CYAN, GREEN, DEFAULT, YELLOW))
    else:
        print("{0}[{2}#{0}] {3}INTERNET {0}- {3}[{2}NOT-CONNECTED{3}]{4}".format(RED, WHITE, CYAN, GREEN, DEFAULT, YELLOW))
        print("{0}[{2}#{0}] {2}Turn on your internet connection and try again.{4}\n".format(RED, WHITE, CYAN, GREEN, DEFAULT, YELLOW))
        exit()


def checkPHP():
    if 256 != system('which php > /dev/null'):
        print(" {0}[{2}*{0}] {2}PHP INSTALLATION FOUND.....{4}".format(RED, WHITE, CYAN, GREEN, DEFAULT, YELLOW))
        sleep(0.5)
    else:
        print("{0}[{2}*{0}] {2}PHP NOT FOUND, installing...{4}".format(RED, WHITE, CYAN, GREEN, DEFAULT, YELLOW))
        system('apt-get install php -y > /dev/null')
        if 256 == system('which php > /dev/null'):
            print(" {0}[{2}*{0}] {2}Could not install PHP. Install it manually.{4}".format(RED, WHITE, CYAN, GREEN, DEFAULT, YELLOW))
            exit()
        sleep(0.5)
