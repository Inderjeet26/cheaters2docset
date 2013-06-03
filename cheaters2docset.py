import sqlite3 as lite
import glob
import os
import subprocess
import BeautifulSoup

# import tidylib
# import urllib

###################################
# CUSTOMIZE THIS PATH : POINT IT TO 
# THE DIRECTORY CONTAINING cheaters

cheaters_path = '../cheaters/' # accepts relative path

#
#
###################################                 
doc_path =  os.path.dirname(os.path.abspath(__file__))+'/cheaters2docset.docset/Contents/Resources/Documents/'
db_path  =  os.path.dirname(os.path.abspath(__file__))+'/cheaters2docset.docset/Contents/Resources/docSet.dsidx'

head ='<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1"><title>Cheat Sheets</title><meta name="viewport" content="width=device-width, initial-scale=1.0"><link rel="stylesheet" href="css/cheaters.css"></head><body class="normal">'
foot ='<script src="js/jquery-1.7.1.min.js" type="text/javascript" charset="utf-8"></script><script type="text/javascript" src="js/cheaters.js"></script></body></html>'

# create an index from the github README.md - requires multimarkdown installed!
b = os.system('multimarkdown '+cheaters_path+'README.md > '+doc_path+'index.html')

#copy the CSS and javascript
b = os.system('cp -R '+cheaters_path+'css/ '+doc_path+'css/')
b = os.system('cp -R '+cheaters_path+'javascripts/ '+doc_path+'javascripts/')

# file length using subprocess and `wc -l`
def file_len(fname):
    p = subprocess.Popen(['wc', '-l', fname], stdout=subprocess.PIPE, 
                                              stderr=subprocess.PIPE)
    result, err = p.communicate()
    if p.returncode != 0:
        raise IOError(err)
    return int(result.strip().split()[0])

# html in cheaters directory listed
filelist = glob.glob(cheaters_path+'cheatsheets/*.html')

#connect to the sqlite db
con = lite.connect(db_path)
cur = con.cursor()    
#erase all
cur.execute('DELETE FROM searchIndex')

#insert the file in the filelist and beautify the html file
for file in filelist:
    if file_len(file) > 10 :
        filename_ext = os.path.basename(file)
        filename=os.path.splitext(filename_ext)[0]
        soup = BeautifulSoup.BeautifulSoup(open(file))
        #re-write the html prettifyied file
        f = open(doc_path+filename_ext, "w")
        f.write(head)
        f.write(soup.prettify())
        f.write(foot)
        f.close()
        cur.execute("INSERT INTO searchIndex (path,type,name) VALUES (?,'func',?)",(filename_ext,filename))
        print 'written > '+filename


# Markdown files in local cheatsheets/ directory
filelist_local = glob.glob(os.path.dirname(os.path.abspath(__file__))+'/cheatsheets/*.md')

#insert the file in the filelist and beautify the html file
for file in filelist_local:
    filename_ext = os.path.basename(file)
    filename=os.path.splitext(filename_ext)[0]
    b = os.system('multimarkdown '+file+' > '+doc_path+filename+'.html')
    cur.execute("INSERT INTO searchIndex (path,type,name) VALUES (?,'func',?)",(filename+'.html',filename))
    print 'converted MD file > '+filename

#commit the DB changes
con.commit()
#close the DB
con.close()
