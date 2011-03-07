##   Copyright (C) 2011 Matthias Matousek <matou@taunusstein.net>
##
##   This program is free software; you can redistribute it and/or modify
##   it under the terms of the GNU General Public License as published by
##   the Free Software Foundation; either version 2, or (at your option)
##   any later version.
##
##   This program is distributed in the hope that it will be useful,
##   but WITHOUT ANY WARRANTY; without even the implied warranty of
##   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##   GNU General Public License for more details.

import xmpp, time, re, logging
from threading import Thread
from random import randint

class Mucbot(Thread):
    
    def __init__(self, jid, pwd, room, botname='', roompwd='', greeting=[], 
            quotes=[], minwait=-1, maxwait=-1, reactions={}, delay=3, 
            rcv_handler=[]):
        '''initalize bot and let it join the room'''
        Thread.__init__(self)

        if botname == '':
            botname = jid.getNode()

        # the jid of the bot
        self.jid = jid
        # the room to join
        self.room = room
        # the nick to appear with
        self.botname = botname
        # quotes to tell periodical
        self.quotes = quotes
        # minimum and maximum time to wait before quoting something
        self.minwait = minwait
        self.maxwait = maxwait
        # a dictionary containing reactions. the keys have to be 
        # regular expressions pattern as strings and the value a list of 
        # reactions from which one will be picked randomly. it's sufficient to
        # consider the lower case since every message body will be made lower
        # case before parsingiit.
        self.reactions = reactions
        # seconds to wait before replying
        self.delay = delay
        # a list of handlers that will be executed when a message is received
        self.rcv_handler = rcv_handler
        # a list of possible greetings when the bot enters a room
        self.greeting = greeting

        # compile the patterns
        for key in self.reactions.keys():
            self.reactions[re.compile(key)] = self.reactions.pop(key)

        self.client = xmpp.Client(jid.getDomain(), debug=[])
        self.client.connect()
        self.client.RegisterHandler('message', self.msg_rcv)
        self.client.RegisterHandler('presence', self.pres_rcv)
        self.client.auth(jid.getNode(), pwd, resource=jid.getResource())
        p = xmpp.Presence(to='%s/%s' % (room, botname))
        p.setTag('x', namespace=xmpp.NS_MUC).setTagData('password', roompwd)
        p.getTag('x').addChild('history', {'maxchars':'0', 'maxstanzas':'0'})
        self.client.send(p)

        logging.info('%s joined %s' % (botname, room))

    def msg_rcv(self, sess, msg):
        '''will be executed when a message arrives'''

        logging.debug('received message')

        # ignore messages that come from this bot
        sender = str(msg.getFrom())
        if len(sender.split('/')) > 1:
            sender = sender.split('/')[1]
        if sender.lower().find(self.botname) >= 0:
            return


        # first execute all given handlers
        for handler in self.rcv_handler:
            handler(self, msg.getFrom(), msg.getBody())

        self.react(msg.getBody())

    def react(self, msg):
        '''react to a message by searching for all patterns and replying with
        the matching answer'''
        logging.debug(msg)
        msg = msg.lower()
        time.sleep(self.delay)
        for pattern in self.reactions.keys():
            if pattern.search(msg):
                self.say(self.reactions[pattern][randint(0,len(self.reactions[pattern])-1)])
                return

    def pres_rcv(self, sess, pres):
        pass

    def say(self, msg):
        '''send the given message to the room'''
        m = xmpp.Message(to=self.room, body=msg, typ='groupchat')
        self.client.send(m)

    def getClient(self):
        return self.client

    def processing(self):
        while True:
            self.client.Process(1)

    def run(self):
        processor = Thread()
        processor.run = self.processing
        processor.start()
        time.sleep(self.delay)
        if len(self.greeting) > 0:
            self.say(self.greeting[randint(0, len(self.greeting)-1)])
        if self.minwait==-1 or self.maxwait==-1:
            return
        while True:
            r = randint(self.minwait, self.maxwait)
            logging.info('waiting %d seconds before next quote' % r)
            time.sleep(r)
            self.say(self.quotes[randint(0,len(self.quotes)-1)])



if __name__ == '__main__':

    jid = xmpp.JID('user@jabber.example.org')
    pwd = 'mypassword'
    room = 'room@conference.jabber.example.org'

    examplebot = Mucbot(jid, pwd, room)
    examplebot.say("hello world")

    time.sleep(1)
