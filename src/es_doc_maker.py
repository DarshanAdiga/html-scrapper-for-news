"""Define the schema of various types of documents that should be stored.
If you want to know the schema of extracted information, this is the place!"""

def make_extracted_url_doc(link):
   doc = {} 
   doc['id'] = link
   doc['url'] = link
   return doc

def make_html_path_doc(path):
   doc = {} 
   doc['id'] = path
   doc['path'] = path
   return doc
