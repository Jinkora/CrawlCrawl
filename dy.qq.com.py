# coding=utf-8
import urllib2, time, gzip
import StringIO, unicodedata, json
import MySQLdb, datetime, uuid
import sys
import logging

LOG_FILENAME = "log_dy_qq.txt"
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)
logging.debug(
    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ":Start *************************************************")

reload(sys)
sys.setdefaultencoding("utf-8")


def reqt(url):
    req = urllib2.Request(url + "&t=" + str(int(round(time.time() * 1000))))
    req.add_header("Accept-Encoding", "gzip, deflate, sdch")
    req.add_header("Accept-Language", "zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4,ko;q=0.2,zh-TW;q=0.2")
    req.add_header("Cache-Control", "no-cache")
    req.add_header("User-Agent",
                   "Mozilla/5.0 (Windows NT 5.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36")
    req.add_header("Accept", "*/*")
    req.add_header("Connection", "keep-alive")
    req.add_header("Host", "dyapi.inews.qq.com")
    req.add_header("Referer", "http://dy.qq.com/manage.htm")
    res = urllib2.urlopen(req).read()
    res = gzip.GzipFile(fileobj=StringIO.StringIO(res)).read()
    return res


def parseJSON(res, var=None):
    return json.loads(res.replace(var, '').replace('(', '').replace(')', ''))


def catList():
    res = parseJSON(
        reqt("http://dyapi.inews.qq.com/getSubWebCatListOnly?withRecom=true&dyapidebug&callback=subscribeNav&t="),
        var="subscribeNav")
    cats = []
    for cat in res['cats']:
        cats.append(cat)
        logging.debug(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "-CAT-:" + str(cat['catName']))
    return cats


def channelList(keys=['chlid', 'chlname', 'icon']):
    res = parseJSON(reqt("http://dyapi.inews.qq.com/getSubWebCatMedia?callback=allManageMedia"), var="allManageMedia")
    channels = []
    for cat in res['cats']:
        for channel in cat['channels']:
            chnlDict = {k: v for k, v in channel.iteritems() if any(k in s for s in keys)}
            chnlDict['catId'] = cat['catId']
            chnlDict['catName'] = '腾讯' + str(cat['catName'])
            logging.debug(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "-CHANNEL-:" + chnlDict['catName'])
            channels.append(chnlDict)
    return channels


def newsList(chlid, keys=['id', 'title', 'thumbnails_qqnews']):
    unparsed = parseJSON(
        reqt("http://dyapi.inews.qq.com/getSubWebMediaNews?chlid=" + chlid + "&page=0&count=10&callback=createHtml")
        , var="createHtml")
    newsList = []
    for news in unparsed['newslist']:
        newsList.append({k: v for k, v in news.iteritems() if any(k in s for s in keys)})

    return newsList


def newsHtml(aid):
    unparsed = parseJSON(
        reqt("http://dyapi.inews.qq.com/getSubWebContent?id=" + aid + "&callback=showArticle"),
        var='showArticle')
    parsed = ''

    if isinstance(unparsed['data'], list):
        for content in unparsed['data'][0]['content']:
            try:
                if content['type'] == 'cnt_article':
                    parsed += '<p>' + content['desc'] + '</p>'
                elif content['type'] == 'img_url':
                    parsed += '<p><img src="' + content['img_url'] + '" /></p>'
            except:
                pass
    return parsed


def globalCrawl():
    for cat in catList():
        print cat

    try:
        for channel in channelList():
            print str(channel['chlname'])

            for news in newsList(channel['chlid']):
                print newsHtml(news['id'])
    except:
        pass


def main():
    globalCrawl()

if __name__ == '__main__':
    main()
