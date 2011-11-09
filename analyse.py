#!/usr/bin/env python
# -*- coding: utf-8 -*- 

##
## analyse.py - nltk_analyse dutch texts
## Simple web-enabled (dutch) named entities extractor
##
## Copyright (c) 2010-2012 Koninklijke Bibliotheek - National library of the Netherlands.
##
## this program is free software: you can redistribute it and/or modify
## it under the terms of the gnu general public license as published by
## the free software foundation, either version 3 of the license, or
## (at your option) any later version.
##
## this program is distributed in the hope that it will be useful,
## but without any warranty; without even the implied warranty of
## merchantability or fitness for a particular purpose. see the
## gnu general public license for more details.
##
## you should have received a copy of the gnu general public license
## along with this program. if not, see <http://www.gnu.org/licenses/>.
##

__author__ = "Willem Jan Faber"

import urllib
import codecs
import cgi
import ast
import os

# NLTK, see http://www.nltk.org/getting-started for details.
# won't work without nltk's downloads.

import nltk

from django.utils.html import strip_tags
from pprint import pprint

class Analyze(object):
    def __init__(self):
        form = cgi.FieldStorage()

        text = form.getvalue("text")
        url = form.getvalue("url")

        print "Content-Type: text/xml;charset=UTF-8; \n\n"
        print('<TPTAResponse version="TPTA nltk">')
        print('<entities>')

        i = 0
        error = False

        if url:
            try:
                data = strip_tags(urllib.urlopen(url).read()).encode('ascii', 'xmlcharrefreplace').replace(':' ,' ').replace(';', ' ')
            except:
                error = True
        elif text:
            try:
                data = strip_tags(text).encode('ascii', 'xmlcharrefreplace').replace(':' ,' ').replace(';', ' ')
                url = True
            except:
                error = True

        if not error:
            from nltk.tokenize import word_tokenize
            from nltk.tag import pos_tag
            from nltk.corpus import stopwords
            from nltk.stem import PorterStemmer

            stopwoorden = set(stopwords.words('dutch'))

            for j in ["de","het","het", "dit", "wel", "bron", "datum tijd onderwerp", "datum", "tijd", "onderwerp", "bron regels"]: 
                stopwoorden.add(j)

            for line in data.split('.'):
                if len(line.strip()) > 0:
                    words = nltk.ne_chunk(pos_tag(word_tokenize(line)))
                    known = {}
                    for word in words:
                        if type(word) == nltk.tree.Tree:
                            prefix=u"<misc>"
                            suffix=u"</misc>"
                            if str(word).find('PERSON') > -1:
                                prefix=u"<person>"
                                suffix=u"</person>"
                            word = u" ".join(i[0] for i in word.leaves()).strip()
                            nword = u""
                            for item in line[line.find(word):].split(' '):
                                if len(item.strip()) > 0:
                                    if item[0].isupper():
                                        nword += item.replace(',',' ').replace('De','')+" "
                                    else:
                                        break
                            if len(nword.strip()) > 0 and not nword.strip() in known and not nword.strip().lower() in stopwoorden:
                                known[nword.strip()] = True
                                print(prefix+nword.strip()+suffix)
                                i+=1

        if not url:
            if not error:
                print("<error>no url or text given</error>")
            else:
                print("<error>could not open requested url</error>")
        elif i == 0:
            print("<error>noentityfound</error>")

        print("</entities>")
        print("</TPTAResponse>")
    

if __name__ == "__main__":
    analyze=Analyze()

