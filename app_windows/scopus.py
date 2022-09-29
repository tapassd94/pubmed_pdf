import requests
import json
import datetime
from progress.bar import IncrementalBar as Bar
from progress.spinner import Spinner as spin
from collections import defaultdict
from bs4 import BeautifulSoup
import urllib.request
import os
import time
import logging as log

"""import class tool from tool.py in same folder"""
from Tool import *

Tool = Tool()


"""initiate the logger"""
log.basicConfig(
    filename="log.txt",
    filemode="a",
    format="%(asctime)s %(filename)s[%(levelname)s]: %(message)s",
)


class scopus:
    def search_scopus(term, max_result=10**9):
        """
        term: search term
        max_result: maximum number of results to return
        return: list of scopus ids(SID)
        """

        print("\nStarting the search for {}".format(term))
        url = "https://api.elsevier.com/content/search/scopus"
        params = {
            "query": term,
            "apiKey": "432bc6112269b5a37af0dc8cadeb30ce",
            "httpAccept": "application/json",
            "count": max_result,
        }
        response = requests.get(url, params=params)
        data = json.loads(response.text)
        print(
            "Found {} results".format(data["search-results"]["opensearch:totalResults"])
        )

        print("Storing only the first", max_result, "results")

        return data["search-results"]["entry"]

    def get_data(data):
        """
        data: list of scopus ids(SID)
        return: list of data from scopus
        """
        scopus = defaultdict(dict)
        print("\nStarting the data extraction")
        bar = Bar("Processing", max=len(data))
        for i in range(len(data)):
            eid = data[i]["eid"]
            if "pubmed-id" in data[i]:
                scopus[eid]["PMID"] = data[i]["pubmed-id"]
            else:
                scopus[eid]["PMID"] = ""
            if "prism:doi" in data[i]:
                scopus[eid]["DOI"] = data[i]["prism:doi"]
            else:
                scopus[eid]["DOI"] = ""
            if "dc:title" in data[i]:
                scopus[eid]["paperTitle"] = data[i]["dc:title"]
            else:
                scopus[eid]["paperTitle"] = ""

            scopus[eid]["abstract"] = []  # data[i]["dc:description"]
            scopus[eid]["authorNames"] = ""  # data[i]["author"][0]["ce:indexed-name"]

            if "prism:coverDate" in data[i]:
                scopus[eid]["date"] = data[i]["prism:coverDate"]
            else:
                scopus[eid]["date"] = ""

            if "citedby-count" in data[i]:
                scopus[eid]["citation_length"] = data[i]["citedby-count"]
            else:
                scopus[eid]["citation_length"] = ""

            scopus[eid]["citation_list"] = []
            scopus[eid]["textList"] = []
            bar.next()

        return scopus

    def save_json_scopus(scopus_id, drugName, sideEffect, path, fileName, max_results):
        """
        scopus: list of data from scopus
        return: None
        """
        dictionary_ = {
            "drugName": drugName,
            "sideEffectList": [{"sideEffect": sideEffect, "articleList": []}],
        }

        dictionary_["sideEffectList"][0]["articleList"] = scopus_id

        with open(path + fileName + "\\JSON\\" + fileName + "_SCOPUS.json", "w") as f:
            json.dump(dictionary_, f)
