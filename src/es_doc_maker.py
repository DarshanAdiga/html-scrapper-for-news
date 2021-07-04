"""Define the schema of various types of documents that should be stored.
If you want to know the schema of extracted information, this is the place!"""

def make_url_doc(link, downloaded=False):
   doc = {} 
   doc['id'] = link
   doc['url'] = link
   doc['downloaded'] = downloaded
   return doc

def make_article_doc(url, title, description, keywords, publish_date, article_text):
   doc = {}
   doc['id'] = url
   doc['url'] = url
   doc['title'] = title
   doc['description'] = description
   doc['keywords'] = keywords
   doc['publish_date'] = publish_date
   doc['article_text'] = article_text
   doc['text_len'] = len(article_text) # For filtering on length of article text

   return doc