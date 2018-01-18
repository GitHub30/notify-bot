import os
import glob
from time import sleep
from urllib import request, error
from datetime import datetime
import lxml.html
from slackclient import SlackClient

sites = [
    {
        'dir_name': 'itsoku',
        'url': 'http://blog.livedoor.jp/itsoku/',
        'url_xpath': '//article//header/h1/a/@href',
        'title_xpath': '//article//header/h1/a/text()'
    },
    {
        'dir_name': 'html5experts',
        'url': 'https://html5experts.jp/',
        'url_xpath': '//section//h1[@class="post-title"]/a/@href',
        'title_xpath': '//section//h1[@class="post-title"]/a/text()'
    },
    {
        'dir_name': 'web',
        'url': 'https://developers.google.com/web/updates/?hl=ja',
        'url_xpath': '//a[h3]/@href',
        'title_xpath': '//a/h3/text()'
    },
    {
        'dir_name': 'publickey',
        'url': 'http://www.publickey1.jp/',
        'url_xpath': '//li[@class="top"]/a/@href',
        'title_xpath': '//li[@class="top"]/a/text()[last()]'
    }
]


def notify(title, url):
    print(datetime.now(), title, url)
    sc = SlackClient(os.environ["SLACK_API_TOKEN"])
    sc.api_call(
        'chat.postMessage',
        channel='D19U7HANA',
        text=f'{title}\n{url}'
    )


def main():
    for site in sites:
        os.makedirs(site['dir_name'], exist_ok=True)
        file_path = '%s/%s.html' % (site['dir_name'], datetime.now().isoformat(timespec='seconds'))
        try:
            request.urlretrieve(site['url'], file_path)
        except error.URLError as e:
            print(datetime.now(), e.reason, 'offline', site['url'])
            continue
        all_file_paths = sorted(glob.glob('%s/*' % site['dir_name']))
        file_paths = all_file_paths[-2:]
        if len(file_paths) != 2:
            continue
        for file_path in all_file_paths[:-2]:
            os.remove(file_path)
        old = lxml.html.parse(file_paths[0])
        new = lxml.html.parse(file_paths[1])
        old_urls = old.xpath(site['url_xpath'])
        new_urls = new.xpath(site['url_xpath'])
        for url in set(new_urls) - set(old_urls):
            notify(title=new.xpath(site['title_xpath'])[new_urls.index(url)].strip(), url=url)


if __name__ == '__main__':
    while True:
        main()
        sleep(10)
