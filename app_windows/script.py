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


class script:
    def search_pubmed_free_full_text(term, max_results=10**9):
        """
        term: search term
        max_results: maximum number of results to return
        return: list of pubmed ids(PMID)
        """

        print("\nStarting the search for {}".format(term))
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {
            "db": "pubmed",
            "retmode": "json",
            "retmax": max_results,
            "term": term,
        }
        response = requests.get(url, params=params)
        data = json.loads(response.text)
        print("Found {} results".format(data["esearchresult"]["count"]))
        return data["esearchresult"]["idlist"]

    def get_pmcid_from_pmid(ids):
        """
        ids: list of pubmed ids(PMID)
        return: dictionary with index as PMCID and values with PMID, DOI
        """

        pmcid_pmid = defaultdict(dict)

        print()
        bar = spin("Converting PMID to PMCID")

        tool = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for id in ids:
            url = (
                "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool="
                + tool
                + "&email="
                + tool
                + "@gmail.com&ids="
            )
            url += id + "&format=json"
            response = requests.get(url)

            """if response gives and error then add it to log and continue"""
            if response.status_code != 200:
                log.warning("PMID: {}".format(id))
                continue

            xml = response.json()

            if "pmcid" in xml["records"][0].keys():
                pmcid_pmid[xml["records"][0]["pmcid"]]["PMID"] = id
                if "doi" in xml["records"][0].keys():
                    pmcid_pmid[xml["records"][0]["pmcid"]]["DOI"] = xml["records"][0][
                        "doi"
                    ]
                else:
                    pmcid_pmid[xml["records"][0]["pmcid"]]["DOI"] = ""
                bar.next()

        bar.finish()
        return pmcid_pmid

    def get_abstract_from_pmcid(ids):
        """
        ids: list of pubmed ids(PMID)
        return: dictionary with index as PMCID
                and values with PMID, DOI, abstract, author name
                title and date
        """

        pmcid_pmid = ids

        print()
        bar = Bar("Retrieving Abstracts", max=len(ids))

        tool = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for pmcid in ids.keys():
            url = (
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id="
                + ids[pmcid]["PMID"]
                + "&retmode=xml"
            )
            response = requests.get(url)
            xml = response.text
            soup = BeautifulSoup(xml, features="xml")

            if soup.find("ArticleTitle") is None:
                ids[pmcid]["paperTitle"] = ""
                log.warning(
                    "PMCID: {} has no article title mentioned in xml".format(pmcid)
                )
            else:
                title = soup.find("ArticleTitle").text
                ids[pmcid]["paperTitle"] = title

            if soup.find("AbstractText") is None:
                ids[pmcid]["abstract"] = [""]
                log.warning("PMCID: {} has no abstract mentioned in xml".format(pmcid))
            else:
                abstract = soup.find("AbstractText").text
                ids[pmcid]["abstract"] = Tool.clean_text(text=abstract)

            authors = soup.find_all("Author")
            if authors is not None:
                authors_list = []
                for author in authors:
                    if (
                        author.find("ForeName") is not None
                        and author.find("LastName") is not None
                    ):
                        authors_list.append(
                            author.find("ForeName").text
                            + " "
                            + author.find("LastName").text
                        )
                ids[pmcid]["authorNames"] = authors_list
            else:
                ids[pmcid]["authorNames"] = ""
                log.warning("PMCID: {} has no authors mentioned in xml".format(pmcid))

            date = soup.find_all("ArticleDate")
            date_list = []
            for d in date:
                date_list.append(
                    d.find("Day").text
                    + "-"
                    + d.find("Month").text
                    + "-"
                    + d.find("Year").text
                )

            if len(date_list) > 0:
                ids[pmcid]["date"] = date_list[0]
            else:
                ids[pmcid]["date"] = ""
                log.warning("PMCID: {} has no date mentioned in xml".format(pmcid))

            if len(soup.find_all("citation")) > 0:
                ids[pmcid]["citation_length"] = str(len(soup.find_all("citation")))
                ref = soup.find_all("reference")
                cit = defaultdict()
                for r in ref:
                    cit[r.find("articleid").text] = r.find("citation").text
            else:
                ids[pmcid]["citation_length"] = ""
                ids[pmcid]["citation"] = ""
                log.warning("PMCID: {} has no citation mentioned in xml".format(pmcid))

            bar.next()

        bar.finish()
        print(
            "Added article title, author names, date of journal, citation and its length and abstract to all PMCIDs"
        )
        return pmcid_pmid

    def save_pdf(ids, path, savePdf=False, fname=".\\", max_result=1):

        pmcid_pmid = ids

        count = 0
        timer = 5
        print()
        bar = Bar("Saving PDF's + extracting text", max=len(ids))
        for pmc in ids.keys():
            if count > max_result:
                break

            """if pdf already exists, skip"""
            if os.path.isfile(path + pmc + ".pdf"):
                nothing = 1
                log.info(
                    "PDF already exists for PMCID: {}, skipping the download and using the existing pdf".format(
                        pmc
                    )
                )
            else:
                """save pdf from base_url"""

                base_url = "https://www.ncbi.nlm.nih.gov/labs/pmc/articles/"
                url = base_url + pmc + "/pdf/"
                try:
                    response = requests.get(url)
                    x = urllib.request.urlopen(response.url)
                except urllib.error.HTTPError as e:
                    log.error("HTTPError: {}".format(e))
                    if e.code in (..., 403, 502, ...):
                        continue
                    if e.code in (..., 429, ...):
                        print(
                            "Server will not respond. Retrying after", timer, "seconds"
                        )
                        log.warning(
                            "Too many requests, sleeping for {} seconds".format(timer)
                        )
                        time.sleep(timer)

                urllib.request.urlretrieve(
                    response.url, path + fname + "\\PDF\\" + pmc + ".pdf"
                )

            text = Tool.convert_pdf_to_txt(path + fname + "\\PDF\\" + pmc + ".pdf")

            pmcid_pmid[pmc]["sitelink"] = (
                "https://www.ncbi.nlm.nih.gov/labs/pmc/articles/" + pmc + "/pdf/"
            )
            pmcid_pmid[pmc]["textList"] = text

            pmcid_pmid[pmc]["textList"] = (
                pmcid_pmid[pmc]["abstract"] + pmcid_pmid[pmc]["textList"]
            )

            if savePdf == False:
                """delete pdf"""
                if os.path.isfile(path + fname + "\\PDF\\" + pmc + ".pdf") == False:
                    log.error("PDF not found for PMCID: {}".format(pmc))
                else:
                    os.remove(path + fname + "\\PDF\\" + pmc + ".pdf")

            timer += timer
            count += 1

            bar.next()

        bar.finish()

        if savePdf == False:
            print("PDF's deleted")
        else:
            print("PDF's saved in", path + fname + "\\PDF\\")
        return pmcid_pmid
