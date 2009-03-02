# Copyright (C) IBM Corporation 2008

from BeautifulSoup import Tag
from NewtifulSoup import NewtifulStoneSoup as BeautifulStoneSoup
from Article_Data import *
import re
import os
import logging

logger = logging.getLogger('infoslicer')

"""
Created by Christopher Leonard.

ID descriptions:
0 - picture
1 - heading
> 1 - anything

This class converts between DITA and article_data representation of articles. Badly in need of refactoring!
"""
def get_article_from_dita(image_path, dita):
    """
    This method takes an article in DITA format as input, parses the DITA, and outputs the corresponding article_data object
    """
    has_shortdesc = False
    input = BeautifulStoneSoup(dita)
    article_id = input.resourceid['id']
    current_section_id = ""
    current_p_id = ""
    sentence_data_list = []
    paragraph_data_list = []
    section_data_list = []
    if input.find("shortdesc") != None:
        paragraph_data=[]
        for ph in input.shortdesc.findAll("ph"):
            id = ph['id']
            source_sentence_id = id
            source_paragraph_id = "shortdesc"
            source_section_id = "shortdesc"
            source_article_id = article_id
            text = ph.renderContents().replace("\n", "").replace("&amp;#160;", "").strip() + " "
            if text[0:5] == "Satur":
                logger.debug(unicode(text))
            sentence_data = Sentence_Data(id, source_article_id, source_section_id, source_paragraph_id, source_sentence_id, text)
            sentence_data_list.append(sentence_data)
        paragraph_data.append(Paragraph_Data("shortdesc", article_id, "shortdesc", "shortdesc", sentence_data_list))
        section_data = Section_Data("shortdesc", article_id, "shortdesc", paragraph_data)
        section_data_list.append(section_data)
        sentence_data_list = []
        input.shortdesc.extract()
        has_shortdesc = True
    taglist = input.findAll(re.compile("refbody|section|p|ph|image"))
    for i in xrange(len(taglist)):
        tag = taglist[len(taglist) - i - 1]
        if tag.name == "ph":
            id = tag['id']
            source_sentence_id = id
            source_paragraph_id = current_p_id
            source_section_id = current_section_id
            source_article_id = article_id
            text = tag.renderContents().replace("\n", "").replace("&amp;#160;", "").strip() + " "
            sentence_data = Sentence_Data(id, source_article_id, source_section_id, source_paragraph_id, source_sentence_id, text)
            sentence_data_list.insert(0, sentence_data)
        elif tag.name == "p":
            if not tag.has_key("id"):
                id = -1
            else:
                id = tag['id']
            source_paragraph_id = id
            source_section_id = current_section_id
            source_article_id = article_id
            paragraph_data = Paragraph_Data(id, source_article_id, source_section_id, source_paragraph_id, sentence_data_list)
            paragraph_data_list.insert(0, paragraph_data)
            sentence_data_list = []
            current_p_id = id
        elif tag.name == "refbody" :
            if tag.findParent("reference").has_key("id"):
                id = "r" + tag.findParent("reference")['id']
            else:
                id = "r90000"
            source_section_id = id
            source_article_id = article_id
            section_data = Section_Data(id, source_article_id, source_section_id, paragraph_data_list)
            if has_shortdesc:
                section_data_list.insert(1,section_data)
            else:
                section_data_list.insert(0,section_data)
            if tag.findChild("title", recursive=False) != None:
                heading = tag.findChild('title').renderContents().replace("\n", "").replace("&amp;#160;", "").strip()
                sen = Sentence_Data(1, source_article_id, source_section_id, 1, 1, heading)
                par = Paragraph_Data(1, source_article_id, source_section_id, 1, [sen])                    
                headingdata = Section_Data(1, source_article_id, source_section_id, [par])
                
                if has_shortdesc:
                    section_data_list.insert(1,headingdata)
                else:
                    section_data_list.insert(0,headingdata)                    
            paragraph_data_list = []
            current_section_id = tag.name[0] + id
            
        elif tag.name == "section":
            id = "s" + tag['id']
            source_section_id = id
            source_article_id = article_id

            section_data = Section_Data(id, source_article_id, source_section_id, paragraph_data_list)
            if has_shortdesc:
                section_data_list.insert(1,section_data)
            else:
                section_data_list.insert(0,section_data)
            if tag.findChild("title", recursive=False) != None:
                heading = tag.findChild('title').renderContents().replace("\n", "").replace("&amp;#160;", "").strip()
                sen = Sentence_Data(1, source_article_id, source_section_id, 1, 1, heading)
                par = Paragraph_Data(1, source_article_id, source_section_id, 1, [sen])                    
                headingdata = Section_Data(1, source_article_id, source_section_id, [par])
                
                if has_shortdesc:
                    section_data_list.insert(1,headingdata)
                else:
                    section_data_list.insert(0,headingdata)
            paragraph_data_list = []
            current_section_id = id
            
        elif tag.name == "image":
            
            if tag.parent.name == "p":
                source_article_id = article_id
                text = image_path + '/' + tag['href']
                if not os.path.exists(text):
                    logger.info('cannot find image %s' % text)
                else:
                    picture_data = Picture_Data(source_article_id, text,
                            tag['orig_href'])
                    sentence_data_list.insert(0, picture_data)
            
    article_title = input.find("title").renderContents().replace("\n", "").strip()
    
    image_list = []
    imglist_tag = input.find(True, attrs={"id" : "imagelist"})
    if imglist_tag != None:
        for img in imglist_tag.findAll("image"):
            caption = img.findChild("alt")
            if caption != None:
                caption = caption.renderContents().replace("\n", "").strip()
            else:
                caption = ""
            if not os.path.exists(os.path.join(image_path, img['href'])):
                logger.info('cannot find image %s' % img['href'])
            else:
                image_list.append((img['href'], caption, img['orig_href']))
    
    data = Article_Data(article_id, article_id, article_title, "theme", section_data_list, image_list)                   
    
    return data


def get_dita_from_article(image_path, article):
    """
    This method takes as input an instance of the Article class.
    It calls the getData method of the article class to get the article_data representation of the article.
    It then constructs the corresponding DITA representation of the article.
    """
    article_data = article.getData()
    output = BeautifulStoneSoup("<?xml version='1.0' encoding='utf-8'?><!DOCTYPE reference PUBLIC \"-//IBM//DTD DITA IBM Reference//EN\" \"ibm-reference.dtd\"><reference><title>%s</title><prolog></prolog></reference>" % article_data.article_title)
    current_ref = output.reference            
    current_title = None

    for section in article_data.sections_data:
        #headings check
        if len(section.paragraphs_data) == 1 and len(section.paragraphs_data[0].sentences_data) == 1 and section.paragraphs_data[0].sentences_data[0].id == 1:
            paragraph = section.paragraphs_data[0]
            current_title = paragraph.sentences_data[0].text
        elif str(section.id).startswith("r"):
            reference_tag = _tag_generator(output, "reference", attrs=[("id", section.id.replace("r", ""))])
            if current_title != None:
                reference_tag.append(_tag_generator(output, "title", contents=current_title))
                current_title = None
            reference_tag.append(_tag_generator(output, "refbody"))
            for paragraph in section.paragraphs_data:
                if paragraph.id == "shortdesc":
                    paragraph_tag = _tag_generator(output, "shortdesc")
                else:
                    paragraph_tag = _tag_generator(output, "p", attrs=[("id", str(paragraph.id))])
                for sentence in paragraph.sentences_data:
                    ph_tag = _tag_generator(output, "ph", attrs=[("id", str(sentence.id))], contents = sentence.text)
                    paragraph_tag.append(ph_tag)
                reference_tag.refbody.append(paragraph_tag) 
            output.reference.append(reference_tag)
            current_ref = reference_tag.refbody
        else:
            if section.id == "shortdesc":
                section_tag = _tag_generator(output, "section", attrs=[("id", "shortdesc")])
            else:
                section_tag = _tag_generator(output, "section", attrs=[("id", str(section.id).replace("s", ""))])
            if current_title != None:
                section_tag.append(_tag_generator(output, "title", contents=current_title))
                current_title = None
            for paragraph in section.paragraphs_data:
                paragraph_tag = _tag_generator(output, "p", attrs=[("id", str(paragraph.id))])
                for sentence in paragraph.sentences_data:
                    if sentence.type == "sentence":
                        ph_tag = _tag_generator(output, "ph", attrs=[("id", str(sentence.id))], contents = sentence.text)
                        paragraph_tag.append(ph_tag)
                    elif sentence.type == "picture":
                        # switch image to relative path
                        text = sentence.text.replace(image_path, '') \
                                .lstrip('/')
                        image_tag = _tag_generator(output,
                                "image", attrs=[("href", text),
                                                ('orig_href', sentence.orig)])
                        paragraph_tag.append(image_tag)
                    else:
                        logger.ebiug(sentence.type)
                        
                section_tag.append(paragraph_tag)
            current_ref.append(section_tag)
        if current_title != None:
            current_ref.append('<section id="56756757"><p id="6875534"><ph id="65657657">%s</ph></p></section>' % current_title)
            current_title = None
    if article_data.image_list != []:
        for unnecessary_tag in output.findAll(True, attrs={"id" : "imagelist"}):
            unnecessary_tag.extract()
        image_list = _tag_generator(output, "reference", [("id", "imagelist")])
        output.reference.append(image_list)
        image_list_body = _tag_generator(output, "refbody")
        image_list.append(image_list_body)
        for image in article_data.image_list:
            image_tag = _tag_generator(output, "image", [("href", image[0]), ("orig_href", image[2])], "<alt>" + image[-1] + "</alt>")
            image_list_body.append(image_tag)
    dita = output.prettify()

    return dita
            
def _tag_generator(soup, name, attrs=[], contents=None):
    if attrs != []:
        new_tag = Tag(soup, name, attrs)
    else:
        new_tag = Tag(soup, name)
    if contents != None:
        new_tag.insert(0, contents)
    return new_tag
