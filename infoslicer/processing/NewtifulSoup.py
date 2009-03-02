# Copyright (C) IBM Corporation 2008

from BeautifulSoup import BeautifulStoneSoup

#Extend beautiful soup HTML parsing library 
#to recognise new self-closing tag <reference> 
class NewtifulStoneSoup(BeautifulStoneSoup):
    NESTABLE_TAGS = BeautifulStoneSoup.NESTABLE_TAGS
    NESTABLE_TAGS['reference'] = 'reference'