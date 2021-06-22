"""Define the schema of various types of documents that should be stored.
If you want to know the schema of extracted information, this is the place!"""

def make_url_doc(link, downloaded=False):
   doc = {} 
   doc['id'] = link
   doc['url'] = link
   doc['downloaded'] = downloaded
   return doc
