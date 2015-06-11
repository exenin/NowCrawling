#!/usr/bin/env python3
__author__ = 'jota'

import urllib.request
import urllib.parse
from optparse import OptionParser, OptionGroup
import re

GOOGLE_SEARCH_URL = "http://google.com/search?%s"
GOOGLE_SEARCH_REGEX = 'href="\/url\?q=[^\/]*\/\/(?!webcache).*?&amp'
SMART_FILE_SEARCH = " intitle:index of "
GOOGLE_NUM_RESULTS = 100
FILE_REGEX = '(href=[^<> ]*tagholder\.(typeholder))|((ftp|http|https):\/\/[^<> ]*tagholder\.(typeholder))'
YES = ['yes', 'y', 'ye', '']
URL_TIMEOUT = 7

class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[36m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def crawlGoogle(numres, start, hint, smart):
    query = urllib.parse.urlencode({'num': numres, 'q': (hint+SMART_FILE_SEARCH if smart is True and SMART_FILE_SEARCH not in hint else hint), "start": start})
    url = GOOGLE_SEARCH_URL % query

    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers = {'User-Agent': user_agent, }
    request = urllib.request.Request(url, None, headers)
    response = urllib.request.urlopen(request)
    data = str(response.read())
    p = re.compile(GOOGLE_SEARCH_REGEX, re.IGNORECASE)

    return list(set(x.replace('href="/url?q=', '').replace('HREF="/url?q=', '').replace('"', '').replace('&amp', '') for x in p.findall(data)))

def getTagsRe(tags):
    tagslist = tags.split(" ")
    tagsre = ''.join(i + "[^<> ]*" for i in tagslist)
    ##print(tagsre)
    return tagsre

def getTypesRe(types):
    return types.replace(' ', '|')

def getURLs(crawlurl, tags, regex2, types):
    url = crawlurl
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers = {'User-Agent': user_agent, }

    request = urllib.request.Request(url, None, headers)
    try:
        response = urllib.request.urlopen(request,timeout=URL_TIMEOUT)
    except:
        return []
    data = str(response.read())
    if (tags is None and regex2 is None):
        regex = FILE_REGEX.replace('tagholder', '').replace('typeholder', getTypesRe(types))
    elif (tags is not None):
        regex = FILE_REGEX.replace('tagholder', getTagsRe(tags)).replace('typeholder', getTypesRe(types))
    else:
        regex = FILE_REGEX.replace('tagholder', regex2).replace('typeholder', getTypesRe(types))

    ##print(regex)
    p = re.compile(regex, re.IGNORECASE)

    tuples = p.findall(data)
    if (len(tuples) < 1):
        return []
    tuples = [j[i] for j in tuples for i in range(len(j)) if '.' in j[i]]

    prettyurls = list(x.replace('href=', '').replace('HREF=', '').replace('"', '').replace('\\', '') for x in tuples)
    prettyurls = list(crawlurl+x if "://" not in x else x for x in prettyurls)
    return prettyurls

def parse_input():
    ##FIXME TODO MAKE -A DEFAULT
    parser = OptionParser()
    parser.add_option('-f', '--files', help='Crawl for files', action="store_true", dest="getfiles")
    parser.add_option('-c', '--content', help='Crawl for content (words, strings, pages, regexes)', action="store_false", dest="getfiles")

    filesgroup = OptionGroup(parser, "Files (-f) Crawler Arguments")
    filesgroup.add_option('-k', '--keywords', help='(Required) A quoted list of words separated by spaces which will be the search terms of the crawler', dest='keywords', type='string')
    filesgroup.add_option('-a', '--ask', help='Ask before downloading', action="store_true", dest="ask", default=False)
    filesgroup.add_option('-l', '--limit', help='File size limit in bytes separated by a hyphen (example: 500-1200 for files between 500 and 1200 bytes, -500 for files smaller than 500 bytes, 500- for files larger than 500 bytes) (Default: None)', dest="limit", type='string', default=None)
    filesgroup.add_option('-n', '--number', help='Number of files to download until crawler stops (Default: Max)', dest="maxfiles", type='int', default=None)
    filesgroup.add_option('-e', '--extensions', help='A quoted list of file extensions separated by spaces. Default: all', dest='extensions', type='string', default='[a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9][a-zA-Z0-9]?')
    filesgroup.add_option('-s', '--smart', help='Smart file search, will highly reduce the crawling time but might not crawl all the results. Basically the same as appending \'intitle: index of\' to your keywords.', action="store_true", dest="smart", default=False)

    filenamegroup = OptionGroup(parser, "File Names Options", "You can only pick one."" If none are picked, EVERY file matching the specified extension will be downloaded")
    filenamegroup.add_option('-t', '--tags', help='A quoted list of words separated by spaces that must be present in the file name that you\'re crawling for', dest='tags', type='string')
    filenamegroup.add_option('-r', '--regex', help='Instead of tags you can just specify a regex for the file name you\'re looking for', dest='regex', type='string')
    ##TODO FIXME -R STILL NEEDS TESTING!
    parser.add_option_group(filesgroup)
    parser.add_option_group(filenamegroup)

    ##contentgroup = OptionGroup(parser, "Content Crawler Options","When crawling for content, the following parameters are available:")
    ##contentgroup.add_option("-c", action="store_true", help="Crawl for Content.")
    ##parser.add_option_group(contentgroup)

    ##filesgroup = OptionGroup(parser, "Debug Options")
    ##filesgroup.add_option('-t', '--tags', help='A quoted list of words separated by spaces that must be present in the file name or content that you\'re crawling for', dest='tags', type='string', default='')
    ##parser.add_option_group(filesgroup)


    ##parser.add_option('-c', '--content', help='Crawl for content (words, strings, pages) instead of files', action="store_false", dest="getfiles", default=True)
    ##parser.add_option('-t', '--tags', help='A quoted list of words separated by spaces that must be present in the file name or content that you\'re crawling for', dest='tags', type='string', default='')
    ##parser.add_option('-r', '--regex', help='Instead of tags you can just specify a regex for the content you\'re looking for', dest='regex', type='string', default='')
    ##parser.add_option('-h', '--hint', help='A quoted list of words separated by spaces which will be the search terms of the crawler (Default will be tags)', dest='hint', type='string', default='')    ##parser.add_option('-c', '--connection-timeout', help='Set the connection timeout waiting time (default: 60)', dest='connection_timeout', type='float', default=60)
    (options, args) = parser.parse_args()

    if (options.getfiles is None):
        parser.error('You must specify the crawler type: -f for files or -c for content')
    if (options.getfiles is True and options.keywords is None):
        parser.error('You must specify keywords when crawling for files.')
    if (options.getfiles is True and (options.tags is not None and options.regex is not None)):
        parser.error('You can\'t pick both file name search options: -t or -r')
    if (options.getfiles is True and options.limit is not None and '-' not in options.limit):
        parser.error('Limits must be separated by a hyphen.')
    ## FIXME FALTA TANTO CHECK AI JASUS, TIPO VER SE O GAJO NAO METE -A SEM METER -F ENTRE OUTROS AI JASUS

    return options.getfiles, options.keywords, options.extensions, options.smart, options.tags, options.regex, options.ask, options.limit, options.maxfiles

def crawl(getfiles, keywords, extensions, smart, tags, regex, ask, limit, maxfiles):
    downloaded = 0
    start = 0
    if (limit is not None):
        limit = limit.split('-')
        maxsize=limit[1]
        minsize=limit[0]
        if (maxsize is ''):
            maxsize = None
        if (minsize is ''):
            minsize = None
        if (maxsize is not None and minsize is not None and int(maxsize) < int(minsize)):
            print(BColors.FAIL+'You are dumb, but it\'s fine, I will swap limits'+BColors.ENDC)
            tmp = maxsize
            maxsize = minsize
            minsize = tmp

    while True:
        googleurls = crawlGoogle(GOOGLE_NUM_RESULTS, start, keywords, smart)
        print(len(googleurls))
        ##print(googleurls)
        for searchurl in googleurls:
            downloadurls = getURLs(searchurl, tags, regex, extensions)
            if len(downloadurls) < 1:
                print('No results in '+searchurl)
            else:
                for file in downloadurls:
                    if (maxfiles is not None and downloaded >= maxfiles):
                        print(BColors.OKGREEN+'All files have been downloaded. Exiting...'+BColors.ENDC)
                        exit()
                    try:
                        filename = file.split('/')[-1]
                        meta = urllib.request.urlopen(file).info()
                        filesize = meta.get_all("Content-Length")[0]
                        if (limit is not None and (maxsize is not None and (int(filesize) > int(maxsize)) or (minsize is not None and (int(filesize) < int(minsize))))):
                            print (BColors.WARNING+'Skipping file '+filename+' because size '+filesize+' is off limits.'+BColors.ENDC)
                            continue
                        if ask:
                            print (BColors.OKBLUE+'Download file '+filename+' of size '+filesize+' from '+file+'? [y/n]:'+BColors.ENDC)
                            choice = input().lower()
                            if choice not in YES:
                               continue
                        print (BColors.OKGREEN+'Downloading file '+filename+' of size '+filesize+BColors.ENDC)
                        urllib.request.urlretrieve(file, filename)
                        downloaded += 1
                    except:
                        print(BColors.FAIL+'File '+file+ ' not available'+BColors.ENDC)
                        continue
        if len(googleurls) < GOOGLE_NUM_RESULTS:
            break
        else:
            start+=len(googleurls)

try:
    crawl(*parse_input())
except KeyboardInterrupt:
    print(BColors.OKGREEN+'All files have been downloaded. Exiting...'+BColors.ENDC)
    exit()
