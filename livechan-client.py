import urllib
import urllib2
import cookielib
import os
import json
from socketIO_client import SocketIO
import curses
import thread
import time

cookies = cookielib.LWPCookieJar()
handlers = [
    urllib2.HTTPHandler(),
    urllib2.HTTPSHandler(),
    urllib2.HTTPCookieProcessor(cookies)
    ]
opener = urllib2.build_opener(*handlers)

def fetch(uri):
    req = urllib2.Request(uri)
    return opener.open(req)

def post(uri, params):
    data = urllib.urlencode(params)
    req = urllib2.Request(uri, data)
    return opener.open(req)

def dump():
    for cookie in cookies:
        print cookie.name, "=", cookie.value

def get_password():
    for cookie in cookies:
        if cookie.name == "password_livechan":
            return cookie.value
    return ""

def post_chat(body, chat, name="Anonymous", convo="General", trip=""):
    post_params = {}
    post_params["name"] = name
    post_params["trip"] = trip
    post_params["body"] = body
    post_params["convo"] = convo
    post_params["chat"] = chat
    return post('https://livechan.net/chat/'+chat, post_params)

def login():
    image_response = fetch('https://livechan.net/captcha.jpg')
    image_data = image_response.read()

    with open('captcha.jpg', 'w') as f:
        f.write(image_data)
    os.system("open captcha.jpg")

    digits = int(raw_input("enter the captcha: "))
    post_params = {}
    post_params["digits"] = digits
    login_response = post('https://livechan.net/login', post_params)
    login_html = login_response.read()

    print login_html
    livechan_pass = get_password()
    if livechan_pass == "":
        login()
    return livechan_pass

def get_data(chat):
    data_response = fetch('https://livechan.net/data/'+chat)
    json_data = json.loads(data_response.read())
    for i in json_data[::-1]:
        print i[u"name"]
        print i[u"body"]
        print

def main_chat(chat):
    chat_body = raw_input("> ")
    mainresp = post_chat(chat_body, chat)
    print mainresp.read()

def on_chat(*args):
    print 'chat', args

def on_user_count(*args):
    print 'chat', args

#import logging
#logging.basicConfig(level=logging.DEBUG)

#login
cookie = login()

chat_room = raw_input("choose room: ")
print
get_data(chat_room)

socketIO = SocketIO('https://livechan.net',
        cookies={'password_livechan': cookie})

socketIO.on('chat', on_chat)
socketIO.on('user_count', on_user_count)
socketIO.emit('subscribe', chat_room);

thread.start_new_thread ( socketIO.wait, () )

#stdscr = curses.initscr()
#curses.noecho()
#curses.cbreak()
#stdscr.keypad(1)

while(True):
    main_chat(chat_room)
    time.sleep(7)

#main_chat(chat_room)

print "done"


