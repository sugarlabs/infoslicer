# Copyright (C) 2012 Aneesh Dogra <lionaneesh@gmail.com>
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from re import sub
import logging
from html.parser import HTMLParser
from infoslicer.processing.article_data import SentenceData, ParagraphData, SectionData, ArticleData
logger = logging.getLogger('infoslicer:html_strip')

def filter_non_printable(text_content):
    return ''.join([c for c in text_content if ord(c) > 31 or ord(c) == 9])

class HTML_Strip(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.__text = []

    def handle_data(self, data):
        text = data.strip()
        if len(text) > 0:
            text = sub('[\t\r\n]+', '', text)
            # replace multiple spaces with one
            text = sub('[ ]+', ' ', text)
            text = filter_non_printable(text)
            self.__text.append(text + '')

    def handle_starttag(self, tag, attrs):
        if tag == 'p':
            self.__text.append('<PARAGRAPH>')
        elif tag == 'br':
            self.__text.append('<SENTENCE>')
        if tag == 'div':
            self.__text.append('<SECTION>')

    def text(self):
        return ''.join(self.__text).strip()


# takes in a HTML document and returns a list of Section objects.
def dehtml(text, title):
    try:
        parser = HTML_Strip()
        parser.feed(text)
        parser.close()
        text_stripped = parser.text()
        # We now need to convert this stripped data to an
        # Article Data object.
        sections = text_stripped.split('<SECTION>')
        section_objs = []
        for section in sections:
            s = section.strip()
            if s:
                paragraphs = text_stripped.split('<PARAGRAPH>')
                p_objs = []
                for para in paragraphs:
                    if para[:len('<SECTION>')] == '<SECTION>':
                        para = para[len('<SECTION>'):]
                    if para.endswith('<SECTION>'):
                        para = para[:-len('<SECTION>')]
                    p = para.strip()
                    if p:
                        sentences = para.split('<SENTENCE>')
                        s_objs = []
                        for sentence in sentences:
                            s = sentence.strip()
                            if s:
                                s_objs += [SentenceData(text=s)]
                                s_objs += [SentenceData(text='\n')]
                        p_objs += [ParagraphData(sentences_data=s_objs)]
                section_objs += [SectionData(paragraphs_data=p_objs)]
        return ArticleData(article_title=title, sections_data=section_objs)
    except Exception as e:
        logger.error('Error while stripping HTML: %s' % e)
        text_stripped = text
