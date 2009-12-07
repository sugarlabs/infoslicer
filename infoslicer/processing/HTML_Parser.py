# Copyright (C) IBM Corporation 2008

from BeautifulSoup import BeautifulSoup, Tag
from NewtifulSoup import NewtifulStoneSoup as BeautifulStoneSoup
import re
from datetime import date

class NoDocException(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

"""
Wrap Beautiful Soup HTML parser up in custom class to add some 
Media Wiki and DITA specific parsing functionality.
"""
class HTML_Parser:
    
    #=======================================================================
    # These lists are used at the pre-parsing stage
    keep_tags = [ "html", "body", "p",  "h1", "h2", "h3", "h4", "h5", "h6",\
                 "img", "table", "tr", "th", "td", "ol", "ul", "li", "sup", "sub"]  
    remove_tags_keep_content= ["div", "span", "strong", "a", "i", "b", "u", "color", "font"]
    remove_classes_regexp = ""
    #=======================================================================
    
    #=======================================================================
    # These lists are used at the parsing stage
    root_node = "body"
    section_separators = ["h2", "h3", "h4", "h5"]
    reference_separators = ["h1"]
    block_elements = ["img", "table", "ol", "ul"]
    #=======================================================================
        
    def __init__(self, document_to_parse, title, source_url):
        if document_to_parse == None:
            raise NoDocException("No content to parse - supply document to __init__")
        self.input = BeautifulSoup(document_to_parse)
        self.source = source_url
        self.output_soup = BeautifulStoneSoup('<?xml version="1.0" encoding="utf-8"?><reference><title>%s</title></reference>' % title)
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
        new_para = self.tag_generator(tag)
        sentences = re.split(re.compile("[\.\!\?\"] "), text)
        separators = re.findall(re.compile("[\.\!\?\"](?= )"), text)
        for i in range(len(sentences) - 1):
            new_para.append(self.tag_generator("ph", sentences[i] + separators[i]))
        new_para.append(self.tag_generator("ph", sentences[-1]))
        return new_para
    
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
        for img in self.input.findAll("img"):
            too_small = False
            image_path = img['src']    
            alt_text = ""
            if img.has_key("width") and img.has_key("height") and int(img['width']) <= 70 and int(img['height']) <= 70:
                too_small = True
            if img.has_key("alt") and img['alt'] != "":
                alt_text = img['alt']
            else:
                alt_text = image_path.split("/")[-1]
            if (not too_small) and self.image_list.refbody.find(attrs={"href" : image_path}) == None:
                self.image_list.refbody.append(self.tag_generator("image", "<alt>%s</alt>" % alt_text, [("href", image_path)]))
            img.extract()

    def make_shortdesc(self):
        """
            Extracts 1st paragraph from input, and makes it a 'shortdesc' tag
            @return: new <shortdesc> tag containing contents of 1st paragraph
        """
        paragraphs = self.input.findAll("p")
        for p in paragraphs:
            contents = p.renderContents()
            if len(contents) > 20 and (("." in contents) or ("?" in contents) or ("!" in contents)):
                p.extract()
                return self.create_paragraph(contents, "shortdesc")
        return self.tag_generator("shortdesc")

    def parse(self):
        """
            parses the document
            @return: String of document in DITA markup
        """
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
        tag = self.input.find(self.root_node).findChild()
        while tag != None:
            #set variable to avoid hammering the string conversion function
            tag_name = tag.name
            #for debugging:
            #ignore the root node
            if tag_name == self.root_node:
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
            elif tag_name in self.section_separators:
                #create a new section tag
                new_section = self.tag_generator("section")
                #make a title for the tag from heading contents
                new_section.append(self.tag_generator("title", tag.renderContents()))
                #hold a pointer to the new section
                current_section = new_section
                #add the new section to the current refbody
                current_refbody.append(new_section)
                #currently working in a section, not a refbody
                in_section = True
            #reference separator action:
            elif tag_name in self.reference_separators:
                #no longer working in a section
                in_section = False
                #create a new reference tag
                new_reference = self.tag_generator("reference")
                #make a title for the tag from heading contents
                new_reference.append(self.tag_generator("title", tag.renderContents()))
                #create a refbody tag for the reference
                new_refbody = self.tag_generator("refbody")
                #add refbody to the reference tag
                new_reference.append(new_refbody)
                #remember the current refbody tag
                current_refbody = new_refbody
                #add the new reference to the containing reference tag in the output
                output_reference.append(new_reference)
            #block element action
            elif tag_name in self.block_elements:
                if in_section:
                    #add block element to current section
                    current_section.append(self.tag_generator(tag_name, tag.renderContents()))
                else:
                    #add block element to new section
                    current_refbody.append(self.tag_generator("section", self.tag_generator(tag_name, tag.renderContents())))
            #find the next tag and continue
            tag = tag.findNextSibling()
        #append the image list
        self.output_soup.reference.append(self.image_list)
        #return output as a properly indented string
        return self.output_soup.prettify()
    
    def pre_parse(self):
        """
            Prepares the input for parsing
        """
        for tag in self.input.findAll(True, recursive=False):
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
        if self.ids.has_key(tag) and attrs == []:
            self.ids[tag] += 1
            attrs = [("id", str(self.ids[tag]))]
        if attrs != []:
            new_tag = Tag(self.output_soup, tag, attrs)
        else:
            new_tag = Tag(self.output_soup, tag)
        if contents != None:
            new_tag.insert(0, contents)
        attrs = []
        return new_tag
    
    def unTag(self, tag):
        """
            recursively removes unwanted tags according to defined lists
            @param tag: tag hierarchy to work on
        """
        for child in tag.findChildren(True, recursive=False):
            self.unTag(child)
        if (self.remove_classes_regexp != "") and (tag.has_key("class") and (re.match(self.remove_classes_regexp, tag["class"]) != None)):
            tag.extract()
        elif tag.name in self.keep_tags:
            new_tag = Tag(self.input, tag.name)
            new_tag.contents = tag.contents
            tag.replaceWith(new_tag)

        elif tag.name in self.remove_tags_keep_content:            
            children = tag.findChildren(True, recursive=False)
            if len(children)==1:
                tag.replaceWith(children[0])
            elif len(children) > 1:
                new_tag = Tag(self.input, "p")
                for child in tag.findChildren(True, recursive=False):
                    new_tag.append(child)
                tag.replaceWith(new_tag)
            else:
                tag.replaceWith(tag.renderContents())
        else:
            tag.extract()        
      
            
