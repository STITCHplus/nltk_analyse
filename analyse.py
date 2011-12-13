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
import sys
import os

# NLTK, see http://www.nltk.org/getting-started for details.
# won't work without nltk's downloads.

import nltk
import calendar
import locale
from lxml import etree

locale.setlocale(locale.LC_ALL, ('nl_NL', 'utf8@euro'))

month_names = []
for i in range(1,12): month_names.append(calendar.month_name[i])

from django.utils.html import strip_tags
from pprint import pprint

class Analyze(object):
    def __init__(self):
        form = cgi.FieldStorage()

        text = form.getvalue("text")
        url = form.getvalue("url")

        print "Content-Type: text/xml;charset=UTF-8; \n\n"

        i = 0
        error = False

        if url:
            data = strip_tags(urllib.urlopen(url).read()).encode('utf-8').replace(':' ,' ').replace(';', ' ')
        elif text:
            data = strip_tags(text).encode('utf-8').replace(':' ,'.').replace(';', '.')
            url = True

        if not error:
            from nltk.tokenize import word_tokenize
            from nltk.tag import pos_tag
            from nltk.corpus import stopwords
            from nltk.stem import PorterStemmer

            doc = etree.Element('TPTAResponse')
            docs = etree.SubElement(doc, 'entities')

            stopwoorden = set(stopwords.words('dutch'))

            for j in ["de","het","het", "dit", "wel", "bron", "datum tijd onderwerp", "datum", "tijd", "onderwerp", "bron regels"]: 
                stopwoorden.add(j)

            for line in data.split('.'):
                if len(line.strip()) > 2:
                    words = nltk.ne_chunk(pos_tag(word_tokenize(line)))
                    known = {}

                    for word in words:
                        if type(word) == nltk.tree.Tree:
                            if str(word).find('PERSON') > -1:
                                prefix="person"
                            elif str(word).find('ORGANIZATION') > -1:
                                person="organization"
                            else:
                                prefix = "misc"
                            word = unicode(" ").join(i[0] for i in word.leaves()).strip().encode('utf-8')
                            nword = None

                            for item in line[line.find(word):].split(' '):
                                if len(item) > 1:
                                    if nword == None:
                                        nword = unicode(item.decode('utf-8'))
                                    else:
                                        if item[0].isupper():
                                            nword += unicode(" " +item.decode('utf-8'))
                                        else:
                                            break

                            if not nword == None:
                                nword=nword.strip()
                                if nword.endswith(',') or nword.endswith(')') or nword.endswith('"'):
                                    nword=nword[:-1]
                                
                                nword=nword.strip()
                                if len(nword) > 0 and not nword in known and not nword.strip().lower() in stopwoorden and not nword.lower() in month_names:
                                    known[nword.strip()] = True
                                    text = etree.SubElement(doc, prefix)
                                    text.text = nword
                                    i+=1

        if not url:
            if not error:
                print("<error>no url or text given</error>")
            else:
                print("<error>could not open requested url</error>")
        elif i == 0:
            print("<error>noentityfound</error>")
        else:
            print(etree.tostring(doc))
        #print("<data>"+data.encode('ascii', 'xmlcharrefreplace')+"</data>")
    

if __name__ == "__main__":
    analyze=Analyze()

