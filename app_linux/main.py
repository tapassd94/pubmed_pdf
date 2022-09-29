import os
import sys
import logging as log


"""initiate the logger"""
log.basicConfig(
    filename="log.txt",
    filemode="a",
    format="%(asctime)s %(filename)s[%(levelname)s]: %(message)s",
)

log.info("Starting the script")


exit = "1"
while exit != "y":
    exit = "1"
    os.system("clear")

    print(
        """
                 _                        _ 
     _ __  _   _| |__  _ __ ___   ___  __| |
    | '_ \| | | | '_ \| '_ ` _ \ / _ \/ _` |
    | |_) | |_| | |_) | | | | | |  __/ (_| |
    | .__/ \__,_|_.__/|_| |_| |_|\___|\__,_|
    |_|                                     
    """
    )

    search = input("Enter search term: ").strip().lower()
    """if search is not None:"""
    if search == "":
        print("Please enter a search term")
        exit = input("\nDo you want to exit? (y/n):  ").strip().lower()
        if exit == "y":
            break
        else:
            continue

    max_results = input("Enter max results(pdf generated<=max results): ").strip()
    """if max_results is not a number then exit"""
    if not max_results.isnumeric():
        print('\n"{}" is not a number.\n'.format(max_results))
        exit = input("\n\nDo you want to exit? (y/n):  ").strip().lower()
        if exit == "y":
            break
        else:
            continue

    max_results = int(max_results)

    if max_results < 1:
        print("Max results must be greater than 0")
        exit = input("\n\nDo you want to exit? (y/n): ").strip().lower()
        if exit == "y":
            break
        else:
            continue

    savePdf = input("Save pdf? (y/n): ").strip().lower()
    if savePdf == "y":
        savePdf = True
    elif savePdf == "n":
        savePdf = False
    else:
        print("Input should be y or n")
        exit = input("\n\nDo you want to exit? (y/n): ").strip().lower()
        if exit == "y":
            break
        else:
            continue

    drugName = input("Enter drug name: ").strip().lower()
    if drugName == "":
        print("Please enter a drug name")
        exit = input("\n\nDo you want to exit? (y/n): ").strip().lower()
        if exit == "y":
            break
        else:
            continue

    sideEffect = input("Enter side effect: ").strip().lower()
    if sideEffect == "":
        print("Please enter a side effect")
        exit = input("\n\nDo you want to exit? (y/n): ").strip().lower()
        if exit == "y":
            break
        else:
            continue

    fileName = input("Enter file name: ").strip().lower()
    if fileName == "":
        print("Please enter a file name")
        exit = input("\n\nDo you want to exit? (y/n): ").strip().lower()
        if exit == "y":
            break
        else:
            continue
    path = input("Enter path or folder name: ").strip()
    if path == "":
        print("Please enter a path")
        exit = input("\n\nDo you want to exit? (y/n): ").strip().lower()
        if exit == "y":
            break
        else:
            continue

    """if path is contains single backslashes, then it will be converted to double backslashes"""
    if path.find("/") != -1:
        path = path.replace("/", "/")

    """if path doesnt end with backslash, then it will be added"""
    if path[-1] != "/":
        path = path + "/"

    from script import *
    from Tool import *

    pmids = script.search_pubmed_free_full_text(search, max_results * 2)
    pmcid = script.get_pmcid_from_pmid(pmids)

    if len(pmcid) < 1:
        print("No results found")
        exit = input("\n\nDo you want to exit? (y/n): ").strip().lower()
        if exit == "n":
            continue
        else:
            break

    """create a folder in path with fileName if not exists"""
    if not os.path.exists(path + fileName):
        os.makedirs(path + fileName)
    if not os.path.exists(path + fileName + "/PDF"):
        os.makedirs(path + fileName + "/PDF")
    if not os.path.exists(path + fileName + "/JSON"):
        os.makedirs(path + fileName + "/JSON")

    pmcid = script.get_abstract_from_pmcid(pmcid)
    pmcid = script.save_pdf(pmcid, path, savePdf, fileName, max_results)

    Tool.dict_to_json(pmcid, drugName, sideEffect, path, fileName, max_results)

    from scopus import *

    print("\n\nNow searching the same in SCOPUS...")
    scopus_id = scopus.search_scopus(search, max_results)
    if len(scopus_id) < 1:
        print("No results found")
        exit = input("\n\nDo you want to exit? (y/n): ").strip().lower()
        if exit == "n":
            continue
        else:
            break
    scopus_id = scopus.get_data(scopus_id)
    scopus_id = scopus.save_json_scopus(
        scopus_id, drugName, sideEffect, path, fileName, max_results
    )

    exit = input("\n\nDo you want to exit? (y/n): ").strip().lower()
    if exit == "y":
        break

log.info("Ending the script")
sys.exit()
