# -*- coding: utf-8 -*-
"""
    config.py
    ~~~~~~~~~

    This module is the middle man for handling/consolidating
    configurations for the IRCpyBot project.

    :copyright: (c) 2012 by Mek, Dippingsauce
    :license: Pending, see LICENSE for more details.
"""

import ConfigParser
import os
import types

def getdef(self, section, option, default_value):
    try:
        return self.get(section, option)
    except:
        return default_value

path = os.path.dirname(__file__)
config = ConfigParser.ConfigParser()
config.read('%s/settings.cfg' % path)

# Add/inject a method to the config object called getdef
config.getdef = types.MethodType(getdef, config)

CONN = {'host': config.getdef("irc", "host", "irc.freenode.net"),
        'port': int(config.getdef("irc", "port", 6667)),
        'channel': '#%s' % config.getdef("irc", "channel", "test")
        }

USER = {'nick': config.getdef("irc", "nick", "pybot"),
        'ident': config.getdef("irc", "ident", "pybot"),
        'realname': config.getdef("irc", "", "Noname"),
        'owner': config.getdef("irc", "", "Noauthor")
        }
