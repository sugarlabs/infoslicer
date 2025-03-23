# Copyright (C) IBM Corporation 2008

from bs4 import BeautifulSoup

#Extend beautiful soup HTML parsing library
#to recognise new self-closing tag <reference>
class NewtifulStoneSoup(BeautifulSoup):
    SELF_CLOSING_TAGS = {"reference"}

    def __init__(self, markup, *args, **kwargs):
        super().__init__(markup, *args, **kwargs)
        self._update_self_closing_tags()

    def _update_self_closing_tags(self):
        """Modify the builder to recognize <reference> as a self-closing tag."""
        if hasattr(self.builder, "self_closing_tags"):
            self.builder.self_closing_tags.update(self.SELF_CLOSING_TAGS)
