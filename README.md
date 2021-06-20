# Scrapper Tools used to prepare the Kannada News Dataset
This project includes various code bases used to acquire, clean, and structure the Kannada news dataset.

## Link Extractor
This component loads the website-dump from local disk, extracts and cleans all the valid HTML URLs. The extracted links are then indexed as well. 

## TODO
* Index the URLs (along with origin-page URL for reference)
* Mark if HTML is already downloaded or not
* Crawl the uncrawled URLs and save HTML
* Extract "VALID and USEFUL" Kannada Text from all the HTML pages (Avoid small texts, duplicate text snippets?) 