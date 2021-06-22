# Scrapper Tools used to prepare the Kannada News Dataset
This project includes various code bases used to acquire, clean, and structure the Kannada news dataset.

## Link Extractor
This component loads the website-dump from local disk, extracts and cleans all the valid HTML URLs. The extracted links are then indexed as well. 

## Entry Point
```src/link_extractor_runner.py```

## Storage
ElasticSearch is used to store the extracted URLs and the text data. Separate indexes are used for different purposes.
Generally,
* `id` field indicates the unique ID
* `source` field contains the short name of the origin news paper

For details about the indices, check `config/sys_config.yml`.

The ElasticSearch Container is configured to store the data at `ES_SAMPLE_DATA/` directory.

## easticsearch Container Setup
The elasticsearch docker container version `7.6.1` is used. More details: https://hub.docker.com/_/elasticsearch/

Start the elastic search container using
```bash
docker run -d --name elasticsearch -p 9200:9200 -p 9300:9300 -v <LOCAL DIR FULL PATH>:/usr/share/elasticsearch/data -e "discovery.type=single-node" elasticsearch:7.6.1
```
*Note:* Make sure <**LOCAL DIR FULL PATH**> is present

## TODO
[X] Index the URLs (along with origin-page URL for reference)
* Mark if HTML is already downloaded or not
* Crawl the uncrawled URLs and save HTML
* Extract "VALID and USEFUL" Kannada Text from all the HTML pages (Avoid small texts, duplicate text snippets?) 