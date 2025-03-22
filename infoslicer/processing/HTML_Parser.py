# Copyright (C) IBM Corporation 2008
# Wrap Beautiful Soup HTML parser up in custom class to add some
# Media Wiki and DITA specific parsing functionality.


import re
import logging
from datetime import date
from bs4 import BeautifulSoup, Tag
logger = logging.getLogger('infoslicer::html_parser')



# These lists are used at the pre-parsing stage
keep_tags = [ "html", "body", "p",  "h1", "h2", "h3", "h4", "h5", "h6",\
                "img", "table", "tr", "th", "td", "ol", "ul", "li", "sup", "sub"]  
remove_tags_keep_content= ["div", "span", "strong", "a", "i", "b", "u", "color", "font"]
REMOVE_CLASSES_REGEXP = ""

# These lists are used at the parsing stage
ROOT_NODE = "body"
section_separators = ["h2", "h3", "h4", "h5"]
reference_separators = ["h1"]
block_elements = ["img", "table", "ol", "ul"]



class NoDocException(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

class HTMLParser:


    def __init__(self, document_to_parse, title, source_url):
        if document_to_parse is None:
            raise NoDocException("No content to parse - supply document to __init__")
        self.soup = BeautifulSoup(document_to_parse, "html.parser")

        self.source = source_url
        xml_template = f'''<?xml version="1.0" encoding="utf-8"?>
        <reference>
            <title>{title}</title>
        </reference>'''

        self.output_soup = BeautifulSoup(xml_template, "html.parser")
        # First ID issued will be id below + 1
        self.ids = {"reference" : 1,\
                    "section" : 1,\
                    "p" : 1,\
                    "ph" : 1\
                    }
        self.image_list = self.tag_generator("reference", self.tag_generator("refbody"),[("id", "imagelist")])

    def create_paragraph(self, text, tag="p"):
        """
        Creates a new paragraph containing <ph> tags, surrounded by the specified tag
        @param text: Text to mark up
        @param tag: Tag to surround with (defaults to "p")
        @return: new tag
        """
        try:
            new_para = self.tag_generator(tag)
            text_str = text.decode('utf-8') if isinstance(text, bytes) else text
            sentences = re.split(re.compile(r"[\.\!\?\"] "), text_str)
            separators = re.findall(re.compile(r"[\.\!\?\"](?= )"), text_str)
            for i in range(len(sentences) - 1):
                new_para.append(self.tag_generator("ph", sentences[i] + separators[i]))
            new_para.append(self.tag_generator("ph", sentences[-1]))
            return new_para
        except Exception as e:
            logger.error(f"Error creating paragraph: {str(e)}")
            return self.tag_generator(tag)

    def get_publisher(self):
        """
            Extracts publisher from source URL
            @return: name of publisher
        """
        output = self.source.replace("http://", "").split("/")[0].split(".")
        return ".".join([output[-2], output[-1]])

    def image_handler(self):
        """
            Extracts image tags from the document
        """
        try:
            for img in self.soup.findAll("img"):
                too_small = False
                image_path = img['src']
                alt_text = ""
                if img.has_key("width") and img.has_key("height") and int(img['width']) <= 70 and int(img['height']) <= 70:
                    too_small = True
                if img.has_key("alt") and img['alt'] != "":
                    alt_text = img['alt']
                else:
                    alt_text = image_path.split("/")[-1]
                if (not too_small) and self.image_list.refbody.find(attrs={"href" : image_path}) is None:
                    self.image_list.refbody.append(self.tag_generator("image", "<alt>%s</alt>" % alt_text, [("href", image_path)]))
                img.extract()
        except Exception as e:
            logger.error(f"Error handling images: {str(e)}")

    def make_shortdesc(self):
        """
            Extracts 1st paragraph from input, and makes it a 'shortdesc' tag
            @return: new <shortdesc> tag containing contents of 1st paragraph
        """
        paragraphs = self.soup.findAll("p")
        for p in paragraphs:
            contents = p.renderContents().decode("utf-8")
            if len(contents) > 20 and (("." in contents) or ("?" in contents) or ("!" in contents)):
                p.extract()
                return self.create_paragraph(contents, "shortdesc")
        return self.tag_generator("shortdesc")

    def parse(self):
        """
            parses the document
            @return: String of document in DITA markup
        """
        try:
            #remove images
            self.image_handler()
            # pre-parse
            self.pre_parse()
            #identify the containing reference tag
            output_reference = self.output_soup.find("reference")
            #add the short description
            output_reference.append(self.make_shortdesc())
            #add the <prolog> tag to hold metadata
            output_reference.append(self.tag_generator("prolog"))
            #add the source url
            output_reference.prolog.append('<source href="%s" />' % self.source)
            #add the publisher
            output_reference.prolog.append(self.tag_generator("publisher", self.get_publisher()))
            the_date = date.today().strftime("%Y-%m-%d")
            #add created and modified dates
            output_reference.prolog.append(self.tag_generator('critdates', '<created date="%s" /><revised modified="%s" />' % (the_date, the_date)))
            #add the first refbody
            output_reference.append(self.tag_generator("refbody"))
            #track whether text should be inserted in a section or into the refbody
            in_section = False
            #set current refbody and section pointers
            current_refbody = output_reference.refbody
            current_section = None
            #call specialised method (redundant in this class, used for inheritance)
            self.specialise()
            #find the first tag
            tag = self.soup.find(ROOT_NODE).findChild()
            while tag is not None:
                #set variable to avoid hammering the string conversion function
                tag_name = tag.name
                #for debugging:
                #ignore the root node
                if tag_name == ROOT_NODE:
                    pass
                #paragraph action:
                elif tag_name == "p":
                    if in_section:
                        #tag contents as sentences and add to current section
                        current_section.append(self.create_paragraph(tag.renderContents()))
                    else:
                        #tag contents as sentences and add to current refbody
                        current_refbody.append(self.create_paragraph(tag.renderContents()))
                #section separator action
                elif tag_name in section_separators:
                    #create a new section tag
                    new_section = self.tag_generator("section")
                    #make a title for the tag from heading contents
                    new_section.append(self.tag_generator("title", tag.renderContents().decode("utf-8")))
                    #hold a pointer to the new section
                    current_section = new_section
                    #add the new section to the current refbody
                    current_refbody.append(new_section)
                    #currently working in a section, not a refbody
                    in_section = True
                #reference separator action:
                elif tag_name in reference_separators:
                    #no longer working in a section
                    in_section = False
                    #create a new reference tag
                    new_reference = self.tag_generator("reference")
                    #make a title for the tag from heading contents
                    new_reference.append(self.tag_generator("title", tag.renderContents().decode("utf-8")))
                    #create a refbody tag for the reference
                    new_refbody = self.tag_generator("refbody")
                    #add refbody to the reference tag
                    new_reference.append(new_refbody)
                    #remember the current refbody tag
                    current_refbody = new_refbody
                    #add the new reference to the containing reference tag in the output
                    output_reference.append(new_reference)
                #block element action
                elif tag_name in block_elements:
                    if in_section:
                        #add block element to current section
                        current_section.append(self.tag_generator(tag_name, tag.renderContents().decode("utf-8")))
                    else:
                        #add block element to new section
                        current_refbody.append(self.tag_generator("section", self.tag_generator(tag_name, tag.renderContents().decode("utf-8"))))
                #find the next tag and continue
                tag = tag.findNextSibling()
            #append the image list
            self.output_soup.reference.append(self.image_list)
            #return output as a properly indented string
            return self.fixHTML(self.output_soup.prettify())
        except Exception as e:
            logger.error(f"Error parsing document: {str(e)}")

    def pre_parse(self):
        """
            Prepares the input for parsing
        """
        for tag in self.soup.findAll(True, recursive=False):
            self.unTag(tag)

    def specialise(self):
        """
            Allows for specialised calls when inheriting
        """
        pass

    def tag_generator(self, tag, contents=None, attrs=[]):
        """
        Generates new tags for the output, adding IDs where appropriate
        @param tag: name of new tag
        @param contents: Optional, contents to add to tag
        @param attrs: Optional, attributes to add to tag
        @return: new Tag object
        """
        if tag in self.ids and attrs == []:
            self.ids[tag] += 1
            attrs = [("id", str(self.ids[tag]))]

        # Convert list of tuples to dictionary
        attrs_dict = dict(attrs) if attrs else {}

        new_tag = Tag(self.output_soup, name=tag, attrs=attrs_dict)
        if contents is not None:
            new_tag.insert(0, contents)
        return new_tag

    def unTag(self, tag):
        """
        Recursively removes unwanted tags according to defined lists
        @param tag: tag hierarchy to work on
        """
        # Skip processing if tag is None or has no name
        if not tag or not hasattr(tag, 'name') or not tag.name:
            return

        try:
            # Process children first (make a copy of children list to avoid modification during iteration)
            children = list(tag.findChildren(True, recursive=False))
            for child in children:
                self.unTag(child)

            # Check if tag has class attribute and process class matching
            if REMOVE_CLASSES_REGEXP and tag.get('class'):
                tag_classes = " ".join(tag.get("class")) if isinstance(tag.get("class"), list) else tag.get("class")
                if tag_classes and re.match(REMOVE_CLASSES_REGEXP, tag_classes):
                    tag.unwrap()  # Use unwrap instead of extract to keep contents
                    return
            if tag.name in keep_tags:
                # Keep the tag but clean it
                tag.attrs = {}  # Remove all attributes

            elif tag.name in remove_tags_keep_content:
                # Instead of creating new tags, just unwrap this one
                tag.unwrap()

            else:
                # Remove tags we don't want to keep
                tag.extract()

        except Exception as e:
            logger.error(f"Error processing tag {tag}: {str(e)}")
            tag.unwrap()

    def fixHTML(self, input_content):
        """fixes HTML entities and malformed tags in HTML
        
        @param input: input string to work on
        @return: modified version of input
        @rtype: string"""
        # First pass: Fix standard HTML entities
        try:
            content = input_content.replace("&lt;", " ").replace("&gt;", " ").replace("&quot;", '"').replace("sup", "")

            # Second pass: Remove HTML tags and citations
            patterns = [
                r'</?sup>',                    # Remove sup tags
                r'\[\d+\]',                    # Remove citation numbers
                r'&lt;/?sup&gt;',             # Remove escaped sup tags
                r'&lt;sup&gt;',               # Remove malformed sup tags
                r'\[citation needed\]',        # Remove citation needed tags
                r'\[\d+\)',                    # Remove citations with parentheses
                r'\s+',                        # Normalize whitespace
            ]

            for pattern in patterns:
                content = re.sub(pattern, ' ', content)

            # Clean up any remaining HTML entities
            content = re.sub(r'&[a-zA-Z]+;', '', content)  # Remove any other HTML entities
            content = re.sub(r'\s+', ' ', content)         # Clean up whitespace

            return content.strip()
        except Exception as e:
            logger.error('The error FixHTML %s', e)
