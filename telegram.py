import requests
from bs4 import BeautifulSoup
import time
import os
import argparse

TELEGRAM_URL = "https://t.me/{}/"
MAX_ERRORS = 35

def download(channel, post_start, file_to):
    """Dowloads and saves all the posts from the specified channel to an html file."""

    post_id = post_start
    url = TELEGRAM_URL.format(channel)
    print("Loading posts fot channel \"{0}\" from {1} into \"{2}\"".format(
        url, post_start, file_to.name))

    # check that the channel exists by getting the first post
    data = requests.get(url + '1')
    soup = BeautifulSoup(data.text, 'html.parser')
    if not soup.find_all('div', {"class": "tgme_page_post"}):
        # channel not found
        file_to.close()
        os.remove(file_to.name)
        raise Exception('Channel not found')
    else:
        url += "{}?embed=1" #embeded page looks better

    header_set = False
    errors = 0
    file_to.write('<!DOCTYPE html><html>')

    # iterate while there are posts on this channel
    while True:
        post_url = url.format(post_id)
        print("Saving post:", post_url)
        data = requests.get(post_url)
        soup = BeautifulSoup(data.text, 'html.parser')

        if not soup.find_all('div', {"class": "tgme_widget_message_error"}):
            if not header_set:
                # get the header from the first post with all the css styles
                for link in soup.find_all('head'):
                    file_to.write(str(link).replace(
                        '//telegram.org', 'https://telegram.org'))
                # set appropriate class to body
                file_to.write('<body class="{}">'.format(
                    ' '.join(soup.body['class'])))
                header_set = True

            for item in soup.find_all('div', {"class": "tgme_widget_message"}):
                file_to.write(str(item))
                errors = 0
        else:
            errors += 1

        post_id += 1

        # too many misses means there are no more posts
        if (errors > MAX_ERRORS):
            break

        # wait a bit before the next http request
        time.sleep(1)

    file_to.write('</body></html>')
    file_to.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Downloads all the posts from a telegram channel to an html file.')
    parser.add_argument('channel', type=str, help='name of the cannel')
    parser.add_argument('-i', type=int, metavar='post_id', required=False,
                        dest='from_post', default=0, help='copy from this post')
    parser.add_argument('-f', type=argparse.FileType('w'), metavar='file',
                        required=False, dest='file', help='output file')
    args = parser.parse_args()

    channel = args.channel
    post_start = args.from_post

    file_to = None
    if (args.file == None):
        file_to = open('channel + '.html', 'w')
    else:
        file_to = args.file

    download(channel, post_start, file_to)
