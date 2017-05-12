# -*- coding: utf-8 -*-
import datetime
import vk_api
import re
import string
from itertools import *
from vk_api.longpoll import VkLongPoll, VkEventType

login, password = '89870195625', '258262St'
vk = vk_api.VkApi(login, password)

class answer:
    def __init__(self, d, a):
        self.dict = d
        self.ans = a

nope = "nope"
empty = [answer([],'')]
whitelist = []
blacklist = []
ans_for_end = []
ans_for_last = []
ans_vasiliy_info = []
ans_vasiliy_predm = []

def chat_preff(chat,user_id,user_name):
    if chat: return '@id'+str(user_id)+' ('+user_name+'), '
    else: return ''

def del_repeats(match):
	return match.group(0)[0]

def write(id, mes, chat):
    if chat: to='chat_id'
    else: to='user_id'
    vk.method('messages.send', {to:int(id),'message':mes})

def file(id, file, chat):
    if chat: to='chat_id'
    else: to='user_id'
    vk.method('messages.send', {to:int(id),'message':'...','attachment':file})

def answer_bad(message, user_name, user_id, chat_id):
    chat = chat_id != nope
    if int(user_id) in whitelist or message.lower().endswith(tuple(ans_vasiliy_info[0].dict)): return nope
    preff = chat_preff(chat,user_id,user_name)
    delimetrs = str.maketrans(
        'qwertyuiopasdfghjklzxcvbnm',
        'квертиуиопасдфгхйклзхцвбнм',
        string.punctuation+'ъ'+"!@#$%^&amp;*()-_=+{}[];:'&quot;&lt;&gt;,./?|\\")
    message = message.lower().translate(delimetrs)
    
    #300
    if message.endswith(tuple(ans_for_end[0].dict)): return preff+ans_for_end[0].ans

    message = message.translate(str.maketrans('','',string.digits))
    message = re.sub(r'(.)\1+', del_repeats, message)
    last_word = message.split(' ')[-1]
    message.replace(' ','')
    for e,l in zip_longest(ans_for_end,ans_for_last):
        if e != None and message.endswith(tuple(e.dict)): return preff+e.ans
        elif l != None and last_word in l.dict: return preff+l.ans
    return nope

def search_good(ans, user_id, chat_id):
    result = ''
    chat = chat_id != nope
    for a in ans.ans:
        if a.startswith('file'): 
            f = a.split('.')[1]
            if chat: file(chat_id,f,True)
            else: file(user_id,f,False)
        else: result = result + a + '\n'
    return result

def answer_good(message, user_name, user_id, chat_id):
    chat = chat_id != nope
    vasiliy = 'id427817510'
    preff = chat_preff(chat_id,user_id,user_name)
    mes = ""
    messages = message.lower().split(' ')
    if int(user_id) in blacklist: return nope
    #Dikaya vlojennost
    if vasiliy in message or not chat:
        if chat: mes = preff
        for m in messages:
            for i,p in zip_longest(ans_vasiliy_info,ans_vasiliy_predm):
                if i != None and m in i.dict: mes = mes + search_good(i, user_id, chat_id)
                elif p != None and m in p.dict: mes = mes + search_good(p, user_id, chat_id)
        return mes    
    return nope

def main():
    try:
        vk.auth()
    except:
        print(error_msg)
        return
    print('Бот запущен')
    longpoll = VkLongPoll(vk)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            print('Новое сообщение: ')
            if event.from_me: print('От меня для:')
            elif event.to_me: 
                print('Для меня от:')
                user_name = vk.method('users.get', {'user_ids':event.user_id})[0]['first_name']
                if event.from_user: chat = nope
                else: chat = event.chat_id
                bad_mes = answer_bad(event.text, user_name, event.user_id, chat)
                good_mes = answer_good(event.text, user_name, event.user_id, chat)
                print(user_name)
                print('Ответочка:',bad_mes,good_mes)

            if event.from_user and event.to_me:
                if bad_mes != nope: write(event.user_id, bad_mes, False)
                elif good_mes != nope: write(event.user_id, good_mes, False)
                print(event.user_id)
            elif event.from_chat and event.to_me:
                if bad_mes != nope: write(event.chat_id, bad_mes, True)
                elif good_mes != nope: write(event.chat_id, good_mes, True)
                print(event.user_id, 'в беседе', event.chat_id)
            elif event.from_group:
                print('группы', event.group_id)

            print('Текст:',event.text)

        elif event.type == VkEventType.USER_TYPING:
            print('Печатает ')

            if event.from_user: print(event.user_id)
            elif event.from_group: print('администратор группы', event.group_id)

        elif event.type == VkEventType.USER_TYPING_IN_CHAT:
            print('Печатает', event.user_id, 'в беседе', event.chat_id)

        elif event.type == VkEventType.USER_ONLINE:
            print('Пользователь', event.user_id, 'онлайн', event.platform)

        elif event.type == VkEventType.USER_OFFLINE:
            print('Пользователь', event.user_id, 'оффлайн', event.offline_type)

        else:
            print(event.type, event.raw[1:])

def load():
    f = open('Data/answers.dat')
    for line in f:
        splits = line.split('^')
        splits[1] = splits[1].split(';')
        to = splits[0]
        dict = splits[1][0].split(',')
        ans = splits[1][1].split('.')[0]

        if to == 'e': ans_for_end.append(answer(dict,ans))
        if to == 'l': ans_for_last.append(answer(dict,ans))

    f = open('Data/info.dat')
    info = []
    predm = []
    for line in f:
        splits = line.split('^')
        splits[1] = splits[1].split(';')
        to = splits[0]
        dict = splits[1][0].split(',') 
        ans = splits[1][1].split("'")
        ans.pop()

        if to == 'i': 
            info.extend(dict)
            ans_vasiliy_info.append(answer(dict,ans))
        if to == 'p': 
            predm.extend(dict)
            ans_vasiliy_predm.append(answer(dict,ans))
    ans_vasiliy_info[0].ans.extend(info) #hello message
    ans_vasiliy_info[1].ans.extend(predm) #predm message

    f = open('Data/users.dat')
    for line in f:
        splits = line.split('^')
        to = splits[0]
        ids = splits[1].split(',')
        ids.pop()

        if to == 'w': whitelist.extend(ids)
        if to == 'b': blacklist.extend(ids)
    f.close()
    print('Данные загружены')

if __name__ == '__main__':
    load()
    main()

