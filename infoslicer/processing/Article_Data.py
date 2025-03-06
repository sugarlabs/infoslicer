# Copyright (C) IBM Corporation 2008
# Created by Jonathan Mace
# Each class in this file represents the data associated with an element of an article.
# These are the data objects which are passed around to and from the Article class.


import random


class SentenceData:
    """
    A class to represent sentence data within an article.
    """
    def __init__(
        self,
        idz=None,
        source_article_id=-1,
        source_section_id=-1,
        source_paragraph_id=-1,
        source_sentence_id=-1,
        text="",
        formatting=None,
    ):
        if idz is None:
            self.id = random.randint(100, 100000)
        else:
            self.id = idz
        self.source_article_id = source_article_id
        self.source_section_id = source_section_id
        self.source_paragraph_id = source_paragraph_id
        self.source_sentence_id = source_sentence_id
        self.text = text
        self.formatting = formatting
        self.type = "sentence"


class PictureData:
    def __init__(self, source_article_id=-1, text=None, orig=None):
        self.source_article_id = source_article_id
        self.id = 0
        self.text = text
        self.type = "picture"
        self.orig = orig


class ParagraphData:
    def __init__(
        self,
        idz=None,
        source_article_id=-1,
        source_section_id=-1,
        source_paragraph_id=-1,
        sentences_data=None,
    ):
        if idz is None:
            self.id = random.randint(100, 100000)
        else:
            self.id = idz
        if sentences_data is None:
            sentences_data = []
        self.source_article_id = source_article_id
        self.source_section_id = source_section_id
        self.source_paragraph_id = source_paragraph_id
        self.sentences_data = sentences_data
        self.type = "paragraph"


class SectionData:
    def __init__(
        self, idz=None, source_article_id=-1, source_section_id=-1, paragraphs_data=None
    ):
        if idz is None:
            self.id = random.randint(100, 100000)
        else:
            self.id = idz
        if paragraphs_data is None:
            paragraphs_data = []
        self.source_article_id = source_article_id
        self.source_section_id = source_section_id
        self.paragraphs_data = paragraphs_data
        self.type = "section"


class ArticleData:
    def __init__(
        self,
        idz=None,
        source_article_id=-1,
        article_title=None,
        article_theme=None,
        sections_data=None,
        image_list=None,
    ):
        if idz is None:
            self.id = random.randint(100, 100000)
        else:
            self.id = idz
        if sections_data is None:
            sections_data = []
        if image_list is None:
            image_list = []
        self.source_article_id = source_article_id
        self.article_title = article_title
        self.article_theme = article_theme
        self.sections_data = sections_data
        self.type = "article"
        self.image_list = image_list

    def get_image_list(self):
        return self.image_list
