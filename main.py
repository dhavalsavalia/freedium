import argparse
import re
import lxml.html.clean
import urllib
import os

import requests
from bs4 import BeautifulSoup


class Medium:
    """
        Base class to perform operations
    """
    # TODO Show debug messages
    # TODO Make user page beautiful
    def __init__(self, article_url):
        self.article_url = article_url
        self.article_response = requests.get(article_url)
        self.soup = BeautifulSoup(self.article_response.text, "html.parser")

    def clean_crap(self):
        """
            Cleans most of the Medium crap that it adds
        """
        # TODO Make use of filter or something
        # I am NOOB lol
        for e in self.soup.findAll('img'):
            # this is to prevent those blurry images
            # and some sizing related issues
            try:
                e['sizes']
                e['class'] = 'img-fluid mx-auto d-block'
                del e['sizes']
                del e['width']
                del e['height']
                img_src = e['srcset'].split()[0]
                del e['srcset']
                e['src'] = img_src
            except:
                e.extract()

        for e in self.soup.findAll('a'):
            # this is to overcome relative linking issue
            # also gets domain name! how lame? I know.
            if e['href'].startswith('/'):
                self.domain = re.search(r'^http[s]*:\/\/[\w\.]*', self.article_url).group()
                e['href'] = self.domain+e['href']

        for e in self.soup.findAll('figcaption'):
            # Some stupid styling
            e['class'] = 'blockquote text-center'

        for e in self.soup.findAll('blockquote'):
            # and some more
            e['class'] = 'text-center'

        return 0


    def get_article_meta(self):
        """
            Parces meta-data of the article
        """
        self.title = self.soup.title.string.split(" – ",1)[0]
        self.author_link = self.soup.find(property='article:author')['content']
        self.subtitle = self.soup.find(property='og:description')['content']
        for tag in self.soup.find_all("meta"):
            if tag.get("name", None) == "author":
                self.author = tag.get("content", None)

            if tag.get("name", None) == "twitter:data1":
                self.read_time = tag.get("value", None)

        self.published_date = self.soup.find(property='article:published_time')['content'][:10]
        self.published_time = self.soup.find(property='article:published_time')['content'][11:19]
        # TODO use html injection
        return_string = f"""<html>
    <head>
        <title>{self.title}</title>
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">
        <link href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,500;0,700;1,400;1,500;1,700&display=swap" rel="stylesheet">
    </head>
    <body class="text-justify" style="font-family: \'Lora\', serif;">
        <div class="container">
        <h1 class="display-4">{self.title}</h1>
        <h2><small class="text-muted">{self.subtitle}</small></h2>
        <a href="{self.author_link}">{self.author}</a>
        <br>Published Datetime: {self.published_date} {self.published_time} | {self.read_time}
        <hr>"""
        return return_string

    def get_article_content(self):
        """
            Parces content of the article
        """
        # TODO Fix h1, h2 for subheaders of content
        # TODO Fix inline Medium links
        content = self.soup.find('article').find('div').find_all(['section', 'hr','pre'])
        final_content = ''
        for count, element in enumerate(content):
            if count==0:
                for i in element.find_all(['p', 'figure', 'li', 'pre']):
                    final_content += i.prettify()
            else:
                final_content += element.prettify()

        final_content += '\t\t</div>\n\t</body>\n</html>'
        return final_content


def parse():
    """
        (IGNORE) Here for future purposes
    """
    parser = argparse.ArgumentParser(
        "freedium",
        description="Medium knowledge for free!"
    )
    parser.add_argument(
        '-u',
        '--user',
        # dest='user',
        help='The username for medium',
        required=True
    )
    return parser.parse_args()

def get_article_name(article_url):
    article_url_ist = article_url.split('/')
    site_name = article_url_ist[2].split('.')[0]
    article_name = article_url_ist[-1]
    article_name = "-".join(article_name.split('-')[:-1])

    file_name = article_name + "-" + site_name + ".html"

    return file_name




def main():
    article_url = input('Please enter article url: ')
    article_fetcher = Medium(article_url)
    article_fetcher.clean_crap()
    article_meta = article_fetcher.get_article_meta()
    article_content = article_fetcher.get_article_content()
    file_name = get_article_name(article_url)
    content = article_meta + '\n' + article_content
    # TODO Use title-slug | possibly with publication
    with open(os.path.join('Output', file_name), 'w') as html_file:
        html_file.write(content)

if __name__=='__main__':
    main()
