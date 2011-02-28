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

import xmpp, time
from threading import Thread

class Mucbot(Thread):
    
    def __init__(self, jid, pwd, room, botname='', roompwd=''):
        '''initalize bot and let it join the room'''
        Thread.__init__(self)

        if botname == '':
            botname = jid.getNode()

        self.jid = jid
        self.room = room
        self.botname = botname

        self.client = xmpp.Client(jid.getDomain(), debug=[])
        self.client.connect()
        self.client.RegisterHandler('message', self.msg_rcv)
        self.client.RegisterHandler('presence', self.pres_rcv)
        self.client.auth(jid.getNode(), pwd, resource=jid.getResource())
        p = xmpp.Presence(to='%s/%s' % (room, botname))
        p.setTag('x', namespace=xmpp.NS_MUC).setTagData('password', roompwd)
        p.getTag('x').addChild('history', {'maxchars':'0', 'maxstanzas':'0'})
        self.client.send(p)

    def msg_rcv(self, sess, msg):
        '''will be executed when a message arrives'''
        pass

    def pres_rcv(self, sess, pres):
        pass

    def say(self, msg):
        '''send the given message to the room'''
        m = xmpp.Message(to=self.room, body=msg, typ='groupchat')
        self.client.send(m)

    def getClient(self):
        return self.client

    def run(self):
        pass


if __name__ == '__main__':

    jid = xmpp.JID('user@jabber.example.org')
    pwd = 'mypassword'
    room = 'room@conference.jabber.example.org'

    examplebot = Mucbot(jid, pwd, room)
    examplebot.say("hello world")

    time.sleep(1)
