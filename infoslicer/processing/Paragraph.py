# Copyright (C) IBM Corporation 2008

from Sentence import *
import logging

logger = logging.getLogger('infoslicer')

"""
Created by Jonathan Mace

The classes here each correspond to a sentence in the given text buffer.

You should not instantiate these classes directly.

Use the "level above" class or the Article class to apply changes to the textbuffer
or structure of the article.

"""

"""
a Paragraph instance contains a list of sentences.  It has methods for inserting,
deleting and rearranging sentences within itself, as well as other housekeeping
functions.

"""

class RawParagraph:
    
    def __init__(self, id, source_article_id, source_section_id, source_paragraph_id, sentences, buf):
        self.id = id
        self.source_article_id = source_article_id
        self.source_section_id = source_section_id
        self.source_paragraph_id = source_paragraph_id
        self.sentences = sentences
        self.buf = buf
        
    def insertSentence(self, sentence_data, lociter):
        insertionindex = self.__get_best_sentence(lociter)
        insertioniter = self.sentences[insertionindex].getStart()
        if sentence_data.type == "sentence":
            sentence = Sentence(sentence_data, self.buf, insertioniter)
        elif sentence_data.type == "picture":
            sentence = Picture(sentence_data, self.buf, insertioniter)
        else:
            logger.debug("WARNING, WEIRD SENTENCES: %s" % (sentence_data.type))
        self.sentences.insert(insertionindex, sentence)
        
    def deleteSentence(self, lociter):
        deletionindex = self.__get_exact_sentence(lociter)
        if deletionindex != len(self.sentences) - 1:
            sentence = self.sentences[deletionindex]
            sentence.delete()
            del self.sentences[deletionindex]
        if len(self.sentences) == 1:
            return True
        else:
            return False
        
    def removeSentence(self, lociter):
        removalindex = self.__get_exact_sentence(lociter)
        if removalindex != len(self.sentences) - 1:
            sentence = self.sentences[removalindex]
            sentence.remove()
            del self.sentences[removalindex]
        if len(self.sentences) == 1:
            return True
        else:
            return False
        
    def delete(self):
        for sentence in self.sentences:
            sentence.delete()
    
    def deleteSelection(self, startiter, enditer):
        startindex = self.__get_exact_sentence(startiter)
        endindex = self.__get_exact_sentence(enditer)
        for i in range(startindex, endindex):
            self.sentences[startindex].delete()
            del self.sentences[startindex]
        if len(self.sentences) == 1:
            return True
        else:
            return False
            
    def remove(self):
        for sentence in self.sentences:
            sentence.remove()

    def getSentence(self, lociter):
        sentenceindex = self.__get_exact_sentence(lociter)
        return self.sentences[sentenceindex]
    
    def getBestSentence(self, lociter):
        sentenceindex = self.__get_best_sentence(lociter)
        if sentenceindex == len(self.sentences):
            return self.sentences[-1]
        else:
            return self.sentences[sentenceindex]
        
    def getStart(self):
        return self.sentences[0].getStart()
    
        
    def getEnd(self):
        return self.sentences[-1].getEnd()
        
    def __get_best_sentence(self, lociter):
        sentenceindex = self.__get_exact_sentence(lociter)
        sentence = self.sentences[sentenceindex]
        left = sentence.getStart().get_offset()
        middle = lociter.get_offset()
        right = sentence.getEnd().get_offset()
        leftdist = middle - left
        rightdist = right - middle
        
        if (sentenceindex < len(self.sentences)) and (leftdist > rightdist):
            sentenceindex = sentenceindex +1 
        return sentenceindex
        
        
    def __get_exact_sentence(self, lociter):
        i = 0
        for i in range(len(self.sentences)-1):
            start = self.sentences[i+1].getStart()
            if lociter.compare(start) == -1:
                return i
        return len(self.sentences) - 1
    
    def getId(self):
        return self.id
    
    def getData(self):
        id = self.id
        source_article_id = self.source_article_id
        source_section_id = self.source_section_id
        source_paragraph_id = self.source_paragraph_id
        sentences_data = []
        for sentence in self.sentences[0:len(self.sentences)-1]:
            sentences_data.append(sentence.getData())
        
        data = Paragraph_Data(id, source_article_id, source_section_id, source_paragraph_id, sentences_data)
        return data
    
    def getDataRange(self, startiter, enditer):
        startindex = self.__get_exact_sentence(startiter)
        endindex = self.__get_exact_sentence(enditer)
        sentences_data = []
        for sentence in self.sentences[startindex:endindex]:
            sentences_data.append(sentence.getData())
        return sentences_data
    
    def mark(self):
        markiter = self.getStart()
        self.markmark = self.buf.create_mark(None, markiter, True)
        arrow = gtk.gdk.pixbuf_new_from_xpm_data(arrow_xpm)
        self.buf.insert_pixbuf(markiter, arrow)
        
    def unmark(self):
        markiter = self.buf.get_iter_at_mark(self.markmark)
        markenditer = self.buf.get_iter_at_offset(markiter.get_offset()+1)
        self.buf.delete(markiter, markenditer)
        self.buf.delete_mark(self.markmark)
        
    def getSentences(self):
        return self.sentences
    
    def getText(self):
        return self.buf.get_slice(self.getStart(), self.getEnd())
    
    def clean(self):
        if len(self.sentences) > 1:
            sentence = self.sentences[-2]
            if sentence.getId() == -1:
                sentence.delete()
                del self.sentences[-2]
            if len(self.sentences) == 1:
                return True
            else:
                return False
        return True
    
    def checkIntegrity(self, nextiter):
        
        i = 0
        sentences = []
        while i < len(self.sentences) - 1:
            sentence = self.sentences[i]
            nextsentence = self.sentences[i+1]
            
            if sentence.getStart().compare(nextsentence.getStart()) == -1:
                sentences.extend(sentence.checkIntegrity(nextsentence.getStart()))
            else:
                sentence.remove()
                del self.sentences[i]
                i = i - 1
                
            i = i + 1
                
        sentence = self.sentences[-1]
        if sentence.getStart().compare(nextiter) == -1:
            sentences.extend(sentence.checkIntegrity(nextiter))
            
        paragraphs = []
        paragraphstart = 0
        for i in range(len(sentences)-1):
            if sentences[i].getText() == "\n":
                paragraphs.append(RawParagraph(self.id, self.source_article_id, self.source_section_id, self.source_paragraph_id, sentences[paragraphstart:i+1], self.buf))
                paragraphstart = i + 1
        paragraphs.append(RawParagraph(self.id, self.source_article_id, self.source_section_id, self.source_paragraph_id, sentences[paragraphstart:len(sentences)], self.buf))
        
        return paragraphs
    
    def generateIds(self):
        if self.id == None or self.id == -1:
            self.id = random.randint(100, 100000)
        for sentence in self.sentences[0:len(self.sentences)-1]:
            sentence.generateIds()
        self.sentences[-1].id = -1
       
class Paragraph( RawParagraph ):
        
    def __init__(self, paragraph_data, buf, insertioniter):
        id = paragraph_data.id
        source_article_id = paragraph_data.source_article_id
        source_section_id = paragraph_data.source_section_id
        source_paragraph_id = paragraph_data.source_paragraph_id
        
        sentences = []
        
        insertionmark = buf.create_mark(None, insertioniter, False)
        for sentence_data in paragraph_data.sentences_data:
            insertioniter = buf.get_iter_at_mark(insertionmark)
            if sentence_data.type == "sentence":
                sentence = Sentence(sentence_data, buf, insertioniter)
            elif sentence_data.type == "picture":
                sentence = Picture(sentence_data, buf, insertioniter)
            else:
                logger.debug("WARNING, WEIRD SENTENCES: %s" %
                        (sentence_data.type))
            sentences.append(sentence)
            
        insertioniter = buf.get_iter_at_mark(insertionmark)
        endsentencedata = Sentence_Data(id = -1, text = "\n")
        sentences.append(Sentence(endsentencedata, buf, insertioniter))
        
        buf.delete_mark(insertionmark)
        
        RawParagraph.__init__(self, id, source_article_id, source_section_id, source_paragraph_id, sentences, buf)
    
    
class dummyParagraph( Paragraph ):
    def __init__(self, buf, insertioniter, leftgravity):
        self.id = -1
        self.source_article_id = -1
        self.source_section_id = -1
        self.source_paragraph_id = -1
        self.buf = buf
        self.sentences = [ dummySentence(buf, insertioniter, leftgravity) ]              
