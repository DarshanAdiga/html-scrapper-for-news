# Scrapper Tools used to prepare the Kannada News Dataset
This project includes various code bases used to acquire, clean, and structure the Kannada news dataset. 

## Preprocessing
The `src/util/` folder includes various cleanup scripts to be run on the website dump, before running the extractors.
1. To fix the directories with name ending with `.html` and contains `index.html` inside it, use `src/util/move_html_directory_to_file.py`

## Task 1: Link Extractor
This component loads the website-dump from local disk, extracts and cleans all the valid HTML URLs. The extracted links are then indexed as well.
### Entry Point
```python3 src/link_extractor_runner.py```

## Task 2: Article Extractor
This component loads the valid HTML pages from the local disk, extracts the article information.
Article document includes article text, publish date, title, description and keywords. The articles are saved on the configured storage.

This component first filters out the URLs present in the seed-url index whose HTML is available, and whose the article has not been extracted. Only such urls will be considered for the extraction.
### Entry Point
``` python3 src/article_extractor.py```

## Task 3: Save to File
Fetch the data from article-index and save to a JL file on local system.
### Entry Point
```python3 src/get_index_dump.py```


## Storage
ElasticSearch is used to store the extracted URLs and the text data. Separate indexes are used for different purposes.
Generally,
* `id` field indicates the unique ID
* `source` field contains the short name of the origin news paper

For details about the indices, check `config/sys_config.yml`.

The ElasticSearch Container is configured to store the data at `ES_SAMPLE_DATA/` directory.

### easticsearch Container Setup
The elasticsearch docker container version `7.6.1` is used. More details: https://hub.docker.com/_/elasticsearch/

Start the elastic search container using
```bash
docker run -d --name elasticsearch -p 9200:9200 -p 9300:9300 -v <LOCAL DIR FULL PATH>:/usr/share/elasticsearch/data -e "discovery.type=single-node" elasticsearch:7.6.1
```
*Note:* Make sure <**LOCAL DIR FULL PATH**> is present

## TODO
[X] Index the URLs (along with origin-page URL for reference)
[X] Fix common issues in article-extraction
  [ ] Space in the html file paths! During extraction:
      Ex: "cricket/rishabh-pant-surpasses-ms dhoni-creates-another-record/330223.html"
[X] Avoid small texts, duplicate text snippets
* Crawl the uncrawled URLs and save HTML