#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Receives a Bibtex file and produces the markdown files for academic-hugo theme

@author: Petros Aristidou
@contact: p.aristidou@ieee.org
@date: 19-10-2017
@version: alpha
"""

import bibtexparser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase
import os, sys, getopt, re
import datetime


def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
    

# check if the date entry is the correct format, i.e., year-month-day
def IsDateFormatValid(str):
    try:
        datetime.datetime.strptime(str, '%Y-%m-%d')
        return True
    except ValueError as err:
        print(err)
        return False
    

# check if the date entry is the correct format, i.e., year-month
def IsOtherDateFormatValid(str):
    try:
        datetime.datetime.strptime(str, '%Y-%m')
        return True
    except ValueError as err:
        print(err)
        return False


# remove all decorative expression in a string
def supetrim(string):
    return string.replace("\\" , "").replace("{" , "").replace("}" , "").replace("\n"," ")


def month_string_to_number(string):
    m = {
        'jan':1,
        'feb':2,
        'mar':3,
        'apr':4,
        'may':5,
        'jun':6,
        'jul':7,
        'aug':8,
        'sep':9,
        'oct':10,
        'nov':11,
        'dec':12
        }
    s = string.strip()[:3].lower()

    try:
        out = m[s]
        return out
    except:
        raise ValueError('Not a month')
        
        
# convert 01, 02, 03 etc to Jan, Feb, Mar etc
def month_number_to_string(num):
    m = {
        1:'Jan',
        2:'Feb',
        3:'Mar',
        4:'Apr',
        5:'May',
        6:'Jun',
        7:'Jul',
        8:'Aug',
        9:'Sep',
        10:'Oct',
        11:'Nov',
        12:'Dec'
        }

    try:
        out = m[num]
        return out
    except:
        raise ValueError('Not a month')

        
# remove empty elements from a string
def removeEmptyString(inStr):
    while("" in inStr):
        inStr.remove("") 
        

# convert bib entry ID to firstAuthor-year-journal-otherInfo format
def formatID(inStr):
    # if the format is already correct in bibtex
    if '-' in inStr:
        return inStr
    #for example, str1 = 'meza2012:report:nvm
    elif ':' in inStr:
        return inStr.replace(':', "-")
    else:
        # e.g., 'li2018iscaCnnDnn'
        # before the year
        a = re.split('[^a-zA-Z]', inStr)
        # year
        b = re.split('[a-zA-Z]', inStr)
        removeEmptyString(a)
        removeEmptyString(b)
        # journal name
        c = re.split('[A-Z][a-zA-Z]*', a[1])
        removeEmptyString(c)
        # other info
        d = re.findall('[A-Z][a-zA-Z]*', a[1])
        outStr = '-'.join([a[0]] + b + c + d)
        return outStr.lower()


def main(argv):
    inputfile = ''
    try:
        opts, args = getopt.getopt(argv, "hi:", ["ifile="])
    except getopt.GetoptError:
        print('parse_bib.py -i <inputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('parse_bib.py -i <inputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
    return inputfile


if __name__ == "__main__":
    inputfile = main(sys.argv[1:])

    try:
        with open(inputfile, encoding="utf8") as bibtex_file:
            bibtex_str = bibtex_file.read()
    except EnvironmentError:  # parent of IOError, OSError *and* WindowsError where available
        print('File '+inputfile+' not found or some other error...')

    # It takes the type of the bibtex entry and maps to a corresponding category of the academic theme
    # Publication type.
    # Legend:
    # 0 = Uncategorized
    # 1 = Conference paper
    # 2 = Journal article
    # 3 = Preprint / Working Paper
    # 4 = Report
    # 5 = Book
    # 6 = Book section
    # 7 = Thesis
    # 8 = Patent
    pubtype_dict = {
        'Uncategorized': '"0"',
        'misc': '"0"',
        'inproceedings': '"1"',
        'conference': '"1"',
        'article': '"2"',
        'submitted': '"3"',
        'preprint': '"3"',
        'techreport': '"4"',
        'book': '"5"',
        'incollection': '"6"',
        'phdthesis': '"7"',
        'mastersthesis': '"7"',
        'patent': '"8"',
    }
    
    bib_database = bibtexparser.loads(bibtex_str)
    currDate = datetime.datetime.now()  # today's date in year, month, day.
    numRef = 0

    for entry in bib_database.entries:
        numRef += 1
        print(str(numRef) + ": " + entry['ID'])
        
        # only True when date entry contains month info or month entry available
        monthInfoAvailable = False

        dirName = formatID(entry['ID'])
#        filedir = 'content/en/publication/'+entry['ID'] 
        filedir = 'publication/' + dirName
        if not os.path.exists(filedir):
            os.mkdir(filedir)
#        filenm = 'content/en/publication/'+entry['ID']+'/index.md'
        filenm = 'publication/'+ dirName + '/index.md'
        
        # If the same publication exists, then skip the creation. I customize the .md files later, so I don't want them overwritten. Only new publications are created.
        if os.path.isfile(filenm):
            print("publication " + dirName + " already exists. Skipping...")
            pass
        else:
            with open(filenm, 'w', encoding='utf8') as the_file:
                the_file.write('---\n')

                the_file.write('draft: false\n')  # assume every bib entry will be published

                # Treating the title of the publication
                the_file.write('title: "'+supetrim(entry['title'])+'"\n')
                print('Parsing ' + dirName)

                # Treating the authors
                if 'author' in entry:
                    authors = entry['author'].split(' and ')
                    the_file.write('authors: [')
                    authors_str = ''
                    for author in authors:
                        author_strip = supetrim(author)
                        author_split = author_strip.split(',')
                        # two naming conventions in bibtex: "LastName, FirstName" or "FirstName LastName"
                        ## 1st case: "LastName, FirstName"
                        if len(author_split)==2:
                            author_strip = author_split[1].strip() + ' ' +author_split[0].strip()
                        # comment out as we just need to print the full name
                        #author_split = author_strip.split(' ')
                        #author_strip = author_split[0][0]+'. '+' '.join(map(str, author_split[1:]))
                        authors_str = authors_str+ '"'+author_strip+'",'
                    the_file.write(authors_str[:-1]+']\n')
                
                # Date
                # formatting publication date to be YYYY-MM-DD
                if 'date' in entry:
                    monthInfoAvailable = True # assume month info always in date entry
                    print('original date entry:', entry['date'])
                    # date format: year-month-day
                    if IsDateFormatValid(entry['date']):
                        origDate = datetime.datetime.strptime(entry['date'], '%Y-%m-%d')  #in datetime.datetime datetype
                        pubDate = str(origDate.year) + '-' + str(origDate.month).zfill(2) + '-' + str(origDate.day).zfill(2)
                        print('formatted date with existing date (year-month-day): ' + pubDate)
                    # date format: year-month
                    elif IsOtherDateFormatValid(entry['date']):
                        origDate = datetime.datetime.strptime(entry['date'], '%Y-%m')
                        pubDate = str(origDate.year) + '-' + str(origDate.month).zfill(2) + '-01'
                        print('formatted date with existing date (year-month): ' + pubDate)
                    pubMonth = month_number_to_string(origDate.month) # used for "publication" item in index.md
                    print('publication month: ' + pubMonth)
#                    print('when date in entry: ' + pubDate)
                    the_file.write('date: ' + pubDate + '\n')
                elif 'year' in entry:
                    pubDate = entry['year']
                    print('original date entry:', pubDate)
                    if 'month' in entry:
                        monthInfoAvailable = True
                        print('publication month:', entry['month'])
                        # month is in digital format, i.e. 01, 02, ...,12
                        if RepresentsInt(entry['month']):
                            month = entry['month'] # string
                        else:
                            # convert Jan, Feb, etc to 01, 02, ...
                            month = str(month_string_to_number(entry['month']))
                        pubDate = pubDate + '-' + month.zfill(2) + '-01'
                        pubMonth = month_number_to_string(int(month))
                        print('formatted date with existing year and month entry: ' + pubDate)
                        print('publication month: '+ pubMonth)
                    else: 
                        # first, check if the status of the publication
                        if 'pubstate' in entry:
                            pubState = entry['pubstate']
                            print(pubState)
                            if pubState == 'forthcoming' or pubState == 'upcoming' or pubState == 'accepted':
                                pubDate = str(currDate.year) + '-' + str(currDate.month).zfill(2) + '-' + str(currDate.day).zfill(2)
                                print('upcoming publication date: '+ pubDate)
                            else:  #draft, submitted, under review, preprint, etc.
                                pubDate = pubDate + '-01-01'                
                        else: # most likely the entry is for an old publication with only published year               
                            pubDate = pubDate + '-01-01'
                        print('publication with only year entry: ' + pubDate)
#                    print('when year in entry: ' + pubDate)
                    the_file.write('date: ' + pubDate + '\n')
                else:  # rare case, no year, month, day info
                    print('Error: No publication date - check the bib entry')
                    the_file.write('date: N/A\n')

                # DOI
                if 'doi' in entry:
                    the_file.write('doi: "'+supetrim(entry['doi'])+'"\n')
                            
                # Treating the publication type
                the_file.write('# Publication type.\n')
                the_file.write('# Legend: 0 = Uncategorized; 1 = Conference paper; 2 = Journal article; 3 = Preprint / Working Paper; 4 = Report; 5 = Book; 6 = Book section; 7 = Thesis; 8 = Patent\n')
                
                if 'ENTRYTYPE' in entry:
                    if 'booktitle' in entry and ('Seminar' in supetrim(entry['booktitle'])):
                        the_file.write('publication_types: ['+pubtype_dict['conference']+']\n')
                    elif 'booktitle' in entry and ('Workshop' in supetrim(entry['booktitle'])):
                        the_file.write('publication_types: ['+pubtype_dict['conference']+']\n')
                    elif 'note' in entry and ('review' in supetrim(entry['note'])):
                        the_file.write('publication_types: ['+pubtype_dict['submitted']+']\n')
                    elif 'note' in entry and ('Conditional' in supetrim(entry['note'])):
                        the_file.write('publication_types: ['+pubtype_dict['submitted']+']\n')
                    elif 'pubstate' in entry and ('preprint' in supetrim(entry['pubstate'])):
                        the_file.write('publication_types: ['+pubtype_dict['preprint']+']\n')
                    else:
                        the_file.write('publication_types: ['+pubtype_dict[entry['ENTRYTYPE']]+']\n')
                
                # Treating the publication journal, conference, etc.
                publication = 'publication: "_'
                
                ## for proceedings, it should display title, _booktitle_, ser.series, location, month, year.
                if 'booktitle' in entry:
                    publication = publication + supetrim(entry['booktitle']) + '_'
                    ## including short name for conference proceedings
                    if 'series' in entry:
                        publication = publication + ', ser. ' + supetrim(entry['series'])
                    if 'location' in entry:
                            publication = publication + ', ' + supetrim(entry['location'])
                    if monthInfoAvailable:
                        publication = publication + ', ' + pubMonth
                    # in case the publication is "accepted" or "forthcoming"
                    if 'pubstate' in entry and ('preprint' not in supetrim(entry['pubstate'])):
                        publication = publication + ', ' + supetrim(entry['pubstate'])
                    elif 'year' in entry:
                            publication = publication + ', ' + supetrim(entry['year'])
                    print(publication + '"\n')
                    the_file.write(publication + '"\n')
               
                ## for articles, it should display title, _journal_, **volumne**, (number), page_start-page_end
                elif 'journal' in entry:
                    publication = publication + supetrim(entry['journal']) + '_'
                    if 'volume' in entry:
                        publication = publication + ', **' + supetrim(entry['volume']) + '**'
                    if 'number' in entry:
                        publication = publication + ', (' + supetrim(entry['number']) + ')'
                    if 'pages' in entry:
                        publication = publication + ', ' + supetrim(entry['pages'])
                    # in case the publication is "accepted" or "forthcoming"
                    if 'pubstate' in entry and ('preprint' not in supetrim(entry['pubstate'])):
                        publication = publication + ', ' + supetrim(entry['pubstate'])
                    elif 'year' in entry:
                        publication = publication + ', ' + supetrim(entry['year'])
                    print(publication + '"\n')
                    the_file.write(publication + '"\n')
                
                elif 'school' in entry:
                    the_file.write('publication: "_'+supetrim(entry['school'])+'_"\n')
                
                elif 'institution' in entry:
                    the_file.write('publication: "_'+supetrim(entry['institution'])+'_"\n')
                else:
                    the_file.write('publication: ""\n')
                    
                                
                # I never put the short version. In the future I will use a dictionary like the authors to set the acronyms of important conferences and journals
                the_file.write('publication_short: ""\n')
                
                # Add the abstract if it's available in the bibtex
                if 'abstract' in entry:
                    the_file.write('abstract: "'+supetrim(entry['abstract'])+'"\n')
                
                # Some features are disabled. I activate them later
                the_file.write('summary: ""\n')
                
                # Treating the keywords/tags
                if 'keywords' in entry:
                    # keywords are separated by ',' instead of ';'
                    the_keywords = entry['keywords'].split(',')
                    the_file.write('tags: [')
                    keyword_str = ''
                    for keyword in the_keywords:
                        keyword_strip = supetrim(keyword)
                        keyword_str = keyword_str + '"'+ keyword_strip.lower() + '",'
                    the_file.write(keyword_str[:-1]+']\n')
                else:
                    the_file.write('tags: []\n')

                the_file.write('categories: []\n')
                
                if 'featured' in entry:
                    the_file.write('featured: true\n\n')
                else:
                    the_file.write('featured: false\n\n')

                # I add urls to the pdf and the DOI
                # disabled for now
                #the_file.write('url_pdf: "/publication/'+entry['ID']+'/manuscript.pdf"\n')
                the_file.write('url_pdf:\n')
                the_file.write('url_code:\n')
                the_file.write('url_dataset:\n')
                the_file.write('url_poster:\n')
                the_file.write('url_project:\n')
                the_file.write('url_slides:\n')
                if 'url' in entry:
                    the_file.write('url_source: ' + supetrim(entry['url']) + '\n')
                the_file.write('url_video:\n\n')
                
                # Default parameters that can be later customized
                the_file.write('image:\n')
                the_file.write('  caption: ""\n')
                the_file.write('  focal_point: ""\n')
                the_file.write('  preview_only: false\n\n')

                the_file.write('projects: []\n\n')
                the_file.write('slides: ""\n')
                
                # I keep in my bibtex file a parameter called award for publications that received an award (e.g., best paper, etc.)
                if 'award' in entry:
                    the_file.write('award: "true"\n')
                
                # I put the individual .bib entry to a file with the same name as the .md to create the CITE option
                db = BibDatabase()
                db.entries =[entry]
                writer = BibTexWriter()
                with open('publication/' + dirName + '/cite.bib', 'w', encoding='utf8') as bibfile:
                    bibfile.write(writer.write(db))

                the_file.write('---\n\n')
                
                # Any notes are copied to the main document
                if 'note' in entry:
                    strTemp = supetrim(entry['note'])
                    the_file.write(strTemp + "\n")
