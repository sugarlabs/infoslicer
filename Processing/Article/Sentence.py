# Copyright (C) IBM Corporation 2008

import pygtk
pygtk.require('2.0')
import os
import gtk
import logging

from Article_Data import *

"""
Created by Jonathan Mace

The classes here each correspond to a sentence in the given text buffer.

You should not instantiate these classes directly.

Use the "level above" class or the Article class to apply changes to the textbuffer
or structure of the article.

"""

"""
A sentence keeps textmarks corresponding to the start and end of the sentence in the buffer.

It has methods for restructuring itself in the event that the textbuffer changes
from an action not controlled by the Article object it is contained in.

"""

logger = logging.getLogger('infoslicer')

class RawSentence:
    
    def __init__(self, id, source_article_id, source_section_id, source_paragraph_id, source_sentence_id, buf, formatting, leftmark, rightmark):
        self.id = id
        self.source_article_id = source_article_id
        self.source_section_id = source_section_id
        self.source_paragraph_id = source_paragraph_id
        self.source_sentence_id = source_sentence_id
        self.buf = buf
        self.formatting = formatting
        self.leftmark = leftmark
        self.rightmark = rightmark   
        self.type = "sentence"
        
    def generateIds(self):
        if self.id == None or self.id == -1:
            self.id = random.randint(100, 100000)
    
    def delete(self):
        b = self.buf
        l = b.get_iter_at_mark(self.leftmark)
        r = b.get_iter_at_mark(self.rightmark)
        b.delete(l, r)
        b.delete_mark(self.leftmark)
        b.delete_mark(self.rightmark)
        
    def remove(self):
        b = self.buf
        b.delete_mark(self.leftmark)
        b.delete_mark(self.rightmark)
        
    def getStart(self):
        return self.buf.get_iter_at_mark(self.leftmark)
        
    def getEnd(self):    
        return self.buf.get_iter_at_mark(self.rightmark)
    
    def getId(self):
        return self.id
    
    def getData(self):
        id = self.id
        source_article_id = self.source_article_id
        source_section_id = self.source_section_id
        source_paragraph_id = self.source_paragraph_id
        source_sentence_id = self.source_sentence_id
        text = self.getText()
        formatting = self.formatting
        
        data = Sentence_Data(id, source_article_id, source_section_id, source_paragraph_id, source_sentence_id, text, formatting)
        return data
    
    def getText(self):
        return self.buf.get_slice(self.getStart(), self.getEnd())
    
    def checkIntegrity(self, nextiter):
        text = unicode(self.buf.get_slice(self.getStart(), nextiter))
        lines = text.splitlines(True)
        sentencestartoffset = self.getStart().get_offset()
        sentences = []
        if text == "":
            return []
        else:
            for line in lines:
                if line == "":
                    pass
                elif line == "\n":
                    startmark = self.buf.create_mark(None, self.buf.get_iter_at_offset(sentencestartoffset), False)
                    endmark = self.buf.create_mark(None, self.buf.get_iter_at_offset(sentencestartoffset + 1), True)
                    sentences.append(RawSentence(self.id, self.source_article_id, self.source_section_id, self.source_paragraph_id, self.source_sentence_id, self.buf, self.formatting, startmark, endmark))
                    sentencestartoffset = sentencestartoffset + 1
                elif line[-1] == "\n":
                    startmark = self.buf.create_mark(None, self.buf.get_iter_at_offset(sentencestartoffset), False)
                    endmark = self.buf.create_mark(None, self.buf.get_iter_at_offset(sentencestartoffset + len(line)-1), True)
                    sentences.append(RawSentence(self.id, self.source_article_id, self.source_section_id, self.source_paragraph_id, self.source_sentence_id, self.buf, self.formatting, startmark, endmark))
                    sentencestartoffset = sentencestartoffset + len(line)-1
                    startmark = self.buf.create_mark(None, self.buf.get_iter_at_offset(sentencestartoffset), False)
                    endmark = self.buf.create_mark(None, self.buf.get_iter_at_offset(sentencestartoffset + 1), True)
                    sentences.append(RawSentence(self.id, self.source_article_id, self.source_section_id, self.source_paragraph_id, self.source_sentence_id, self.buf, self.formatting, startmark, endmark))
                    sentencestartoffset = sentencestartoffset + 1
                else:
                    startmark = self.buf.create_mark(None, self.buf.get_iter_at_offset(sentencestartoffset), False)
                    endmark = self.buf.create_mark(None, self.buf.get_iter_at_offset(sentencestartoffset + len(line)), True)
                    sentences.append(RawSentence(self.id, self.source_article_id, self.source_section_id, self.source_paragraph_id, self.source_sentence_id, self.buf, self.formatting, startmark, endmark))
        
        return sentences    

class Sentence( RawSentence ):
    
    def __init__(self, sentence_data, buf, insertioniter):
        
        id = sentence_data.id
        source_article_id = sentence_data.source_article_id
        source_section_id = sentence_data.source_section_id
        source_paragraph_id = sentence_data.source_paragraph_id
        source_sentence_id = sentence_data.source_sentence_id
        
        """ 
        Here, apply formatting changes when necessary.
        Yet to be implemented. """
        formatting = sentence_data.formatting
                
        rightmark = buf.create_mark(None, insertioniter, True)
        leftmark = buf.create_mark(None, insertioniter, False)
        buf.insert(insertioniter, unicode(sentence_data.text))
        left = buf.get_iter_at_mark(rightmark)
        right = buf.get_iter_at_mark(leftmark)
        buf.move_mark(leftmark, left)
        buf.move_mark(rightmark, right)
        
        RawSentence.__init__(self, id, source_article_id, source_section_id, source_paragraph_id, source_sentence_id, buf, formatting, leftmark, rightmark)

class Picture( RawSentence ):
    
    def __init__(self, picture_data, buf, insertioniter):
        id = 0
        source_article_id = picture_data.source_article_id
        source_section_id = 0
        source_paragraph_id = 0
        source_sentence_id = 0
        formatting = [] 
        
        self.text = picture_data.text
        self.orig = picture_data.orig
        
        rightmark = buf.create_mark(None, insertioniter, True)
        leftmark = buf.create_mark(None, insertioniter, False)
        
        if os.path.isfile(picture_data.text):
            pixbuf = gtk.gdk.pixbuf_new_from_file(picture_data.text) 
            buf.insert_pixbuf(insertioniter, pixbuf)
        else:
            logger.warning('cannot open image %s' % picture_data.text)
        
        left = buf.get_iter_at_mark(rightmark)
        right = buf.get_iter_at_mark(leftmark)
        buf.move_mark(leftmark, left)
        buf.move_mark(rightmark, right)   
        
        RawSentence.__init__(self, id, source_article_id, source_section_id, source_paragraph_id, source_sentence_id, buf, formatting, leftmark, rightmark)
        self.type = "picture"
        
    def getData(self):
        return Picture_Data(self.source_article_id, self.text, self.orig)

    def checkIntegrity(self, nextiter):
        sentences = []
        if self.getEnd().compare(nextiter) == 0:
            return [self]
        elif self.getStart().compare(self.getEnd()) > 0:
             sentences.append(self)
             if self.getEnd().compare(nextiter) > 0: 
                startmark = self.buf.create_mark(None, self.getEnd(), False)
                endmark = self.buf.create_mark(None, nextiter, True)
                nextsentence = RawSentence(self.source_article_id, 1, 1, 1, self.buf, [], startmark, endmark)
                nextsentences = nextsentence.checkIntegrity(nextiter)
                sentences.extend(nextsentences)
        return sentences
        

class dummySentence( Sentence ):
    def __init__(self, buf, insertioniter, leftgravity):
        self.id = -1
        self.source_article_id = -1
        self.source_section_id = -1
        self.source_paragraph_id = -1
        self.source_sentence_id = -1
        self.text = ""
        self.formatting = []
        self.buf = buf
        self.leftmark = self.buf.create_mark(None, insertioniter, leftgravity)
        self.rightmark = self.buf.create_mark(None, insertioniter, leftgravity)  
        self.type = "dummysentence"
   
