#!/usr/bin/python
# -*- coding: utf-8 -*-
from gettext import gettext as _
from bs4 import BeautifulSoup


def parse_dita(dita_str):
    soup = BeautifulSoup(dita_str)

    html = open('article.html', 'r').read().decode('utf-8')

    html_tags = []

    title = soup.find('title').string.strip()
    h1_title = '<h1>%(title)s</h1>' % \
        {'title': title}
    index_link = '<p><a href="librarymap.html">' + \
        _('Return to index') + '</a></p>'

    html_tags.append(index_link)
    html_tags.append(h1_title)

    for section in soup.findAll('section'):
        for p in section.findAll('p'):
            images = p.findAll('image')
            for img in images:
                html_tags.append('<img src="%(src)s" />' % \
                                      {'src': img.get('href')})
            html_tags.append('<p>')
            for ph in p.findAll('ph'):
                html_tags.append(ph.string.strip())
            html_tags.append('</p>')

    html = html % {'title': title,
                   'body': '\n'.join(html_tags)}
    return html


def parse_ditamap(ditamap_str):
    soup = BeautifulSoup(ditamap_str)
    html = open('article.html', 'r').read().decode('utf-8')

    html_tags = []

    title = soup.find('map').get('title')

    h1_title = '<h1>%(title)s</h1>' % \
        {'title': title}
    html_tags.append(h1_title)

    html_tags.append('<li>')
    for topic in soup.findAll('topicref'):
        dita_path = topic.get('href')
        html_tags.append('<ul><a href="%(href)s">%(name)s</a></ul>' % \
                             {'href': dita_path.replace('.dita', '.html'),
                              'name': topic.get('navtitle')})
    html_tags.append('</li>')

    html = html % {'title': title,
                   'body': '\n'.join(html_tags)}
    return html
