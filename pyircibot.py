#!/usr/bin/python

import socket
import random
import ssl


class PyIrciBot(object):
    '''This class provide helper to connect and act on IRC.
    It can be useful to develop an IRC botnet.
    You can provide your own class using `use_parser_class` method
    with the following methods:

    - `__init__(nick, channel)`: this is for instantiation
    - `set_channel(channel)`: will provide you the channel name
    - `set_nick(nick)`: will provide you the nick (also if changed by a request)
    - `parse_raw(text)`: this will be called for every received raw message
    - `parse_message(message, source, target)`: this is called for the received PRIVMSG messages
    - `timeout_function()`: this is called if nothing is received within a timeout if non blocking mode

    `parse_raw()`, `parse_message` and `timeout_function()` can return a dictionary with the following possible commands:
        - 'cmd': request to execute a command with possible values:
            - 'end': will stop the IRC bot
            - a dictionary with possible keys:
                -'mode': a mode to set for the bot given in value
                -'away': change status to away with message in value
                -'message': send a message stored in value to the
                    value of the key 'target' if exists else to the channel
                -'nick': change nickname to the value
                -'join': join the provided channel in value
                -'send': send a raw IRC command stored in value
    Note that all your functions should not be blocking as it run in the same thread.

    '''

    def __init__(self, server, channel=None, nick=None, port=6667, ssl=False):
        '''Initializes data

        @param server: the IRC server to connect
        @param channel: a channel join
        @param nick: a nickname. if not given, a nickname will be generated 
        with 5 random hexa digits like 'pyircibot_5fa8b'
        @param port: the port to connect to the server
        @param ssl: use or not SSL

        '''
        self.server = server
        self.channel = channel
        if nick == None:
            random.seed()
            nhash = "".join([hex(random.randint(0,15)).replace('0x', '') for _ in range(5)])
            self.nick = "pyircibot_" + nhash
        else:
            self.nick = nick
        self.port = port
        self.ssl = ssl
        self.parser_obj = None
        self.timeout_use_class = False
        self.timeout_function = None

    def use_parser_class(self, pclass, *args, **kwargs):
        '''Sets a parser class and instantiate it. It will be used to parse and proceed IRC data.

        @param pclass: the parser class that will be instantiated adding at least nick and channel parameters
        @param *args: other pclass parameters to add for instantiation
        @param *kwargs: other pclass parameters to add for instantiation

        '''
        self.parser_obj = pclass(nick=self.nick, channel=self.channel, *args, **kwargs)

    def connect(self, timeout_function=None, timeout_use_class=False, timeout=1):
        '''Connects to the IRC server. If a channel was set, then it will join it.

        @param timeout_function: if set then the receive function will be non-blocking with
        a timeout set to `timeout` value. If the timeout is raised, then the function
        `timeout_function` will be executed. Don't use it when `timeout_use_class` is set to True.
        Note: If the function return not None and if the result is a string, it will be used as an
        IRC received message, and if it is a dict so it will be used as in parse message function.
        @type timeout_function: callable
        @param timeout_use_class: is True, the receive function will be non-blocking with a
        a timeout set to `timeout`. The parser class's method `timeout_function` will be called
        when the timeout is reached. So the class should be set before running and should
        contain a method with the appropriate name.
        Note: If the function return not None and if the result is a string, it will be used as an
        IRC received message, and if it is a dict so it will be used as in parse message function.
        @type timeout_use_class: bool
        @param timeout: the timeout value in seconds to wait for receiving data
        in non-blocking mode

        '''
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print ("connecting to:"+self.server)
        if self.ssl:
            self.irc = ssl.wrap_socket(self.irc, cert_reqs=ssl.CERT_NONE)
            print("using SSL")
        self.irc.connect((self.server, self.port))
        if timeout_function or timeout_use_class:
            self.irc.settimeout(timeout)
            if timeout_function:
                self.timeout_function = timeout_function
            else:
                self.timeout_use_class = timeout_use_class
        self.irc.send("USER "+ self.nick +" "+ self.nick +" "+ self.nick +" :This is a PyIrciBot!\n")
        self.irc.send("NICK "+ self.nick +"\n")
#        self.irc.send("PRIVMSG nickserv :iNOOPE\r\n")
        if self.channel:
            self.irc.send("JOIN "+ self.channel +"\n")
            if self.parser_obj:
                try:
                    self.parser_obj.set_channel(self.channel)
                except:
                    pass

    def join(self, channel):
        '''Joins a channel

        @param channel: the channel to join

        '''
#TODO: how to manage several channels
        self.irc.send("JOIN "+ str(channel) +"\n")

    def mode(self, mode):
        '''Sets a mode

        @param mode: the mode to set (i.e.: "+v" or "-v", ...)

        '''
        m = "MODE "+ str(self.nick) + ' ' + mode + "\n"
        self.irc.send(m)
        self.irc.send("PRIVMSG " + self.channel + "==>>" + m)

    def message(self, message, target):
        '''Send a message to a target that can be a user or a channel.

        @param message: the message to send
        @param target: the target
        
        '''
        if '\n' in message:
            for msg in message.split('\n'):
                self.irc.send("PRIVMSG " + target + " :" + msg + '\n')
        else:
            self.irc.send("PRIVMSG " + target + " :" + message + '\n')

    def run(self, parse_message=None, parse_raw_data=None):
        '''Run in an infinit loop receiving irc messages and responding to PINGs. 
        Callbacks can be given to do additional process.

        @param parse_message: if given, function to parse a received privmsg. 
        The data is given in parameter. If 'end' id returned then the loop will end.
        @param parse_raw_data: if given, function to parse received raw received data. 
        The provided parameters are respectively: 
            the message typed, 
            the nickname of the writer, 
            the target (the channel or the nick of the bot).
        If 'end' id returned then the loop will end.

        '''
        running = True
        while running:
            res = ''
            # receive an IRC message
            try:
                text = self.irc.recv(2048)

            # if non blocking and reached timeout run user callback function
            except (socket.timeout, ssl.SSLError) as e:
                result = None
                if self.timeout_function:
                    try:
                        result = self.timeout_function()
                    except:
                        print("Warning: failed to run timeout_function()")
                elif self.timeout_use_class:
                    try:
                        result = self.parser_obj.timeout_function()
                    except:
                        print("Warning: failed to run the parser class timeout_function()")
                if result and type(result) is str:
                    text = result
                elif result and type(result) is dict:
                    res = result
                    text = ''
                else:
                    continue

            # response to the ping (mandatory to not be kicked)
            if 'PING' in text:
                self.irc.send('PONG ' + text.split()[1] + '\r\n')

            # run user callback function for raw data
            if text and self.parser_obj:
                try:
                    res = self.parser_obj.parse_raw(text)
                except:
                    pass
            if text and parse_raw_data:
                res = parse_raw_data(text)

            # run user callback function for interpreted IRC message (message, target, source)
            if 'PRIVMSG' in text: 
                lst = text.split()
                nick = lst[0].strip().split("!")[0][1:]
                target = lst[2]
                msg = " ".join(lst[3:])[1:].strip()
                if self.parser_obj:
                    res = self.parser_obj.parse_message(msg, nick, target)
                if parse_message:
                    res = parse_message(msg, nick, target)

            # proceed user requests

            if type(res) is dict:
                if 'cmd' in res:
                    if res['cmd'] == 'end':
                        running = False
                    # List of available commands:
                    #
                    #  - 'mode': sets the provided mode
                    #  - 'away': change to away with the provided message
                    #  - 'message': send a message provided to a target if
                    #               key 'target' exists else to the channel
                    #  - 'nick': change nickname to the provided one
                    #  - 'send': send the provided raw irc command
                    #  - 'join': join the provided channel
                    #  - 'end': will stop the bot. the provided value is ignored
                    #
                    elif type(res['cmd']) is dict:
                        if 'mode' in res['cmd']:
                            mode = res['cmd']['mode']
                            self.mode(mode)
                        if 'away' in res['cmd']:
                            self.irc.send('AWAY ' + res['cmd']['away'] + '\n')
                        if 'message' in res['cmd']:
                            if 'target' not in res['cmd']:
                                res['cmd']['target'] = self.channel
                            self.message(res['cmd']['message'], res['cmd']['target'])
                        if 'nick' in res['cmd']:
                            self.irc.send('NICK ' + res['cmd']['nick'] + '\n')
                            if self.parser_obj:
                                self.parser_obj.set_nick(res['cmd']['nick'])
                        if 'send' in res['cmd']:
                            self.irc.send(res['cmd']['send'] + '\n')
                        if 'join' in res['cmd']:
                            self.join(res['cmd']['join'])
                        if 'end' in res['cmd']:
                            running = False
            elif res == 'end':
                running = False
            elif res and res.startswith("cmd"): #TODO: is this necessary???
                cmd = res[3:]
                if cmd.startswith("mode"):
                    mode = cmd.replace("mode", "")
                    self.mode(mode)
            elif res:
                print ("Warning: unknown action for res=" + str(res))
