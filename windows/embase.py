import requests
import warnings

warnings.filterwarnings("ignore")

apikey = "432bc6112269b5a37af0dc8cadeb30ce"


from elsapy.elsclient import ElsClient
from elsapy.elsprofile import ElsAuthor, ElsAffil
from elsapy.elsdoc import FullDoc, AbsDoc
from elsapy.elssearch import ElsSearch
import json


client = ElsClient(apikey)


doc_srch = ElsSearch("star trek vs star wars", "sciencedirect")
doc_srch.execute(client, get_all=False)
print("doc_srch has", len(doc_srch.results), "results.")
