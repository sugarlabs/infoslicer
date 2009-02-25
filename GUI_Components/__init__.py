# Copyright (C) IBM Corporation 2008 
"""
Every class of type *_Pane has the following.
Thank python for not having interfaces.

pane.panel
pane.toolbar

These correspond to the main view and toolbar associated with this pane.

set_source_article
get_source_article
set_working_article
get_working_article

The GUI passes the currently selected source and working articles between panes
when panes are switched.  The pane will always be given an article using
set_source_article before the get_source_article method is called.  Thus it is
feasible to just save the article argument and return it in the get method.

"""
