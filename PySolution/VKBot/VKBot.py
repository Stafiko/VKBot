# -*- coding: utf-8 -*-
import vk_api
import string
import re
from itertools import *
from vk_api.longpoll import VkLongPoll, VkEventType

login, password = '89870195625', '258262St'
vk = vk_api.VkApi(login, password)
whitelist = (25069332,'25069332')
class answer:
    def __init__(self, d, a):
        self.dict = d
        self.ans = a

ans_for_end = [ answer((u'тристо',u'триста',u'трицто',u'трицта',
	                    u'300',u'3оо',u'3о0',u'30о',
		                u'3сто',u'3ста',u'3цто',u'3цта',
		                u'три100',u'три1оо',u'три1о0',u'три10о'),u'отсоси у программиста'),
                answer((u'ет',),u'пидора ответ'),
                answer((u'да',),u'на хую борода')]

ans_for_last = [answer((u'куда',u'кида'),u'туда, куда не ходят поезда'),
                answer((u'тоже',u'тоге',u'тойе'),u'на говно похоже'),
                answer((u'где',),u'в караганде'),
                answer((u'ок',),u'пидора кусок'),
                answer((u'я',u'йа',u'иа'),u'головка от хуя'),
                answer((u'кек',),u'лол арбидол'),
                answer((u'лол',),u'кек чебурек')]

def del_repeats(match):
	return match.group(0)[0]

def write_chat(id, mes):
    vk.method('messages.send', {'chat_id':id,'message':mes})

def write_user(id, mes):
    vk.method('messages.send', {'user_id':id,'message':mes})

def maketrans_unicode(s1, s2, todel=""):
	trans_tab = dict( zip( map(ord, s1), map(ord, s2) ) )
	trans_tab.update( (ord(c),None) for c in todel )
	return trans_tab
	
def answer_mes(message, user_id, user_name, from_chat):
    if user_id in whitelist: return 'nope'
    if from_chat: preff = '@id'+str(user_id)+' ('+user_name+'), '
    else: preff = ''
    delimetrs = maketrans_unicode(
        u'qwertyuiopasdfghjklzxcvbnm',
        u'квертиуиопасдфгхйклзхцвбнм',
        string.punctuation+u'ьъ'+"!@#$%^&amp;*()-_=+{}[];:'&quot;&lt;&gt;,./?|\\")
    message = message.lower().translate(delimetrs)
    
    #300
    if message.endswith(tuple(ans_for_end[0].dict)): return preff+ans_for_end[0].ans

    message = message.translate(maketrans_unicode('','',string.digits))
    message = re.sub(r'(.)\1+', del_repeats, message)
    last_word = message.split(' ')[-1]
    message.replace(' ','')
    for e,l in izip_longest(ans_for_end,ans_for_last):
        if e != None and message.endswith(tuple(e.dict)): return preff+e.ans
        elif l != None and last_word in l.dict: return preff+l.ans
    return 'nope'

def main():
    try:
        vk.auth()
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return

    longpoll = VkLongPoll(vk)
    for event in longpoll.listen():

        if event.type == VkEventType.MESSAGE_NEW:
            print(u'Новое сообщение: ')
            user_name = vk.method('users.get', {'user_ids':event.user_id})[0]['first_name']
            mes = answer_mes(event.text, event.user_id, user_name, event.from_chat)
            print(u'От кого: ' + user_name)
            print(u'Ответочка: ' + mes)
            if event.from_me: print(u'От меня для: ')
            elif event.to_me: print(u'Для меня от: ')

            if event.from_user and event.to_me:
                if mes != 'nope': write_user(event.user_id, mes)
                print(event.user_id)
            elif event.from_chat and event.to_me:
                if mes != 'nope': write_chat(event.chat_id, mes)
                print(event.user_id, u' в беседе ', event.chat_id)
            elif event.from_group:
                print(u' группы ', event.group_id)

            print(u'Текст: ',event.text)

        elif event.type == VkEventType.USER_TYPING:
            print(u'Печатает ')

            if event.from_user: print(event.user_id)
            elif event.from_group: print(u' администратор группы ', event.group_id)

        elif event.type == VkEventType.USER_TYPING_IN_CHAT:
            print(u'Печатает ', event.user_id, u' в беседе ', event.chat_id)

        elif event.type == VkEventType.USER_ONLINE:
            print(u'Пользователь', event.user_id, u' онлайн ', event.platform)

        elif event.type == VkEventType.USER_OFFLINE:
            print(u'Пользователь', event.user_id, u' оффлайн ', event.offline_type)

        else:
            print(event.type, event.raw[1:])

if __name__ == '__main__':
    main()

