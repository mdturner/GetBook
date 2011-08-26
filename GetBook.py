# This script generates ePub files from the books made 
# available by the Neal A. Maxwell Institute for 
# Religious Scholarship at Brigham Young University 
# (http://maxwellinstitute.byu.edu/).
# Run the script by passing the bookid from the book's url as an argument
# e.g. for _Temple and the Cosmos_ 
# (http://maxwellinstitute.byu.edu/publications/books/?bookid=103), 
# use the command'python GetBook.py 103'

# Script created by Matt Turner (http://guavaduck.com/)

import urllib
import re
import os
import zipfile
import glob
import shutil
import sys
import tidy
import codecs 
import platform

class URLopener(urllib.FancyURLopener):
    version = 'GetBook.py/0.1 '+platform.platform()+' (+http://guavaduck.com/)'
urlopener=URLopener()

print '--'
print 'Maxwell Institute Book to ePub Converter'
print 'by Matt Turner (http://guavaduck.com/)'
print '--'
print ''

if len(sys.argv)>1:
    book_id=sys.argv[1]
else:
    book_id=raw_input('Book id? ')

book_url='http://maxwellinstitute.byu.edu/publications/books/?bookid='+book_id

f=urlopener.open(book_url)
#f=open('sample_book.html')
s=f.read()

#book_title=re.search('(?<=<META NAME="title" CONTENT=").+?(?=">)',s).group(0)
book_header=re.search('(?<=<title>).+?(?=</title>)',s).group(0)
book_title=re.search('^.+(?= by )',book_header).group(0)
book_author=re.search('(?<='+book_title+' by ).+$',book_header)
#book_author=re.search('(?<=<META NAME="author" CONTENT=").+?(?=">)',s)
if book_author:
    book_author=book_author.group(0)
else:
    book_author="Unknown"

#book_author=re.search('(?<=<META NAME="author" CONTENT=").+?(?=">)',s).group(0)
#book_id=re.search('(?<=<META NAME="bookid" CONTENT=")[0-9]+(?=">)',s).group(0)

print 'Retrieving _'+book_title+'_ by '+book_author

chapters=re.findall('(?<=\?bookid='+book_id+'&chapid=)[0-9]+(?=">)',s)

n_chapters=len(chapters)
chapter_titles=['']*n_chapters
chapter_texts=['']*n_chapters

tidy_options = dict(output_xhtml=1, add_xml_decl=1, indent=1, tidy_mark=0, char_encoding='utf8')
#tidy_options = dict(output_xhtml=1, add_xml_decl=1, indent=1, tidy_mark=0)

def chapterlink(matchobj):
    return 'chapter'+str(chapters.index(re.sub('http.+=','',matchobj.group(0))))+'.xhtml'

for n in range(n_chapters):
#for n in range(1):
    print 'Retrieving chapter '+str(n+1)+' of '+str(n_chapters)
    chapter_url=book_url+'&chapid='+chapters[n]
    f=urlopener.open(chapter_url)
#    f=open('sample_chapter.html')
    s_chapter=unicode(f.read(),'utf8','ignore')
#    chapter_titles[n]=re.search('(?<=<META NAME="title" CONTENT=").+?(?=">)',s_chapter).group(0)
    chapter_titles[n]=re.search('(?<=<title>'+book_title+' - ).+?(?=</title>)',s_chapter).group(0)
    chapter_text=re.findall("<div id='content_readable'>[\s\S]*?(?=</div>)",s_chapter)[0]
    chapter_text=re.sub('http.+?chapid=([0-9]+)',chapterlink,chapter_text)
    chapter_texts[n]=re.sub('\n','\n\t\t',chapter_text)
    f.close()
    try:
        print '    '+chapter_titles[n]
    except:
        print '    '+chapter_titles[n].encode('ascii', 'replace')
    
book_path=re.sub('[^a-zA-Z0-9\-_.() ]',' ',book_title)+'.'+book_id
book_path0=book_path+''
n_path=0

while os.path.exists(book_path) or os.path.exists(book_path+'.epub'):
    n_path+=1
    book_path=book_path0+'.'+str(n_path)

os.mkdir(book_path)

os.chdir(book_path)

f=open('mimetype','w')
f.write('application/epub+zip')
f.close()

os.mkdir('META-INF')
os.chdir('META-INF')
f=open('container.xml','w')
f.write('''<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>''')
f.close()
os.chdir('..')

os.mkdir('OEBPS')
os.chdir('OEBPS')
f=codecs.open('content.opf','w','utf-8')
f.write('''<?xml version="1.0"?>
<package version="2.0" xmlns="http://www.idpf.org/2007/opf"
         unique-identifier="BookId">
 <metadata xmlns:dc="http://purl.org/dc/elements/1.1/"
           xmlns:opf="http://www.idpf.org/2007/opf">
   <dc:title>'''+book_title+'''</dc:title> 
   <dc:creator opf:role="aut">'''+book_author+'''</dc:creator>
   <dc:language>en-US</dc:language> 
   <dc:identifier id="BookId">urn:uuid:'''+book_url+'''</dc:identifier>
 </metadata>
 <manifest>
  <item id="ncx" href="toc.ncx" media-type="text/xml" />
  <item id="title" href="title.xhtml" media-type="application/xhtml+xml"/>''')

for n in range(n_chapters):
    f.write('''
  <item id="chapter'''+str(n)+'''" href="chapter'''+str(n)+'''.xhtml" media-type="application/xhtml+xml"/>''')
  
f.write('''
 </manifest>
 <spine toc="ncx">
  <itemref idref="title"/>''')
 
for n in range(n_chapters):
    f.write('''
  <itemref idref="chapter'''+str(n)+'''"/>''')

f.write('''
 </spine>
</package>''')
f.close()

f=codecs.open('toc.ncx', 'w', 'utf-8')
f.write('''<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="'''+book_url+'''"/>
    <meta name="dtb:depth" content="1"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNumber" content="0"/>
  </head>
  <docTitle>
    <text>'''+book_title+'''</text>
  </docTitle>
  <navMap>
    <navPoint id="title" playOrder="1">
      <navLabel>
        <text>Title Page</text>
      </navLabel>
      <content src="title.xhtml"/>
    </navPoint>''')
for n in range(n_chapters):
    f.write('''
    <navPoint id="chapter'''+str(n)+'''" playOrder="'''+str(n+2)+'''">
      <navLabel>
        <text>'''+chapter_titles[n]+'''</text>
      </navLabel>
      <content src="chapter'''+str(n)+'''.xhtml"/>
    </navPoint>''')
f.write('''
  </navMap>
</ncx>''')

f=codecs.open('title.xhtml','w','utf-8')
f.write(str(tidy.parseString('<html>\n\t<head>\n\t\t<title>'+book_title+'</title>\n\t</head>\n\t<body>\n\t\t<center><h1>'+book_title+'</h1>\n\t\t<h2>by '+book_author+'</h2></center>\n\t</body>\n</html>', **tidy_options)))
f.close()

for n in range(n_chapters):
    f=open('chapter'+str(n)+'.xhtml','w')
    f.write(str(tidy.parseString(('<html>\n\t<head>\n\t\t<title>'+chapter_titles[n]+'</title>\n\t</head>\n\t<body>\n\t\t<center><h1>'+chapter_titles[n]+'''</h1></center>\n\t\t'''+chapter_texts[n]+'\n\t</body>\n</html>').encode('utf-8'), **tidy_options)))
    f.close()

os.chdir('../..')

file = zipfile.ZipFile(book_path+'.epub', "w")
os.chdir(book_path)
file.write('mimetype','mimetype',zipfile.ZIP_STORED)
file.write('META-INF/container.xml','META-INF/container.xml',zipfile.ZIP_DEFLATED)
#file.write('META-INF/container.xml','META-INF/container.xml',zipfile.ZIP_STORED)
for name in glob.glob("OEBPS/*"):
    file.write(name,name,zipfile.ZIP_DEFLATED)
#    file.write(name,name,zipfile.ZIP_STORED)
file.close()

os.chdir('..')
shutil.rmtree(book_path)
