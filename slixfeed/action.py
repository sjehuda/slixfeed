#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

TODO

1) Function scan at "for entry in entries"
   Suppress directly calling function "add_entry" (accept db_file)
   Pass a list of valid entries to a new function "add_entries"
   (accept db_file) which would call function "add_entry" (accept cur).
   * accelerate adding of large set of entries at once.
   * prevent (or mitigate halt of consequent actions).
   * reduce I/O.

2) Call sqlite function from function statistics.
   Returning a list of values doesn't' seem to be a good practice.

3) Special statistics for operator:
   * Size of database(s);
   * Amount of JIDs subscribed;
   * Amount of feeds of all JIDs;
   * Amount of entries of all JIDs.

"""

from asyncio.exceptions import IncompleteReadError
from bs4 import BeautifulSoup
from http.client import IncompleteRead
from feedparser import parse
import logging
from lxml import html
import slixfeed.config as config
import slixfeed.crawl as crawl
from slixfeed.dt import (
    current_date, current_time, now,
    convert_struct_time_to_iso8601,
    rfc2822_to_iso8601
    )
import slixfeed.fetch as fetch
import slixfeed.sqlite as sqlite
from slixfeed.url import (
    complete_url,
    join_url,
    remove_tracking_parameters,
    replace_hostname,
    trim_url
    )
import slixfeed.xmpp.bookmark as bookmark
from urllib import error
from urllib.parse import parse_qs, urlsplit
import xml.etree.ElementTree as ET

try:
    import html2text
except:
    logging.info(
        "Package html2text was not found.\n"
        "Markdown support is disabled.")

try:
    import pdfkit
except:
    logging.info(
        "Package pdfkit was not found.\n"
        "PDF support is disabled.")

try:
    from readability import Document
except:
    logging.info(
        "Package readability was not found.\n"
        "Arc90 Lab algorithm is disabled.")


def log_to_markdown(timestamp, filename, jid, message):
    """
    Log message to file.

    Parameters
    ----------
    timestamp : str
        Time stamp.
    filename : str
        Jabber ID as name of file.
    jid : str
        Jabber ID.
    message : str
        Message content.

    Returns
    -------
    None.
    
    """
    with open(filename + '.md', 'a') as file:
        # entry = "{} {}:\n{}\n\n".format(timestamp, jid, message)
        entry = (
        "## {}\n"
        "### {}\n\n"
        "{}\n\n").format(jid, timestamp, message)
        file.write(entry)


def is_feed(feed):
    """
    Determine whether document is feed or not.

    Parameters
    ----------
    feed : dict
        Parsed feed.

    Returns
    -------
    val : boolean
        True or False.
    """
    value = False
    # message = None
    if not feed.entries:
        if "version" in feed.keys():
            feed["version"]
            if feed.version:
                value = True
                # message = (
                #     "Empty feed for {}"
                #     ).format(url)
        elif "title" in feed["feed"].keys():
            value = True
            # message = (
            #     "Empty feed for {}"
            #     ).format(url)
        else:
            value = False
            # message = (
            #     "No entries nor title for {}"
            #     ).format(url)
    elif feed.bozo:
        value = False
        # message = (
        #     "Bozo detected for {}"
        #     ).format(url)
    else:
        value = True
        # message = (
        #     "Good feed for {}"
        #     ).format(url)
    return value


def list_unread_entries(result, feed_title):
    # TODO Add filtering
    # TODO Do this when entry is added to list and mark it as read
    # DONE!
    # results = []
    # if get_settings_value(db_file, "filter-deny"):
    #     while len(results) < num:
    #         result = cur.execute(sql).fetchone()
    #         blacklist = await get_settings_value(db_file, "filter-deny").split(",")
    #         for i in blacklist:
    #             if i in result[1]:
    #                 continue
    #                 print("rejected:", result[1])
    #         print("accepted:", result[1])
    #         results.extend([result])

    # news_list = "You've got {} news items:\n".format(num)
    # NOTE Why doesn't this work without list?
    #      i.e. for result in results
    # for result in results.fetchall():
    ix = result[0]
    title = result[1]
    # # TODO Retrieve summary from feed
    # # See fetch.view_entry
    # summary = result[2]
    # # Remove HTML tags
    # try:
    #     summary = BeautifulSoup(summary, "lxml").text
    # except:
    #     print(result[2])
    #     breakpoint()
    # # TODO Limit text length
    # summary = summary.replace("\n\n\n", "\n\n")
    # length = await get_settings_value(db_file, "length")
    # summary = summary[:length] + " […]"
    # summary = summary.strip().split('\n')
    # summary = ["> " + line for line in summary]
    # summary = "\n".join(summary)
    link = result[2]
    link = remove_tracking_parameters(link)
    link = (replace_hostname(link, "link")) or link
    news_item = (
        "\n{}\n{}\n{} [{}]\n"
        ).format(
            str(title), str(link), str(feed_title), str(ix)
            )
    return news_item


def list_search_results(query, results):
    message = (
        "Search results for '{}':\n\n```"
        ).format(query)
    for result in results:
        message += (
            "\n{}\n{}\n"
            ).format(str(result[0]), str(result[1]))
    if len(results):
        message += "```\nTotal of {} results".format(len(results))
    else:
        message = "No results were found for: {}".format(query)
    return message


def list_feeds_by_query(query, results):
    message = (
        "Feeds containing '{}':\n\n```"
        ).format(query)
    for result in results:
        message += (
            "\nName : {} [{}]"
            "\nURL  : {}"
            "\n"
            ).format(
                str(result[0]), str(result[1]), str(result[2]))
    if len(results):
        message += "\n```\nTotal of {} feeds".format(len(results))
    else:
        message = "No feeds were found for: {}".format(query)
    return message


async def get_setting_value(db_file, key):
    value = (
        await sqlite.get_settings_value(db_file, key) or
        config.get_value_default("settings", "Settings", key)
        )
    return value


async def list_statistics(db_file):
    """
    Return table statistics.

    Parameters
    ----------
    db_file : str
        Path to database file.

    Returns
    -------
    msg : str
        Statistics as message.
    """
    entries_unread = await sqlite.get_number_of_entries_unread(db_file)
    entries = await sqlite.get_number_of_items(db_file, 'entries')
    archive = await sqlite.get_number_of_items(db_file, 'archive')
    entries_all = entries + archive
    feeds_active = await sqlite.get_number_of_feeds_active(db_file)
    feeds_all = await sqlite.get_number_of_items(db_file, 'feeds')
    key_archive = await get_setting_value(db_file, "archive")
    key_interval = await get_setting_value(db_file, "interval")
    key_quantum = await get_setting_value(db_file, "quantum")
    key_enabled = await get_setting_value(db_file, "enabled")

    # msg = """You have {} unread news items out of {} from {} news sources.
    #       """.format(unread_entries, entries, feeds)

    # try:
    #     value = cur.execute(sql, par).fetchone()[0]
    # except:
    #     print("Error for key:", key)
    #     value = "Default"
    # values.extend([value])

    message = (
        "```"
        "\nSTATISTICS\n"
        "News items   : {}/{}\n"
        "News sources : {}/{}\n"
        "\nOPTIONS\n"
        "Items to archive : {}\n"
        "Update interval  : {}\n"
        "Items per update : {}\n"
        "Operation status : {}\n"
        "```"
        ).format(
            entries_unread,
            entries_all,
            feeds_active,
            feeds_all,
            key_archive,
            key_interval,
            key_quantum,
            key_enabled
            )
    return message


# FIXME Replace counter by len
def list_last_entries(results, num):
    message = "Recent {} titles:\n\n```".format(num)
    for result in results:
        message += (
            "\n{}\n{}\n"
            ).format(
                str(result[0]), str(result[1]))
    if len(results):
        message += "```\n"
    else:
        message = "There are no news at the moment."
    return message


def list_feeds(results):
    message = "\nList of subscriptions:\n\n```\n"
    for result in results:
        message += (
            "Name : {}\n"
            "URL  : {}\n"
            # "Updated : {}\n"
            # "Status  : {}\n"
            "ID   : {}\n"
            "\n"
            ).format(
                str(result[0]), str(result[1]), str(result[2]))
    if len(results):
        message += (
            "```\nTotal of {} subscriptions.\n"
            ).format(len(results))
    else:
        message = (
            "List of subscriptions is empty.\n"
            "To add feed, send a URL\n"
            "Try these:\n"
            # TODO Pick random from featured/recommended
            "https://reclaimthenet.org/feed/"
            )
    return message


async def list_bookmarks(self):
    conferences = await bookmark.get(self)
    message = "\nList of groupchats:\n\n```\n"
    for conference in conferences:
        message += (
            "{}\n"
            "\n"
            ).format(
                conference["jid"]
                )
    message += (
        "```\nTotal of {} groupchats.\n"
        ).format(len(conferences))
    return message


def export_to_markdown(jid, filename, results):
    with open(filename, 'w') as file:
        file.write(
            '# Subscriptions for {}\n'.format(jid))
        file.write(
            '## Set of feeds exported with Slixfeed\n')
        for result in results:
            file.write(
                '- [{}]({})\n'.format(result[0], result[1]))
        file.write(
            '\n\n* * *\n\nThis list was saved on {} from xmpp:{} using '
            '[Slixfeed](https://gitgud.io/sjehuda/slixfeed)\n'.format(
                current_date(), jid))


# TODO Consider adding element jid as a pointer of import
def export_to_opml(jid, filename, results):
    root = ET.Element("opml")
    root.set("version", "1.0")
    head = ET.SubElement(root, "head")
    ET.SubElement(head, "title").text = "{}".format(jid)
    ET.SubElement(head, "description").text = (
        "Set of subscriptions exported by Slixfeed")
    ET.SubElement(head, "generator").text = "Slixfeed"
    ET.SubElement(head, "urlPublic").text = (
        "https://gitgud.io/sjehuda/slixfeed")
    time_stamp = current_time()
    ET.SubElement(head, "dateCreated").text = time_stamp
    ET.SubElement(head, "dateModified").text = time_stamp
    body = ET.SubElement(root, "body")
    for result in results:
        outline = ET.SubElement(body, "outline")
        outline.set("text", result[0])
        outline.set("xmlUrl", result[1])
        # outline.set("type", result[2])
    tree = ET.ElementTree(root)
    tree.write(filename)


async def import_opml(db_file, url):
    result = await fetch.http(url)
    document = result[0]
    if document:
        root = ET.fromstring(document)
        before = await sqlite.get_number_of_items(
            db_file, 'feeds')
        feeds = []
        for child in root.findall(".//outline"):
            url = child.get("xmlUrl")
            title = child.get("text")
            # feed = (url, title)
            # feeds.extend([feed])
            feeds.extend([(url, title)])
        await sqlite.import_feeds(db_file, feeds)
        await sqlite.add_metadata(db_file)
        after = await sqlite.get_number_of_items(
            db_file, 'feeds')
        difference = int(after) - int(before)
        return difference


async def add_feed(db_file, url):
    while True:
        exist = await sqlite.get_feed_id_and_name(db_file, url)
        if not exist:
            result = await fetch.http(url)
            document = result[0]
            status_code = result[1]
            if document:
                feed = parse(document)
                # if is_feed(url, feed):
                if is_feed(feed):
                    if "title" in feed["feed"].keys():
                        title = feed["feed"]["title"]
                    else:
                        title = urlsplit(url).netloc
                    if "language" in feed["feed"].keys():
                        language = feed["feed"]["language"]
                    else:
                        language = ''
                    if "encoding" in feed.keys():
                        encoding = feed["encoding"]
                    else:
                        encoding = ''
                    if "updated_parsed" in feed["feed"].keys():
                        updated = feed["feed"]["updated_parsed"]
                        try:
                            updated = convert_struct_time_to_iso8601(updated)
                        except:
                            updated = ''
                    else:
                        updated = ''
                    version = feed["version"]
                    entries = len(feed["entries"])
                    await sqlite.insert_feed(
                        db_file, url,
                        title=title,
                        entries=entries,
                        version=version,
                        encoding=encoding,
                        language=language,
                        status_code=status_code,
                        updated=updated
                        )
                    await scan(
                        db_file, url)
                    old = await get_setting_value(db_file, "old")
                    if not old:
                        await sqlite.mark_feed_as_read(
                            db_file, url)
                    response = (
                        "> {}\nNews source \"{}\" has been "
                        "added to subscription list."
                        ).format(url, title)
                    break
                else:
                    result = await crawl.probe_page(
                        url, document)
                    if isinstance(result, str):
                        response = result
                        break
                    else:
                        url = result[0]
            else:
                response = (
                    "> {}\nFailed to load URL.  Reason: {}"
                    ).format(url, status_code)
                break
        else:
            ix = exist[0]
            name = exist[1]
            response = (
                "> {}\nNews source \"{}\" is already "
                "listed in the subscription list at "
                "index {}".format(url, name, ix)
                )
            break
    return response


async def view_feed(url):
    while True:
        result = await fetch.http(url)
        document = result[0]
        status = result[1]
        if document:
            feed = parse(document)
            # if is_feed(url, feed):
            if is_feed(feed):
                if "title" in feed["feed"].keys():
                    title = feed["feed"]["title"]
                else:
                    title = urlsplit(url).netloc
                entries = feed.entries
                response = "Preview of {}:\n\n```\n".format(title)
                counter = 0
                for entry in entries:
                    counter += 1
                    if entry.has_key("title"):
                        title = entry.title
                    else:
                        title = "*** No title ***"
                    if entry.has_key("link"):
                        # link = complete_url(source, entry.link)
                        link = join_url(url, entry.link)
                        link = trim_url(link)
                    else:
                        link = "*** No link ***"
                    if entry.has_key("published"):
                        date = entry.published
                        date = rfc2822_to_iso8601(date)
                    elif entry.has_key("updated"):
                        date = entry.updated
                        date = rfc2822_to_iso8601(date)
                    else:
                        date = "*** No date ***"
                    response += (
                        "Title : {}\n"
                        "Date  : {}\n"
                        "Link  : {}\n"
                        "Count : {}\n"
                        "\n"
                        ).format(title, date, link, counter)
                    if counter > 4:
                        break
                response += (
                    "```\nSource: {}"
                    ).format(url)
                break
            else:
                result = await crawl.probe_page(
                    url, document)
                if isinstance(result, str):
                    response = result
                    break
                else:
                    url = result[0]
        else:
            response = (
                "> {}\nFailed to load URL.  Reason: {}"
                ).format(url, status)
            break
    return response


async def view_entry(url, num):
    while True:
        result = await fetch.http(url)
        document = result[0]
        status = result[1]
        if document:
            feed = parse(document)
            # if is_feed(url, feed):
            if is_feed(feed):
                if "title" in feed["feed"].keys():
                    title = feed["feed"]["title"]
                else:
                    title = urlsplit(url).netloc
                entries = feed.entries
                num = int(num) - 1
                entry = entries[num]
                response = "Preview of {}:\n\n```\n".format(title)
                if entry.has_key("title"):
                    title = entry.title
                else:
                    title = "*** No title ***"
                if entry.has_key("published"):
                    date = entry.published
                    date = rfc2822_to_iso8601(date)
                elif entry.has_key("updated"):
                    date = entry.updated
                    date = rfc2822_to_iso8601(date)
                else:
                    date = "*** No date ***"
                if entry.has_key("summary"):
                    summary = entry.summary
                    # Remove HTML tags
                    summary = BeautifulSoup(summary, "lxml").text
                    # TODO Limit text length
                    summary = summary.replace("\n\n\n", "\n\n")
                else:
                    summary = "*** No summary ***"
                if entry.has_key("link"):
                    # link = complete_url(source, entry.link)
                    link = join_url(url, entry.link)
                    link = trim_url(link)
                else:
                    link = "*** No link ***"
                response = (
                    "{}\n"
                    "\n"
                    # "> {}\n"
                    "{}\n"
                    "\n"
                    "{}\n"
                    "\n"
                    ).format(title, summary, link)
                break
            else:
                result = await crawl.probe_page(
                    url, document)
                if isinstance(result, str):
                    response = result
                    break
                else:
                    url = result[0]
        else:
            response = (
                "> {}\nFailed to load URL.  Reason: {}"
                ).format(url, status)
            break
    return response


async def scan(db_file, url):
    """
    Check feeds for new entries.

    Parameters
    ----------
    db_file : str
        Path to database file.
    url : str, optional
        URL. The default is None.
    """
    if isinstance(url, tuple): url = url[0]
    result = await fetch.http(url)
    try:
        document = result[0]
        status = result[1]
    except:
        return
    new_entries = []
    if document and status == 200:
        feed = parse(document)
        entries = feed.entries
        # length = len(entries)
        await remove_nonexistent_entries(
            db_file, url, feed)
        try:
            if feed.bozo:
                # bozo = (
                #     "WARNING: Bozo detected for feed: {}\n"
                #     "For more information, visit "
                #     "https://pythonhosted.org/feedparser/bozo.html"
                #     ).format(url)
                # print(bozo)
                valid = 0
            else:
                valid = 1
            feed_id = await sqlite.get_feed_id(db_file, url)
            await sqlite.update_feed_validity(
                db_file, feed_id, valid)
            if "updated_parsed" in feed["feed"].keys():
                updated = feed["feed"]["updated_parsed"]
                try:
                    updated = convert_struct_time_to_iso8601(updated)
                except:
                    updated = ''
            else:
                updated = ''
            feed_id = await sqlite.get_feed_id(db_file, url)
            await sqlite.update_feed_properties(
                db_file, feed_id, len(feed["entries"]), updated)
            # await update_feed_status
        except (
                IncompleteReadError,
                IncompleteRead,
                error.URLError
                ) as e:
            logging.error(e)
            return
        # new_entry = 0
        for entry in entries:
            if entry.has_key("published"):
                date = entry.published
                date = rfc2822_to_iso8601(date)
            elif entry.has_key("updated"):
                date = entry.updated
                date = rfc2822_to_iso8601(date)
            else:
                date = now()
            if entry.has_key("link"):
                # link = complete_url(source, entry.link)
                link = join_url(url, entry.link)
                link = trim_url(link)
            else:
                link = url
            # title = feed["feed"]["title"]
            # title = "{}: *{}*".format(feed["feed"]["title"], entry.title)
            title = entry.title if entry.has_key("title") else date
            entry_id = entry.id if entry.has_key("id") else link
            feed_id = await sqlite.get_feed_id(db_file, url)
            exist = await sqlite.check_entry_exist(
                db_file, feed_id, entry_id=entry_id,
                title=title, link=link, date=date)
            if not exist:
                summary = entry.summary if entry.has_key("summary") else ''
                read_status = 0
                pathname = urlsplit(link).path
                string = (
                    "{} {} {}"
                    ).format(
                        title, summary, pathname)
                allow_list = await config.is_include_keyword(
                    db_file, "filter-allow", string)
                if not allow_list:
                    reject_list = await config.is_include_keyword(
                        db_file, "filter-deny", string)
                    if reject_list:
                        read_status = 1
                        logging.debug(
                            "Rejected : {}\n"
                            "Keyword  : {}".format(
                                link, reject_list))
                if isinstance(date, int):
                    logging.error(
                        "Variable 'date' is int: {}".format(date))
                media_link = ''
                if entry.has_key("links"):
                    for e_link in entry.links:
                        try:
                            # if (link.rel == "enclosure" and
                            #     (link.type.startswith("audio/") or
                            #      link.type.startswith("image/") or
                            #      link.type.startswith("video/"))
                            #     ):
                            media_type = e_link.type[:e_link.type.index("/")]
                            if e_link.has_key("rel"):
                                if (e_link.rel == "enclosure" and
                                    media_type in ("audio", "image", "video")):
                                    media_link = e_link.href
                                    media_link = join_url(url, e_link.href)
                                    media_link = trim_url(media_link)
                                    break
                        except:
                            logging.error(
                                "KeyError: 'href'\n"
                                "Missing 'href' attribute for {}".format(url))
                            logging.info(
                                "Continue scanning for next potential "
                                "enclosure of {}".format(link))
                entry = {
                    "title": title,
                    "link": link,
                    "enclosure": media_link,
                    "entry_id": entry_id,
                    "date": date,
                    "read_status": read_status
                    }
                new_entries.extend([entry])
                # await sqlite.add_entry(
                #     db_file, title, link, entry_id,
                #     url, date, read_status)
                # await sqlite.set_date(db_file, url)
    if len(new_entries):
        feed_id = await sqlite.get_feed_id(db_file, url)
        await sqlite.add_entries_and_update_timestamp(
            db_file, feed_id, new_entries)


def get_document_title(data):
    try:
        document = Document(data)
        title = document.short_title()
    except:
        document = BeautifulSoup(data, 'html.parser')
        title = document.title.string
    return title


def generate_document(data, url, ext, filename):
    error = None
    try:
        document = Document(data)
        content = document.summary()
    except:
        content = data
        logging.warning(
            "Check that package readability is installed.")
    match ext:
        case "html":
            generate_html(content, filename)
        case "md":
            try:
                generate_markdown(content, filename)
            except:
                logging.warning(
                    "Check that package html2text is installed.")
                error = (
                    "Package html2text was not found.")
        case "pdf":
            try:
                generate_pdf(content, filename)
            except:
                logging.warning(
                    "Check that packages pdfkit and wkhtmltopdf "
                    "are installed.")
                error = (
                    "Package pdfkit or wkhtmltopdf was not found.")
    if error:
        return error

    # TODO Either adapt it to filename
    # or change it to something else
    #filename = document.title()
    # with open(filename, 'w') as file:
    #     html_doc = document.summary()
    #     file.write(html_doc)


async def extract_image_from_feed(db_file, feed_id, url):
    feed_url = sqlite.get_feed_url(db_file, feed_id)
    result = await fetch.http(feed_url)
    document = result[0]
    if document:
        feed = parse(document)
        for entry in feed.entries:
            try:
                if entry.link == url:
                    for link in entry.links:
                        if (link.rel == "enclosure" and
                            link.type.startswith("image/")):
                            image_url = link.href
                            return image_url
            except:
                logging.error(url)
                logging.error(
                    "AttributeError: object has no attribute 'link'")
                breakpoint()


async def extract_image_from_html(url):
    result = await fetch.http(url)
    data = result[0]
    if data:
        try:
            document = Document(data)
            content = document.summary()
        except:
            content = data
            logging.warning(
                "Check that package readability is installed.")
        tree = html.fromstring(content)
        # TODO Exclude banners, class="share" links etc.
        images = tree.xpath(
            '//img[not('
                'contains(@src, "avatar") or '
                'contains(@src, "emoji") or '
                'contains(@src, "icon") or '
                'contains(@src, "logo") or '
                'contains(@src, "smiley")'
            ')]/@src')
        if len(images):
            image = images[0]
            image = str(image)
            image_url = complete_url(url, image)
            return image_url


def generate_html(text, filename):
    with open(filename, 'w') as file:
        file.write(text)


def generate_pdf(text, filename):
    pdfkit.from_string(text, filename)


def generate_markdown(text, filename):
    h2m = html2text.HTML2Text()
    # Convert HTML to Markdown
    markdown = h2m.handle(text)
    with open(filename, 'w') as file:
        file.write(markdown)


# TODO Add support for eDonkey, Gnutella, Soulseek
async def get_magnet(link):
    parted_link = urlsplit(link)
    queries = parse_qs(parted_link.query)
    query_xt = queries["xt"][0]
    if query_xt.startswith("urn:btih:"):
        filename = queries["dn"][0]
        checksum = query_xt[len("urn:btih:"):]
        torrent = await fetch.magnet(link)
        logging.debug(
            "Attempting to retrieve {} ({})".format(
                filename, checksum))
        if not torrent:
            logging.debug(
                "Attempting to retrieve {} from HTTP caching service".format(
                    filename))
            urls = [
                'https://watercache.libertycorp.org/get/{}/{}',
                'https://itorrents.org/torrent/{}.torrent?title={}',
                'https://firecache.libertycorp.org/get/{}/{}',
                'http://fcache63sakpihd44kxdduy6kgpdhgejgp323wci435zwy6kiylcnfad.onion/get/{}/{}'
                ]
            for url in urls:
                torrent = fetch.http(url.format(checksum, filename))
                if torrent:
                    break
    return torrent


async def remove_nonexistent_entries(db_file, url, feed):
    """
    Remove entries that don't exist in a given parsed feed.
    Check the entries returned from feed and delete read non
    existing entries, otherwise move to table archive, if unread.

    Parameters
    ----------
    db_file : str
        Path to database file.
    url : str
        Feed URL.
    feed : list
        Parsed feed document.
    """
    feed_id = await sqlite.get_feed_id(db_file, url)
    items = await sqlite.get_entries_of_feed(db_file, feed_id)
    entries = feed.entries
    for item in items:
        ix = item[0]
        entry_title = item[1]
        entry_link = item[2]
        entry_id = item[3]
        timestamp = item[4]
        read_status = item[5]
        valid = False
        for entry in entries:
            title = None
            link = None
            time = None
            # valid = False
            # TODO better check and don't repeat code
            if entry.has_key("id") and entry_id:
                if entry.id == entry_id:
                    # print("compare1:", entry.id)
                    # print("compare2:", entry_id)
                    # print("============")
                    valid = True
                    break
            else:
                if entry.has_key("title"):
                    title = entry.title
                else:
                    title = feed["feed"]["title"]
                if entry.has_key("link"):
                    link = join_url(url, entry.link)
                else:
                    link = url
                if entry.has_key("published") and timestamp:
                    # print("compare11:", title, link, time)
                    # print("compare22:", entry_title, entry_link, timestamp)
                    # print("============")
                    time = rfc2822_to_iso8601(entry.published)
                    if (entry_title == title and
                        entry_link == link and
                        timestamp == time):
                        valid = True
                        break
                else:
                    if (entry_title == title and
                        entry_link == link):
                        # print("compare111:", title, link)
                        # print("compare222:", entry_title, entry_link)
                        # print("============")
                        valid = True
                        break
            # TODO better check and don't repeat code
        if not valid:
            # print("id:        ", ix)
            # if title:
            #     print("title:     ", title)
            #     print("entry_title:   ", entry_title)
            # if link:
            #     print("link:      ", link)
            #     print("entry_link:   ", entry_link)
            # if entry.id:
            #     print("last_entry:", entry.id)
            #     print("entry_id:   ", entry_id)
            # if time:
            #     print("time:      ", time)
            #     print("timestamp:   ", timestamp)
            # print("read:      ", read_status)
            # breakpoint()

            # TODO Send to table archive
            # TODO Also make a regular/routine check for sources that
            #      have been changed (though that can only happen when
            #      manually editing)
            # ix = item[0]
            # print(">>> SOURCE: ", source)
            # print(">>> INVALID:", entry_title)
            # print("title:", entry_title)
            # print("link :", entry_link)
            # print("id   :", entry_id)
            if read_status == 1:
                await sqlite.delete_entry_by_id(db_file, ix)
                # print(">>> DELETING:", entry_title)
            else:
                # print(">>> ARCHIVING:", entry_title)
                await sqlite.archive_entry(db_file, ix)
        limit = await get_setting_value(db_file, "archive")
        await sqlite.maintain_archive(db_file, limit)
