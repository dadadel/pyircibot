PyIrciBot
=========

This is a Python IRC client helping to create IRC botnets.

There is no inheritance. You write a class doing things with some methods with a particular name returning a particular dictionary and you provide that class to PyIrciBot.
Then you run it and it is done!
It is also possible to write some functions that are given to PyIrciBot instead of providing a class.

Howto
-----

You can refer to `testbot.py <https://github.com/dadadel/pyircibot/blob/master/testbot.py>`_ to see an example of use.

- Example of use

The basic usage is:

.. code-block:: python

    from pyircibot import PyIrciBot
    bot = PyIrciBot("irc.server.org", "#channel")
    bot.connect()

And that step we are connected to the server "irc.server.org" and to the channel "#channel".
As no nick name was provided, a random one was generated.
Note that the bot won't do anything and it will probably be kicked as it won't
answer to the ping. To do at least that last action and stay connected to the
chan, use:

.. code-block:: python

    bot.run()

But there is no interaction possible. You can provide a function to parse
messages posted to chan or addressed to the bot:

.. code-block:: python

    from pyircibot import PyIrciBot
    def parse(message, source, target):
        print ('{} wrote to {} the message: {}'.format(source, source, target))
        return {'cmd': {'message': '{} wrote to {} the message: {}'.format(source, source, target)}}
    bot = PyIrciBot("irc.server.org", "#channel")
    bot.connect()
    bot.run(parse_message=parse)

Note that the bot will never leave the chan. It will echo any message written to
the chan or to the bot.

You can also provide a class using `use_parser_class()` like it is done the the *testbot.py* file.

- Parameters

The available parameters of PyIrciBot are::

    server: the IRC server to connect (mandatory)
    channel: a channel join
    nick: a nickname. if not given, a nickname will be generated
            with 5 random hexa digits like 'pyircibot_5fa8b'
    port: the port to connect to the server
    parser_class: the user class (as provided in testbot.py)

