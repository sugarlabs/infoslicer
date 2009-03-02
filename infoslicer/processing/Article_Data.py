# Copyright (C) IBM Corporation 2008

import random

""" 
Created by Jonathan Mace

Each class in this file represents the data associated with an element of an article.

These are the data objects which are passed around to and from the Article class.
"""

class Sentence_Data:
    
    def __init__(self, id = None, source_article_id = -1, source_section_id = -1, source_paragraph_id = -1, source_sentence_id = -1, text = "", formatting = None):
        if id == None:
            self.id = random.randint(100, 100000)
        else:
            self.id = id
        self.source_article_id = source_article_id
        self.source_section_id = source_section_id
        self.source_paragraph_id = source_paragraph_id
        self.source_sentence_id = source_sentence_id
        self.text = text
        self.formatting = formatting
        self.type = "sentence"
        
class Picture_Data:
    
    def __init__(self, source_article_id = -1, text = None, orig=None):
        self.source_article_id = source_article_id
        self.id = 0
        self.text = text
        self.type = "picture"
        self.orig = orig
    

class Paragraph_Data:
    
    def __init__(self, id = None, source_article_id = -1, source_section_id = -1, source_paragraph_id = -1, sentences_data = []):
        if id == None:
            self.id = random.randint(100, 100000)
        else:
            self.id = id
        self.source_article_id = source_article_id
        self.source_section_id = source_section_id
        self.source_paragraph_id = source_paragraph_id
        self.sentences_data = sentences_data
        self.type = "paragraph"

class Section_Data:
    
    def __init__(self, id = None, source_article_id = -1, source_section_id = -1, paragraphs_data = []):
        if id == None:
            self.id = random.randint(100, 100000)
        else:
            self.id = id
        self.source_article_id = source_article_id
        self.source_section_id = source_section_id
        self.paragraphs_data = paragraphs_data 
        self.type = "section" 
        
class Article_Data:
    
    def __init__(self, id = None, source_article_id = -1, article_title = None, article_theme = None, sections_data = [], image_list=[]):
        if id == None:
            self.id = random.randint(100, 100000)
        else:
            self.id = id
        self.source_article_id = source_article_id
        self.article_title = article_title
        self.article_theme = article_theme
        self.sections_data = sections_data
        self.type = "article"
        self.image_list = image_list
    
    def get_image_list(self):
        return self.image_list
                
