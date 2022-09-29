import json
import re
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
from collections import defaultdict
import logging as log


"""initiate logger"""
"""initiate the logger"""
log.basicConfig(
    filename="log.txt",
    filemode="a",
    format="%(asctime)s %(filename)s[%(levelname)s]: %(message)s",
)


class Tool:
    def clean_text(self, text):
        """
        text: text to be cleaned
        return: cleaned text
        """

        """remove text after Acknowledgement and abbreviations"""
        text = text.split("Acknowledgments")[0]
        text = text.split("Abbreviations")[0]
        text = text.split("Figure Legend")[0]
        text = text.split("Supplementary Information")[0]
        text = text.split("Funding")[0]
        text = text.split("References")[0]

        """if Acknowledgments is not found then log it"""
        if "Acknowledgments" not in text:
            log.warning("Acknowledgments not found")
        else:
            log.info("Acknowledgments found")

        if "Abbreviations" not in text:
            log.warning("Abbreviations not found")
        else:
            log.info("Abbreviations found")

        if "Supplementary Information" not in text:
            log.warning("Supplementary Information not found")
        else:
            log.info("Supplementary Information found")

        if "Funding" not in text:
            log.warning("Funding not found")
        else:
            log.info("Funding found")

        if "References" not in text:
            log.warning("References not found")
        else:
            log.info("References found")

        if "Figure Legend" not in text:
            log.warning("Figure Legend not found")
        else:
            log.info("Figure Legend found")

        """remove extra spaces"""
        text = re.sub(" +", " ", text)

        """join hyphen words"""
        text = re.sub("-\s+", "", text)
        text = re.sub("\s+-", "", text)

        """replace \n with space"""
        text = re.sub("\n", " ", text)
        text = re.sub("\r", " ", text)
        text = re.sub("\t", " ", text)
        text = re.sub("\f", " ", text)

        """deliminate from fullstop"""
        text = re.split(r"\. (?=[A-Z])", text)

        """remove text in brackets"""
        text = [re.sub(r"\[.*?\]", "", t) for t in text]
        text = [re.sub(r"\(.*?\)", "", t) for t in text]
        text = [re.sub(r"\{.*?\}", "", t) for t in text]

        """remove extra spaces"""
        text = [re.sub(" +", " ", t) for t in text]

        """remove links and emails"""
        text = [re.sub(r"http\S+", "", t) for t in text]
        text = [re.sub(r"\S+@\S+", "", t) for t in text]

        """remove lines with less than 5 words"""
        text = [t for t in text if len(t.split()) > 5]

        '''remove line if it contains "page  of "'''
        pat = r"\d of"
        text = [t for t in text if re.search(pat, t) is None]

        """remove extra spaces"""
        text = [re.sub(" +", " ", t) for t in text]

        return text

    def convert_pdf_to_txt(self, path):
        """
        path: path to the pdf file
        return: cleaned tokenized text in the pdf file
        """

        rsrcmgr = PDFResourceManager()
        retstr = StringIO()
        codec = "utf-8"
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, laparams=laparams)
        """if file cannot be opened, log it"""
        try:
            fp = open(path, "rb")
        except FileNotFoundError:
            log.error("File not found, path is:" + path)
            return ""
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        password = ""
        maxpages = 0
        caching = True
        pagenos = set()

        for page in PDFPage.get_pages(
            fp,
            pagenos,
            maxpages=maxpages,
            password=password,
            caching=caching,
            check_extractable=True,
        ):
            interpreter.process_page(page)

        text = retstr.getvalue()
        """if text is empty then log it"""
        if text == "":
            log.error("Text is empty, path is:" + path)
            return ""

        fp.close()
        device.close()
        retstr.close()
        return self.clean_text(text)

    def dict_to_json(dictionary, fname, sname, path, filename, max_result):
        """
        dictionary: dictionary to be converted
        fname: file name
        sname: sheet name
        """

        dictionary_ = {
            "drugName": fname,
            "sideEffectList": [{"sideEffect": sname, "articleList": []}],
        }

        arr = []
        count = 0
        for k, v in dictionary.items():
            if count > max_result:
                break
            dic = defaultdict()
            dic["PMCID"] = k
            for k, v in v.items():
                dic[k] = v
            arr.append(dic)
            count += 1

        dictionary_["sideEffectList"][0]["articleList"] = arr

        with open(path + filename + "/JSON/" + filename + "_PUBMED.json", "w") as fp:
            json.dump(dictionary_, fp)

        print("JSON saved in", path + filename + "/JSON/")
