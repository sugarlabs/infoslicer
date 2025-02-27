# Copyright (C) IBM Corporation 2008

import logging
import os
import re

from bs4 import Tag
from infoslicer.processing.article_data import (
    ArticleData,
    ParagraphData,
    PictureData,
    SectionData,
    SentenceData,
)
from infoslicer.processing.newtiful_soup import NewtifulStoneSoup as BeautifulStoneSoup

logger = logging.getLogger("infoslicer:Article_Builder")

"""
Created by Christopher Leonard.

ID descriptions:
0 - picture
1 - heading
> 1 - anything

"""


def get_article_from_dita(image_path, dita):
    """
    This method takes an article in DITA format as input, parses the DITA, and 
    outputs the corresponding article_data object
    """
    has_shortdesc = False
    soup = BeautifulStoneSoup(dita)
    article_id = soup.resourceid["id"]
    current_section_id = ""
    current_p_id = ""
    sentence_data_list = []
    paragraph_data_list = []
    section_data_list = []
    if soup.find("shortdesc") is not None:
        paragraph_data = []
        for ph in soup.shortdesc.findAll("ph"):
            idz = ph["id"]
            source_sentence_id = idz
            source_paragraph_id = "shortdesc"
            source_section_id = "shortdesc"
            source_article_id = article_id
            text = (
                ph.renderContents().replace("\n", "").replace("&amp;#160;", "").strip()
                + " "
            )
            if text[0:5] == "Satur":
                logger.debug(text)
            sentence_data = SentenceData(
                idz,
                source_article_id,
                source_section_id,
                source_paragraph_id,
                source_sentence_id,
                text,
            )
            sentence_data_list.append(sentence_data)
        paragraph_data.append(
            ParagraphData(
                "shortdesc", article_id, "shortdesc", "shortdesc", sentence_data_list
            )
        )
        section_data = SectionData(
            "shortdesc", article_id, "shortdesc", paragraph_data
        )
        section_data_list.append(section_data)
        sentence_data_list = []
        input.shortdesc.extract()
        has_shortdesc = True
    taglist = input.findAll(re.compile("refbody|section|p|ph|image"))
    for i in range(len(taglist)):
        tag = taglist[len(taglist) - i - 1]
        if tag.name == "ph":
            idz = tag["id"]
            source_sentence_id = idz
            source_paragraph_id = current_p_id
            source_section_id = current_section_id
            source_article_id = article_id
            text = (
                tag.renderContents().replace("\n", "").replace("&amp;#160;", "").strip()
                + " "
            )
            sentence_data = SentenceData(
                idz,
                source_article_id,
                source_section_id,
                source_paragraph_id,
                source_sentence_id,
                text,
            )
            sentence_data_list.insert(0, sentence_data)
        elif tag.name == "p":
            if not tag.has_key("id"):
                idz = -1
            else:
                idz = tag["id"]
            source_paragraph_id = idz
            source_section_id = current_section_id
            source_article_id = article_id
            paragraph_data = ParagraphData(
                idz,
                source_article_id,
                source_section_id,
                source_paragraph_id,
                sentence_data_list,
            )
            paragraph_data_list.insert(0, paragraph_data)
            sentence_data_list = []
            current_p_id = idz
        elif tag.name == "refbody":
            if tag.findParent("reference").has_key("id"):
                idz = "r" + tag.findParent("reference")["id"]
            else:
                idz = "r90000"
            source_section_id = idz
            source_article_id = article_id
            section_data = SectionData(
                idz, source_article_id, source_section_id, paragraph_data_list
            )
            if has_shortdesc:
                section_data_list.insert(1, section_data)
            else:
                section_data_list.insert(0, section_data)
            if tag.findChild("title", recursive=False) is not None:
                heading = (
                    tag.findChild("title")
                    .renderContents()
                    .replace("\n", "")
                    .replace("&amp;#160;", "")
                    .strip()
                )
                sen = SentenceData(
                    1, source_article_id, source_section_id, 1, 1, heading
                )
                par = ParagraphData(1, source_article_id, source_section_id, 1, [sen])
                headingdata = SectionData(
                    1, source_article_id, source_section_id, [par]
                )

                if has_shortdesc:
                    section_data_list.insert(1, headingdata)
                else:
                    section_data_list.insert(0, headingdata)
            paragraph_data_list = []
            current_section_id = tag.name[0] + idz

        elif tag.name == "section":
            idz = "s" + tag["id"]
            source_section_id = idz
            source_article_id = article_id

            section_data = SectionData(
                idz, source_article_id, source_section_id, paragraph_data_list
            )
            if has_shortdesc:
                section_data_list.insert(1, section_data)
            else:
                section_data_list.insert(0, section_data)
            if tag.findChild("title", recursive=False) is not None:
                heading = (
                    tag.findChild("title")
                    .renderContents()
                    .replace("\n", "")
                    .replace("&amp;#160;", "")
                    .strip()
                )
                sen = SentenceData(
                    1, source_article_id, source_section_id, 1, 1, heading
                )
                par = ParagraphData(1, source_article_id, source_section_id, 1, [sen])
                headingdata = SectionData(
                    1, source_article_id, source_section_id, [par]
                )

                if has_shortdesc:
                    section_data_list.insert(1, headingdata)
                else:
                    section_data_list.insert(0, headingdata)
            paragraph_data_list = []
            current_section_id = idz

        elif tag.name == "image":
            if tag.parent.name == "p":
                source_article_id = article_id
                text = image_path + "/" + tag["href"]
                if not os.path.exists(text):
                    logger.info("cannot find image %s", text)
                else:
                    picture_data = PictureData(
                        source_article_id, text, tag["orig_href"]
                    )
                    sentence_data_list.insert(0, picture_data)

    article_title = input.find("title").renderContents().replace("\n", "").strip()

    image_list = []
    imglist_tag = input.find(True, attrs={"id": "imagelist"})
    if imglist_tag is not None:
        for img in imglist_tag.findAll("image"):
            caption = img.findChild("alt")
            if caption is not None:
                caption = caption.renderContents().replace("\n", "").strip()
            else:
                caption = ""
            if not os.path.exists(os.path.join(image_path, img["href"])):
                logger.info("cannot find image %s", img["href"])
            else:
                image_list.append((img["href"], caption, img["orig_href"]))

    data = ArticleData(
        article_id, article_id, article_title, "theme", section_data_list, image_list
    )

    return data


def get_dita_from_article(image_path, article):
    """
    This method takes as input an instance of the Article class.
    It calls the getData method of the article class to get the article_data 
    representation of the article.
    It then constructs the corresponding DITA representation of the article.
    """
    article_data = article.getData()
    output = BeautifulStoneSoup(
        "<?xml version='1.0' encoding='utf-8'?><!DOCTYPE reference PUBLIC \"-//IBM//DTD DITA IBM Reference//EN\" \"ibm-reference.dtd\"><reference><title>%s</title><prolog></prolog></reference>"
        % article_data.article_title
    )
    current_ref = output.reference
    current_title = None

    for section in article_data.sections_data:
        # headings check
        if (
            len(section.paragraphs_data) == 1
            and len(section.paragraphs_data[0].sentences_data) == 1
            and section.paragraphs_data[0].sentences_data[0].id == 1
        ):
            paragraph = section.paragraphs_data[0]
            current_title = paragraph.sentences_data[0].text
        elif str(section.id).startswith("r"):
            reference_tag = _tag_generator(
                output, "reference", attrs=[("id", section.id.replace("r", ""))]
            )
            if current_title is not None:
                reference_tag.append(
                    _tag_generator(output, "title", contents=current_title)
                )
                current_title = None
            reference_tag.append(_tag_generator(output, "refbody"))
            for paragraph in section.paragraphs_data:
                if paragraph.id == "shortdesc":
                    paragraph_tag = _tag_generator(output, "shortdesc")
                else:
                    paragraph_tag = _tag_generator(
                        output, "p", attrs=[("id", str(paragraph.id))]
                    )
                for sentence in paragraph.sentences_data:
                    ph_tag = _tag_generator(
                        output,
                        "ph",
                        attrs=[("id", str(sentence.id))],
                        contents=sentence.text,
                    )
                    paragraph_tag.append(ph_tag)
                reference_tag.refbody.append(paragraph_tag)
            output.reference.append(reference_tag)
            current_ref = reference_tag.refbody
        else:
            if section.id == "shortdesc":
                section_tag = _tag_generator(
                    output, "section", attrs=[("id", "shortdesc")]
                )
            else:
                section_tag = _tag_generator(
                    output, "section", attrs=[("id", str(section.id).replace("s", ""))]
                )
            if current_title is not None:
                section_tag.append(
                    _tag_generator(output, "title", contents=current_title)
                )
                current_title = None
            for paragraph in section.paragraphs_data:
                paragraph_tag = _tag_generator(
                    output, "p", attrs=[("id", str(paragraph.id))]
                )
                for sentence in paragraph.sentences_data:
                    if sentence.type == "sentence":
                        ph_tag = _tag_generator(
                            output,
                            "ph",
                            attrs=[("id", str(sentence.id))],
                            contents=sentence.text,
                        )
                        paragraph_tag.append(ph_tag)
                    elif sentence.type == "picture":
                        # switch image to relative path
                        text = sentence.text.replace(image_path, "").lstrip("/")
                        image_tag = _tag_generator(
                            output,
                            "image",
                            attrs=[("href", text), ("orig_href", sentence.orig)],
                        )
                        paragraph_tag.append(image_tag)
                    else:
                        logger.ebiug(sentence.type)

                section_tag.append(paragraph_tag)
            current_ref.append(section_tag)
        if current_title is not None:
            current_ref.append(
                '<section id="56756757"><p id="6875534"><ph id="65657657">%s</ph></p></section>'
                % current_title
            )
            current_title = None
    if article_data.image_list != []:
        for unnecessary_tag in output.findAll(True, attrs={"id": "imagelist"}):
            unnecessary_tag.extract()
        image_list = _tag_generator(output, "reference", [("id", "imagelist")])
        output.reference.append(image_list)
        image_list_body = _tag_generator(output, "refbody")
        image_list.append(image_list_body)
        for image in article_data.image_list:
            image_tag = _tag_generator(
                output,
                "image",
                [("href", image[0]), ("orig_href", image[2])],
                "<alt>" + image[-1] + "</alt>",
            )
            image_list_body.append(image_tag)
    dita = output.prettify()

    return dita


def _tag_generator(soup, name, attrs=None, contents=None):
    if attrs is None:
        attrs = []
    if attrs != []:
        new_tag = Tag(soup, name, attrs)
    else:
        new_tag = Tag(soup, name)
    if contents is not None:
        new_tag.insert(0, contents)
    return new_tag
