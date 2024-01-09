#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def print_info():
    """
    Print information.

    Returns
    -------
    msg : str
        Message.
    """
    msg = (
        "```"
        "\n"
        "ABOUT\n"
        " Slixfeed aims to be an easy to use and fully-featured news\n"
        " aggregator bot for XMPP. It provides a convenient access to Blogs,\n"
        " Fediverse and News websites along with filtering functionality."
        "\n"
        " Slixfeed is primarily designed for XMPP (aka Jabber).\n"
        " Visit https://xmpp.org/software/ for more information.\n"
        "\n"
        " XMPP is the Extensible Messaging and Presence Protocol, a set\n"
        " of open technologies for instant messaging, presence, multi-party\n"
        " chat, voice and video calls, collaboration, lightweight\n"
        " middleware, content syndication, and generalized routing of XML\n"
        " data."
        " Visit https://xmpp.org/about/ for more information on the XMPP\n"
        " protocol."
        " "
        # "PLATFORMS\n"
        # " Supported prootcols are IRC, Matrix, Tox and XMPP.\n"
        # " For the best experience, we recommend you to use XMPP.\n"
        # "\n"
        "FILETYPES\n"
        " Supported filetypes: Atom, RDF, RSS and XML.\n"
        "\n"
        "PROTOCOLS\n"
        " Supported protocols: Dat, FTP, Gemini, Gopher, HTTP and IPFS.\n"
        "\n"
        "AUTHORS\n"
        " Laura Harbinger, Schimon Zackary.\n"
        "\n"
        "THANKS\n"
        " Christian Dersch (SalixOS),"
        " Cyrille Pontvieux (SalixOS, France),"
        "\n"
        " Denis Fomin (Gajim, Russia),"
        " Dimitris Tzemos (SalixOS, Greece),"
        "\n"
        " Emmanuel Gil Peyrot (poezio, France),"
        " Florent Le Coz (poezio, France),"
        "\n"
        " George Vlahavas (SalixOS, Greece),"
        " Maxime Buquet (slixmpp, France),"
        "\n"
        " Mathieu Pasquet (slixmpp, France),"
        " Pierrick Le Brun (SalixOS, France),"
        "\n"
        " Remko Tronçon (Swift, Germany),"
        " Thorsten Mühlfelder (SalixOS, Germany),"
        "\n"
        " Yann Leboulanger (Gajim, France).\n"
        "\n"
        "COPYRIGHT\n"
        " Slixfeed is free software; you can redistribute it and/or\n"
        " modify it under the terms of the MIT License.\n"
        "\n"
        " Slixfeed is distributed in the hope that it will be useful,\n"
        " but WITHOUT ANY WARRANTY; without even the implied warranty of\n"
        " MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n"
        " GNU General Public License for more details.\n"
        "\n"
        "NOTE\n"
        " You can run Slixfeed on your own computer, server, and\n"
        " even on a Linux phone (i.e. Droidian, Kupfer, Mobian, NixOS,\n"
        " postmarketOS). You can also use Termux.\n"
        "\n"
        " All you need is one of the above and an XMPP account to\n"
        " connect Slixfeed to.\n"
        "\n"
        "DOCUMENTATION\n"
        " Slixfeed\n"
        "   https://gitgud.io/sjehuda/slixfeed\n"
        " Slixmpp\n"
        "   https://slixmpp.readthedocs.io/\n"
        " feedparser\n"
        "   https://pythonhosted.org/feedparser\n"
        "```"
        )
    return msg


def print_help():
    """
    Print help manual.

    Returns
    -------
    msg : str
        Message.
    """
    msg = (
        "```"
        "\n"
        "NAME\n"
        "Slixfeed - News syndication bot for Jabber/XMPP\n"
        "\n"
        "DESCRIPTION\n"
        " Slixfeed is a news aggregator bot for online news feeds.\n"
        " This program is primarily designed for XMPP.\n"
        " For more information, visit https://xmpp.org/software/\n"
        "\n"
        "BASIC USAGE\n"
        " <url>\n"
        "   Add <url> to subscription list.\n"
        " add <url> TITLE\n"
        "   Add <url> to subscription list (without validity check).\n"
        " get <id> <type>\n"
        "   Send an article as file. Specify <id> and <type>."
        "   Supported types are HTML, MD and PDF (default).\n"
        " join <muc>\n"
        "   Join specified groupchat.\n"
        " read <url>\n"
        "   Display most recent 20 titles of given <url>.\n"
        " read <url> <n>\n"
        "   Display specified entry number from given <url>.\n"
        "\n"
        "CUSTOM ACTIONS\n"
        " new\n"
        "   Send only new items of newly added feeds.\n"
        " old\n"
        "   Send all items of newly added feeds.\n"
        " next N\n"
        "   Send N next updates.\n"
        " reset\n"
        "   Mark all entries as read and remove all archived entries\n"
        " reset <url>\n"
        "   Mark entries of <url> as read and remove all archived entries of <url>.\n"
        " start\n"
        "   Enable bot and send updates.\n"
        " stop\n"
        "   Disable bot and stop updates.\n"
        "\n"
        "MESSAGE OPTIONS\n"
        " interval <num>\n"
        "   Set interval update to every <num> minutes.\n"
        " length\n"
        "   Set maximum length of news item description. (0 for no limit)\n"
        " quantum <num>\n"
        "   Set <num> amount of updates per interval.\n"
        "\n"
        "GROUPCHAT OPTIONS\n"
        " ! (command initiation)\n"
        "   Use exclamation mark to initiate an actionable command.\n"
        # " activate CODE\n"
        # "   Activate and command bot.\n"
        # " demaster NICKNAME\n"
        # "   Remove master privilege.\n"
        # " mastership NICKNAME\n"
        # "   Add master privilege.\n"
        # " ownership NICKNAME\n"
        # "   Set new owner.\n"
        "\n"
        "FILTER OPTIONS\n"
        " allow +\n"
        "   Add keywords to allow (comma separates).\n"
        " allow -\n"
        "   Delete keywords from allow list (comma separates).\n"
        " deny +\n"
        "   Keywords to block (comma separates).\n"
        " deny -\n"
        "   Delete keywords from deny list (comma separates).\n"
        # " filter clear allow\n"
        # "   Reset allow list.\n"
        # " filter clear deny\n"
        # "   Reset deny list.\n"
        "\n"
        "EDIT OPTIONS\n"
        " remove <id>\n"
        "   Remove feed of <id> from subscription list.\n"
        " disable <id>\n"
        "   Disable updates for feed of <id>.\n"
        " enable <id>\n"
        "   Enable updates for feed of <id>.\n"
        "\n"
        "SEARCH OPTIONS\n"
        " feeds\n"
        "   List all subscriptions.\n"
        " feeds <text>\n"
        "   Search subscriptions by given <text>.\n"
        " search <text>\n"
        "   Search news items by given <text>.\n"
        " recent <num>\n"
        "   List recent <num> news items (up to 50 items).\n"
        "\n"
        # "STATISTICS OPTIONS\n"
        # " analyses\n"
        # "   Show report and statistics of feeds.\n"
        # " obsolete\n"
        # "   List feeds that are not available.\n"
        # " unread\n"
        # "   Print number of unread news items.\n"
        # "\n"
        "BACKUP OPTIONS\n"
        " export opml\n"
        "   Send an OPML file with feeds.\n"
        # " backup news html\n"
        # "   Send an HTML formatted file of your news items.\n"
        # " backup news md\n"
        # "   Send a Markdown file of your news items.\n"
        # " backup news text\n"
        # "   Send a Plain Text file of your news items.\n"
        "\n"
        "SUPPORT\n"
        " commands\n"
        "   Print list of commands.\n"
        " help\n"
        "   Print this help manual.\n"
        " info\n"
        "   Print information page.\n"
        " support\n"
        "   Join xmpp:slixfeed@chat.woodpeckersnest.space?join\n"
        # "\n"
        # "PROTOCOLS\n"
        # " Supported prootcols are IRC, Matrix and XMPP.\n"
        # " For the best experience, we recommend you to use XMPP.\n"
        # "\n"
        "```"
        )
    return msg


def print_cmd():
    """
    Print list of commands.

    Returns
    -------
    msg : str
        Message.
    """
    msg = (
        "```"
        "\n"
        "!                 : Use exclamation mark to initiate an actionable command (groupchats only).\n"
        "<muc>             : Join specified groupchat.\n"
        "<url>             : Add <url> to subscription list.\n"
        "add <url> <title> : Add <url> to subscription list (without validity check).\n"
        "allow +           : Add keywords to allow (comma separates).\n"
        "allow -           : Delete keywords from allow list (comma separates).\n"
        "deny +            : Keywords to block (comma separates).\n"
        "deny -            : Delete keywords from deny list (comma separates).\n"
        "disable <id>      : Disable updates for feed of <id>.\n"
        "enable <id>       : Enable updates for feed of <id>.\n"
        "export opml       : Send an OPML file with feeds.\n"
        "feeds             : List all subscriptions.\n"
        "feeds <text>      : Search subscriptions by given <text>.\n"
        "get <id> <type>   : Send an article as file. Specify <id> and <type>. Supported types are HTML, MD and PDF (default).\n"
        "interval <n>      : Set interval update to every <n> minutes.\n"
        "join <muc>        : Join specified groupchat.\n"
        "length            : Set maximum length of news item description. (0 for no limit)\n"
        "new               : Send only new items of newly added feeds.\n"
        "next <n>          : Send <n> next updates.\n"
        "old               : Send all items of newly added feeds.\n"
        "quantum <n>       : Set <n> amount of updates per interval.\n"
        "read <url>        : Display most recent 20 titles of given <url>.\n"
        "read <url> <n>    : Display specified entry number from given <url>.\n"
        "recent <n>        : List recent <n> news items (up to 50 items).\n"
        "reset             : Mark all entries as read.\n"
        "reset <url>       : Mark entries of <url> as read.\n"
        "remove <id>       : Remove feed from subscription list.\n"
        "search <text>     : Search news items by given <text>.\n"
        "start             : Enable bot and send updates.\n"
        "stop              : Disable bot and stop updates.\n"
        "```"
        )
    return msg