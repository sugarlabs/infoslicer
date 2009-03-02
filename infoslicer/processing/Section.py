# Copyright (C) IBM Corporation 2008

from Paragraph import *
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
a Section instance contains a list of paragraphs.  It has methods for inserting,
deleting and rearranging paragraphs within itself, as well as other housekeeping
functions.

"""

class RawSection:
    
    def __init__(self, id, source_article_id, source_section_id, paragraphs, buf):
        self.id = id
        self.source_article_id = source_article_id
        self.source_section_id = source_section_id
        self.paragraphs = paragraphs
        self.buf = buf
        
    def insertParagraph(self, paragraph_data, lociter):
        insertionindex = self.__get_best_paragraph(lociter)
        insertioniter = self.paragraphs[insertionindex].getStart()
        paragraph = Paragraph(paragraph_data, self.buf, insertioniter)
        self.paragraphs.insert(insertionindex, paragraph)            
        
    def deleteParagraph(self, lociter):
        deletionindex = self.__get_exact_paragraph(lociter)
        if deletionindex != len(self.paragraphs) - 1:
            paragraph = self.paragraphs[deletionindex]
            paragraph.delete()
            del self.paragraphs[deletionindex]
        if len(self.paragraphs) == 1:
            return True
        else:
            return False
        
    def removeParagraph(self, lociter):
        removalindex = self.__get_exact_paragraph(lociter)
        if removalindex != len(self.paragraphs) - 1:
            paragraph = self.paragraphs[removalindex]
            paragraph.delete()
            del self.paragraphs[removalindex]
        if len(self.paragraphs) == 1:
            return True
        else:
            return False
        
    def splitParagraph(self, lociter):
        paragraphindex = self.__get_exact_paragraph(lociter)
        paragraph = self.paragraphs[paragraphindex]
        source_article_id = paragraph.source_article_id
        source_section_id = paragraph.source_section_id
        source_paragraph_id = paragraph.source_paragraph_id
        firstdata = paragraph.getDataRange(paragraph.getStart(), lociter)
        seconddata = paragraph.getDataRange(lociter, paragraph.getEnd())
        mark = self.buf.create_mark(None, lociter, False)
        if firstdata != [] and seconddata != []:
            self.deleteParagraph(lociter)
            
            insertioniter = self.buf.get_iter_at_mark(mark)
            paragraphdata = Paragraph_Data(None, source_article_id, source_section_id, source_paragraph_id, firstdata)
            paragraph = Paragraph(paragraphdata, self.buf, insertioniter)
            self.paragraphs.insert(paragraphindex, paragraph)   
                
            insertioniter = self.buf.get_iter_at_mark(mark)
            paragraphdata = Paragraph_Data(None, source_article_id, source_section_id, source_paragraph_id, seconddata)
            paragraph = Paragraph(paragraphdata, self.buf, insertioniter)
            self.paragraphs.insert(paragraphindex+1, paragraph)   
            
        
        
                
    def delete(self):
        for paragraph in self.paragraphs:
            paragraph.delete()
            
    def remove(self):
        for paragraph in self.paragraphs:
            paragraph.remove()
            
    def deleteSelection(self, startiter, enditer):
        startindex = self.__get_exact_paragraph(startiter)
        endindex = self.__get_exact_paragraph(enditer)
        if endindex == len(self.paragraphs)-1:
            endindex = endindex - 1
        if startindex == endindex:
            empty = self.paragraphs[startindex].deleteSelection(startiter, enditer)
            if empty:
                self.paragraphs[startindex].delete()
                del self.paragraphs[startindex]
        elif startindex < endindex:
            startmark = self.buf.create_mark(None, startiter, True)
            endmark = self.buf.create_mark(None, enditer, True)
            
            endparagraph = self.paragraphs[endindex]
            empty = endparagraph.deleteSelection(endparagraph.getStart(), self.buf.get_iter_at_mark(endmark))
            if empty:
                self.paragraphs[endindex].delete()
                del self.paragraphs[endindex]
            self.buf.delete_mark(endmark)
            
            for i in range(startindex+1, endindex):
                self.paragraphs[startindex+1].delete()
                del self.paragraphs[startindex+1]
            
            startparagraph = self.paragraphs[startindex]
            empty = startparagraph.deleteSelection(self.buf.get_iter_at_mark(startmark), startparagraph.getEnd())
            if empty:
                self.paragraphs[startindex].delete()
                del self.paragraphs[startindex]
            self.buf.delete_mark(startmark)
        if len(self.paragraphs) == 1:
            return True
        else:
            return False
        
    
    def getParagraph(self, lociter):
        paragraphindex = self.__get_exact_paragraph(lociter)
        return self.paragraphs[paragraphindex]   
    
    def getBestParagraph(self, lociter):
        paragraphindex = self.__get_best_paragraph(lociter)
        if paragraphindex == len(self.paragraphs):
            return self.paragraphs[-1]
        else:
            return self.paragraphs[paragraphindex]
        
    def getStart(self):
        return self.paragraphs[0].getStart()
    
    def getEnd(self):
        return self.paragraphs[-1].getEnd()
        
    def __get_best_paragraph(self, lociter):
        paragraphindex = self.__get_exact_paragraph(lociter)
        paragraph = self.paragraphs[paragraphindex]
        left = paragraph.getStart().get_offset()
        middle = lociter.get_offset()
        right = paragraph.getEnd().get_offset()
        leftdist = middle - left
        rightdist = right - middle
        
        if (paragraphindex < len(self.paragraphs)) and (leftdist > rightdist):
            paragraphindex = paragraphindex +1 
        return paragraphindex
        
    def __get_exact_paragraph(self, lociter):
        i = 0
        for i in range(len(self.paragraphs)-1):
            start = self.paragraphs[i+1].getStart()
            if lociter.compare(start) == -1:
                return i
        return len(self.paragraphs)-1
    
    def getId(self):
        return self.id
    
    def getData(self):
        id = self.id
        source_article_id = self.source_article_id
        source_section_id = self.source_section_id
        paragraphs_data = []
        for paragraph in self.paragraphs[0:len(self.paragraphs)-1]:
            paragraphs_data.append(paragraph.getData())
        
        data = Section_Data(id, source_article_id, source_section_id, paragraphs_data)
        return data
    
    def getDataRange(self, startiter, enditer):
        startindex = self.__get_exact_paragraph(startiter)
        endindex = self.__get_exact_paragraph(enditer)
        if startindex == endindex:
            return self.paragraphs[startindex].getDataRange(startiter, enditer)
        else:
            startdata = []
            startparagraph = self.paragraphs[startindex]
            if startiter.compare(startparagraph.getStart()) == 0:
                startdata.append(self.paragraphs[startindex].getData())
            else:
                startdata.extend(startparagraph.getDataRange(startiter, startparagraph.getEnd()))
                dummydata = Sentence_Data(id = -1, text = "")
                startdata.append(dummydata)
            
            middledata = []
            for paragraph in self.paragraphs[startindex+1:endindex]:
                middledata.append(paragraph.getData())
                
            enddata = [] 
            if endindex != len(self.paragraphs):           
                endparagraph = self.paragraphs[endindex]
                enddata.extend(endparagraph.getDataRange(endparagraph.getStart(), enditer))
                
            data = startdata + middledata + enddata
                
            return data
    
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
        
    def getParagraphs(self):
        return self.paragraphs 
    
    def pad(self):
        # Pad adds a dummy paragraph containing the sentence " ", to this section
        insertioniter = self.paragraphs[-1].getStart()
        dummydata = Sentence_Data(id = -1, text = " ")
        dummyparagraphdata = Paragraph_Data(id = -1, sentences_data = [dummydata])
        paragraph = Paragraph(dummyparagraphdata, self.buf, insertioniter)
        self.paragraphs.insert(-1, paragraph)
        
    def clean(self):
        # Removes the effects of pad.
        # Returns true if, after removing the pad, the section has no meaningful content and can therefore be destroyed
        if len(self.paragraphs) > 1:
            paragraph = self.paragraphs[-2]
            paragraphisempty = paragraph.clean()  
            if paragraphisempty:
                del self.paragraphs[-2]
            if len(self.paragraphs) == 1:
                return True
            else:
                return False
        else:
            return True
        
    def getText(self):
        return self.buf.get_slice(self.getStart(), self.getEnd())
        
    def checkIntegrity(self, nextiter):
        i = 0
        paragraphs = []
        while i < len(self.paragraphs) - 1:
            paragraph = self.paragraphs[i]
            nextparagraph = self.paragraphs[i+1]
            
            if paragraph.getStart().compare(nextparagraph.getStart()) == -1:
                text = self.buf.get_slice(paragraph.getStart(), nextparagraph.getStart())
                if len(text) > 0 and text[-1] != "\n":
                    logger.debug("concatenating paragraphs")
                    nextparagraph.sentences = paragraph.sentences + nextparagraph.sentences
                else:
                    paragraphs.extend(paragraph.checkIntegrity(nextparagraph.getStart()))
            else:
                paragraph.remove()
                del self.paragraphs[i]
                i = i - 1
            
            i = i + 1
                    
        paragraph = self.paragraphs[-1]
        
        if paragraph.getStart().compare(nextiter) == -1:
            paragraphs.extend(paragraph.checkIntegrity(nextiter))
        
        sections = []
        paragraphstart = 0
        for i in range(len(paragraphs)-1):
            if paragraphs[i].getText() == "\n":
                sections.append(RawSection(self.id, self.source_article_id, self.source_section_id, paragraphs[paragraphstart:i+1], self.buf))
                paragraphstart = i + 1
        sections.append(RawSection(self.id, self.source_article_id, self.source_section_id, paragraphs[paragraphstart:len(paragraphs)], self.buf))

        return sections
    
    def generateIds(self):
        if self.id == None or self.id == -1:
            self.id = random.randint(100, 100000)
        for paragraph in self.paragraphs[0:len(self.paragraphs)]:
            paragraph.generateIds()
        self.paragraphs[-1].id = -1

class Section( RawSection ):
        
    def __init__(self, section_data, buf, insertioniter):
        id = section_data.id
        source_article_id = section_data.source_article_id
        source_section_id = section_data.source_section_id
        
        paragraphs = []
        insertionmark = buf.create_mark(None, insertioniter, False)
          
        for paragraph_data in section_data.paragraphs_data:
            insertioniter = buf.get_iter_at_mark(insertionmark)
            paragraphs.append(Paragraph(paragraph_data, buf, insertioniter))
            
        insertioniter = buf.get_iter_at_mark(insertionmark)
        endparagraphdata = Paragraph_Data(id = 1, sentences_data = [])
        paragraphs.append(Paragraph(endparagraphdata, buf, insertioniter))
        
        buf.delete_mark(insertionmark)
        
        RawSection.__init__(self, id, source_article_id, source_section_id, paragraphs, buf)
     
class dummySection(Section):
    def __init__(self, buf, insertioniter, leftgravity):
        self.id = -1
        self.source_article_id = -1
        self.source_section_id = -1
        self.buf = buf
        self.paragraphs = [ dummyParagraph(buf, insertioniter, leftgravity) ]

