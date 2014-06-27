from time import time
from pyircibot import PyIrciBot


class Mybot(object):
    '''Example of user bot class to test PyIrciBot.
    It will print all received IRC raw data (see `parse_raw()`).
    It will print all channel messages with a particular format,
    making distinction between messages addressed to the bot and
    other messages. And it will interprete private messages:
    STOP, MODE, NICK, AWAY, SEND, and request actions depending
    on the previous commands (see `parse_message()`).
    When no activity the `timeout_function()` will print a message
    and after 2 minutes of running it will request to stop.

    '''

    def __init__(self, nick=None, channel=None):
        '''Init the data

        '''
        self.channel = channel
        self.nick = nick
        self.init_time = time()

    def set_nick(self, nick):
        '''Sets the nick. This will be called by PyIrciBot to update the nickname.

        @param nick: the nick name
        
        '''
        self.nick = nick

    def set_channel(self, channel):
        '''Sets the channel. This will be called by PyIrciBot to update the channel.

        @param channel: the channel name
        
        '''
        self.channel = channel

    def parse_raw(self, data):
        '''Proceeds raw data. This will be called by PyIrciBot.

        '''
        print "---" + data.strip() + "---"

    def timeout_function(self):
        '''Will check the duration since instanciation.
        After 2 minutes it will send order to stop.
        This will be called by PyIrciBot at each timeout if
        non blocking mode is set to the PyIrciBot connect method.

        '''
        print "after 2 minutes stop %s from %s" % (self.nick, self.channel)
        if time() - self.init_time > 120:
            return {"cmd": {'end': '', 
                            'message': "2 minutes passed I stop, bye ;)"}
                   }

    def parse_message(self, message, source, target):
        '''Proceeds a message received with PRIVMSG. This will be called by PyIrciBot
        Will react if the following are found in the message:
            -'STOP': will send stop request to the bot
            -'MODE': will send the given IRC mode request to the bot
            -'AWAY': will send the message to put with the away instruction request to the bot
            -'SEND': will send an IRC raw message request to the bot
            -'NICK': request to change nick name

        @param message: the message
        @param source: the sender of the message
        @param target: the target of the message (might be the channel or the bot)
        @return: None or a dictionary with keys:
            - 'cmd': request to execute a command with possible values:
                - 'end': will stop the IRC bot
                - a dictionary with possible keys:
                    -'mode': a mode to set for the bot given in value
                    -'away': change status to away with message in value
                    -'message': send a message stored in value to the 
                        value of the key 'target' if exists else to the channel
                    -'nick': change nickname to the value
                    -'send': send a raw IRC command stored in value

        '''
        if not target.startswith('#'):
            # Private message
            if 'STOP' in message:
                print ("I was asked to stop!")
                return {'cmd': {'end': '', 'message': 'bye!'}}
            if 'MODE' in message:
                return {'cmd': {'mode': message.replace('MODE', '').strip()}}
            if 'AWAY' in message:
                return {'cmd': {'away': message.replace('AWAY', '').strip()}}
            if 'NICK' in message:
                return {'cmd': {'nick': message.replace('NICK', '').strip()}}
            if 'SEND' in message:
                return {'cmd': {'send': message.replace('SEND', '').strip()}}
            print "*" + str(source) + "*" + " => '" + message + "'"
            
        else:
            # Channel message
            if message.startswith(self.nick) and not message.replace(self.nick, '')[0].isalnum():
                print ">>" + str(source) + "<<" + " *TOLD ME* " + "'" + message + "'"
            else:
                print ">>" + str(source) + "<<" + " *SAID* " + "'" + message + "'"


# Following example functions that can be provided instead of providing the class to PyIrciBot

def parse_raw(data):
    print "--->>> " + str(data)

def parse_message(msg, nick, target):
    if not target.startswith('#'):
        if 'STOP' in msg:
            return 'end'
        if 'MODE' in msg:
            return 'cmdmode' + msg.replace('MODE', '').strip()
        print "*" + str(nick) + "*" + " => '" + msg + "'"
    else:
        print ">>" + str(nick) + "<<" + " *SAID* " + "'" + msg + "'"

def timeout_function():
    print "timeout"

if __name__ == '__main__':
    server = "irc.freenode.org"
    channel = "#testpyircibot"
    botnick = "pyircibot"
    bot = PyIrciBot(server, channel, botnick)
    bot.connect(timeout_use_class=True)
    #bot.connect(timeout_function=timeout_function)
    bot.use_parser_class(Mybot)
    bot.run()
    #bot.run(parse_message=parse_message, parse_raw_data=parse_raw)
