"""
4.12.2020
version 1-2
-Import of another Jupyter Notebook - part D (4_data-evaluation_v1-3)
-This part includes some changes for better evaluation of listings in DataFrame and export to .csv file

3.12.2020
version 1-1

-Syntactic code polishing after import from three Jupyter Notebooks (parts A,B,C)
-Add a condition to check the existence of elements in the list with new urls (urls_list)
-Add exit() if the urls_list is empty in the end of Part A
-Removal of the same if checks from the next to parts (B,C)

-----------------------------------------------------------------------------------------------------------------------
2.12.2020
version 1-0
-Created by the integration of export of three Jupyter Notebooks (parts A,B,C)
-underlying files (1url_list_spider_v1-3, 2real-estate-scraper_v1-3, 3data-frame-processing_v1-3)

!!!
Everything is only copied from the source files without further modification
Code improvements will be available in future versions v_1-1 etc ...
!!!
"""

import pandas as pd
from bs4 import BeautifulSoup
import requests
from time import sleep
import re
from datetime import datetime

"""
--------------------------------          PART A: "Url Spider"          -------------------------------------
"""

""" I. DEFINING OF START URLS """

# Prodeje bytů (celá ČR, řazeno od nejnovější)
# start_url = "https://www.bezrealitky.cz/vypis/nabidka-prodej/byt?order=timeOrder_desc"
# Prodeje bytů Ústecký kraj okres Ústí nad Labem (řazeno od nejnovější)
usti_start_url = "https://www.bezrealitky.cz/vypis/nabidka-prodej/byt/ustecky-kraj/okres-usti-nad-labem?_token=xRxZbrzCvTQg1lC0S-mmZuJgOPvU0OrF17Vgwgs2q8Y"

""" II. OBTAINING NEW URLS """
# SETTING AN URL WHERE TO START
url = usti_start_url

# MAKING A SOUP OF URLS FROM STARTING URL
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'}
r = requests.get(url, headers=headers)
soup_inzeratu = BeautifulSoup(r.text, 'html.parser')

# MAKING A LIST TO BE FILLED WITH NEW LISTINGS URLS (SUFFIXES)
newest_listings_list = []

# USE OF DISTINGUISHING IDENTIFIER FOR NEW A LISTING URLS
# --->  class_="btn btn-shadow btn-primary btn-sm"
for link in soup_inzeratu.find_all("a", class_="btn btn-shadow btn-primary btn-sm"):
    output = str(link.get('href'))
    # print(output)
    output_processed = output[:22]
    if output_processed == "/nemovitosti-byty-domy":
        # print (output_processed)
        # print (output)
        newest_listings_list.append(output)
sleep(3.5)

# MAKING A PROPER LIST OF NEW URLS TO SCRAPE
urls_list = []
for url in newest_listings_list:
    url = "https://www.bezrealitky.cz" + url
    urls_list.append(url)

# TEST THAT NO URL HAVE GOT LOST
print("TEST ZDA SOUHLASÍ POČET:", "NEJNOVĚJŠÍCH NABÍDEK =", len(newest_listings_list), "S POČTEM VYTVOŘENÝCH URL =",
      len(urls_list))

# URLS IN THE LIST
print(urls_list)

""" III. TESTS - SEARCH FOR 404 ERROR AND INACTIVE LISTINGS """

# MAKING A CHECK LIST
urls_check_list = []

# NOT WORKING PAGES IDENTIFICATION: 404 + INACTIVE LISTINGS "Tato nabídka je neaktivní"
for url in urls_list:
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'}
    r = requests.get(url, headers=headers)
    soup_inzeratu = BeautifulSoup(r.text, 'html.parser')

    # TESTS FOR "404 PAGE ERROR" + "Tato nabídka je neaktivní" (=INACTIVE LISTING)
    not_found_page = soup_inzeratu.find("title")
    neaktivni_page = soup_inzeratu.find("strong")
    if not_found_page.text == 'Stránka nenalezena | Bezrealitky':
        urls_check_list.append("404")
        print("404")
    elif neaktivni_page.text == 'Tato nabídka je neaktivní':
        urls_check_list.append("Tato nabídka je neaktivní")
        print("Tato nabídka je neaktivní")
    else:
        urls_check_list.append("OK")
        print(url, "=OK")
    sleep(1.5)

# CREATE CHECK DICTIONARY PAIRING AN URL WITH TEST RESULT
check_dictionary = dict(zip(urls_list, urls_check_list))

# CONTINUOUS CHECK
print(check_dictionary)

""" IV. APLICATION OF RESULTS OF TESTS ON CREATED LIST OF URLS
(=> Odstranění nefunkčních url ze seznamu url)
USING: Filter a Dictionary by conditions
sOURCE: https://thispointer.com/python-filter-a-dictionary-by-conditions-on-keys-or-values/ """


# ITERATE OVER ALL THE ITEMS IN DICTIONARY 
# AND FILTER WHEN '404'+ 'Tato nabídka je neaktivní' IS FOUND
for (key, value) in check_dictionary.items():
    # Check if key is even then add pair to new dictionary
    if value == '404' or value == 'Tato nabídka je neaktivní':
        print(key)
        url_value = str(key)
        urls_list.remove(url_value)

# CONTINUOUS CHECK
print("KONTROLNÍ VÝPIS: seznam url pro scrapování má----->", len(urls_list), "položek.")
# print(urls_list)

# LOADING VISITED LISTINGS URLS DATAFRAME
C_visited_listings_urls_BEZREALITKY_df = pd.read_pickle("dataframes/C_visited_listings_urls_BEZREALITKY_df.pkl")
print(C_visited_listings_urls_BEZREALITKY_df)

""" V. TEST THAT NEW URL ISN'T AMONG ALREADY VISITED URLS """
# TRANSFORMATION OF VISITED LISTINGS URLS DATAFRAME TO A LIST
visited_urls_list = C_visited_listings_urls_BEZREALITKY_df['url'].tolist()
print(visited_urls_list)

# LISTS COMPARISON
visited_urls_to_remove = []
for new_url in urls_list:
    if (new_url in visited_urls_list):
        visited_urls_to_remove.append(new_url)
        print(new_url, "= JIŽ NAVŠTÍVENO")
print("hotovo!!!")

""" VI. APPLICATION OF RESULTS OF "VISITED URLS TEST" """
for visited_url in visited_urls_to_remove:
    urls_list.remove(visited_url)

# CONTINUOUS CHECK
print("KONTROLNÍ VÝPIS: seznam url pro scrapování má----->", len(urls_list), "položek.")
print(urls_list)

""" VII. CRUCIAL CHECK IF THE LIST OF NEW URLS TO SCRAPE IS NOT EMPTY"""
if not urls_list:
  print("NO NEW LISTINGS TO SCRAPE")
  exit()

""" VII. TRANSFORMATION OF URLS LIST TO A DATAFRAME """
A_new_urls_to_scrape_BEZREALITKY_df = pd.DataFrame(urls_list)
print(A_new_urls_to_scrape_BEZREALITKY_df)

""" VIII. EXPORT OF DATAFRAME (of urls to be scraped) """
A_new_urls_to_scrape_BEZREALITKY_df.to_pickle("dataframes/A_new_urls_to_scrape_BEZREALITKY_df.pkl")

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
"""
---------------------------------------          PART B: "Scraper"         --------------------------------------------
"""

""" I. LOADING OF URLS TO SCRAPE """
A_new_urls_to_scrape_BEZREALITKY_df = pd.read_pickle("dataframes/A_new_urls_to_scrape_BEZREALITKY_df.pkl")
print(A_new_urls_to_scrape_BEZREALITKY_df)

""" II. CONVERSION OF DATAFRAME COLUMN TO A LIST """
if not A_new_urls_to_scrape_BEZREALITKY_df.empty:
    urls_list = A_new_urls_to_scrape_BEZREALITKY_df[0].to_list()
    urls_list
else:
    print("DATAFRAME", A_new_urls_to_scrape_BEZREALITKY_df, "je prázdný")
    urls_list = []

""" III. MAKING LISTS TO BE FILLED WITH SCRAPPED DATA """

# MAKING LISTS FOR THE OFFER FEATURES DATA
ids = []
dispozice = []
plochy = []
ceny = []
poplatky = []
vratna_kauce = []
mesta = []
mestske_casti = []
typy_vlastnictvi = []
typy_budovy = []
penb = []
vybavenost = []
podlazi = []
balkony = []
terasy = []
sklepy = []
lodzie = []
parkovani = []
vytahy = []
garaze = []
k_dispozici_od = []
stari = []
provedeni = []
typ_vytapeni = []
podlazi_v_ramci_domu = []
urls = []
scraped_times = []
print("Lists created")

""" IV. DATA SCRAPING """

# LOADING URLS TO SCRAPE
for url in urls_list:
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'}
    r = requests.get(url, headers=headers)
    soup_inzeratu = BeautifulSoup(r.text, 'html.parser')

    # EXTRACTION OF ALL OFFER FEATURE CATEGORIES (steps 1-4)

    # 1. makes a list of 3 elements each containing tbody division
    offer_properties_raw = soup_inzeratu.find_all("tbody")
    # pick a second element of the listabove that contains all the offer features
    offer_properties_mixed = offer_properties_raw[0]
    # makes a list that contains all the offer features
    offer_properties_cleaned = offer_properties_mixed.find_all("td")

    # 2. MAKING A LIST CONTAINING RAW FEATURES DATA ()
    offer_properties_list = []
    for offer_property in offer_properties_cleaned:
        offer_properties_list.append(offer_property.text)

    # 3. MAKING A LIST OF FEATURE CATEGORIES
    list_of_feature_categories_raw = offer_properties_raw[0].find_all("th")
    list_of_feature_categories = []
    for category_name_raw in list_of_feature_categories_raw:
        list_of_feature_categories.append(category_name_raw.text[:-1])

    # 4. RAW FEATURES DATA CLEANING
    # INTERNET CATEGORY REMOVAL
    if list_of_feature_categories[0] == 'Internet':
        list_of_feature_categories.remove('Internet')
    # AD TEXTS REMOVAL
    for item in offer_properties_list:
        if item == "\nChci hypotéku\n\ni\n\n":
            offer_properties_list.remove("\nChci hypotéku\n\ni\n\n")
        if item == "\nZjistěte rychlost O2 internetu u vás doma.\n\n":
            offer_properties_list.remove('\nZjistěte rychlost O2 internetu u vás doma.\n\n')
        if item == 'Chci slevu na nábytek a elektro':
            offer_properties_list.remove('Chci slevu na nábytek a elektro')
        if item == 'Stěhování něco stojí. S naší půjčkou to zvládnete.':
            offer_properties_list.remove('Stěhování něco stojí. S naší půjčkou to zvládnete.')
        if item == 'Získejte družstevní byt s Buřinkou\n\ni\n\n':
            offer_properties_list.remove('Získejte družstevní byt s Buřinkou\n\ni\n\n')

    # ADD A TIMESTAMP OF THE TIME OF SCRAPING
    time_of_scraping = pd.Timestamp.now(tz=None)
    scraped_times.append(time_of_scraping)

    # FEATURES DATA DISTRIBUTION INTO OWN LISTS
    while True:
        # URL
        list_of_feature_categories.append("URL")
        offer_properties_list.append(url)
        urls.append(url)

        # ID
        x = 0
        ids.append(offer_properties_list[x])

        # DISPOZICE
        x = x + 1
        if len(offer_properties_list) <= x:
            dispozice.append("Missing_Category")
        else:
            if list_of_feature_categories[x] == "Dispozice":
                dispozice.append(offer_properties_list[x])
            else:
                dispozice.append("N/A")
                x = x - 1

        # PLOCHA
        x = x + 1
        if len(offer_properties_list) <= x:
            plochy.append("Missing_Category")
        else:
            if list_of_feature_categories[x] == "Plocha":
                plochy.append(offer_properties_list[x])
            else:
                plochy.append("N/A")
                x = x - 1

        # CENA
        x = x + 1
        if len(offer_properties_list) <= x:
            ceny.append("Missing_Category")
        else:
            if list_of_feature_categories[x] == "Cena":
                ceny.append(offer_properties_list[x])
            else:
                ceny.append("N/A")
                x = x - 1

        # POPLATKY
        x = x + 1
        if len(offer_properties_list) <= x:
            poplatky.append("Missing_Category")
        else:
            if list_of_feature_categories[x] == "Poplatky":
                poplatky.append(offer_properties_list[x])
            else:
                poplatky.append("N/A")
                x = x - 1

        # VRATNÁ KAUCE
        x = x + 1
        if len(offer_properties_list) <= x:
            vratna_kauce.append("Missing_Category")
        else:
            if list_of_feature_categories[x] == "Vratná kauce":
                vratna_kauce.append(offer_properties_list[x])
            else:
                vratna_kauce.append("N/A")
                x = x - 1

        # MĚSTO
        x = x + 1
        if len(offer_properties_list) <= x:
            mesta.append("Missing_Category")
        else:
            if list_of_feature_categories[x] == "Město":
                mesta.append(offer_properties_list[x])
            else:
                mesta.append("N/A")
                x = x - 1

        # MĚSTSKÁ ČÁST
        x = x + 1
        if len(offer_properties_list) <= x:
            mestske_casti.append("Missing_Category")
        else:
            if list_of_feature_categories[x] == "Městská část":
                mestske_casti.append(offer_properties_list[x])
            else:
                mestske_casti.append("N/A")
                x = x - 1

        # TYP VLASTNICTVÍ
        x = x + 1
        if len(offer_properties_list) <= x:
            typy_vlastnictvi.append("Missing_Category")
        else:
            if list_of_feature_categories[x] == "Typ vlastnictví":
                typy_vlastnictvi.append(offer_properties_list[x])
            else:
                typy_vlastnictvi.append("N/A")
                x = x - 1

        # TYP BUDOVY
        x = x + 1
        if len(offer_properties_list) <= x:
            typy_budovy.append("Missing_Category")
        else:
            if list_of_feature_categories[x] == "Typ budovy":
                typy_budovy.append(offer_properties_list[x])
            else:
                typy_budovy.append("N/A")
                x = x - 1

        # PENB
        x = x + 1
        if len(offer_properties_list) <= x:
            penb.append("Missing_Category")
        else:
            if list_of_feature_categories[x] == "PENB":
                penb.append(offer_properties_list[x])
            else:
                penb.append("N/A")
                x = x - 1

        # VYBAVENOST
        x = x + 1
        if len(offer_properties_list) <= x:
            vybavenost.append("Missing_Category")
        else:
            if list_of_feature_categories[x] == "Vybavenost":
                vybavenost.append(offer_properties_list[x])
            else:
                vybavenost.append("N/A")
                x = x - 1

        # PODLAŽÍ
        x = x + 1
        if len(offer_properties_list) <= x:
            podlazi.append("Missing_Category")
        else:
            if list_of_feature_categories[x] == "Podlaží":
                podlazi.append(offer_properties_list[x])
            else:
                podlazi.append("N/A")
                x = x - 1

        # BALKÓN
        x = x + 1
        if len(offer_properties_list) <= x:
            balkony.append("Missing_Category")
        else:
            if list_of_feature_categories[x] == "Balkón":
                balkony.append(offer_properties_list[x])
            else:
                balkony.append("N/A")
                x = x - 1

        # TERASA
        x = x + 1
        if len(offer_properties_list) <= x:
            terasy.append("Missing_Category")
        else:
            if list_of_feature_categories[x] == "Terasa":
                terasy.append(offer_properties_list[x])
            else:
                terasy.append("N/A")
                x = x - 1

        # SKLEP
        x = x + 1
        if len(offer_properties_list) <= x:
            sklepy.append("Missing_Category")
        else:
            if list_of_feature_categories[x] == "Sklep":
                sklepy.append(offer_properties_list[x])
            else:
                sklepy.append("N/A")
                x = x - 1

        # LODŽIE
        x = x + 1
        if len(offer_properties_list) <= x:
            lodzie.append("Missing_Category")
        else:
            if list_of_feature_categories[x] == "Lodžie":
                lodzie.append(offer_properties_list[x])
            else:
                lodzie.append("N/A")
                x = x - 1

        # PARKOVÁNÍ
        x = x + 1
        if len(offer_properties_list) <= x:
            parkovani.append("Missing_Category")
        else:
            if list_of_feature_categories[x] == "Parkování":
                parkovani.append(offer_properties_list[x])
            else:
                parkovani.append("N/A")
                x = x - 1

        # VÝTAH
        x = x + 1
        if len(offer_properties_list) <= x:
            vytahy.append("Missing_Category")
        else:
            if list_of_feature_categories[x] == "Výtah":
                vytahy.append(offer_properties_list[x])
            else:
                vytahy.append("N/A")
                x = x - 1

        # GARÁŽ
        x = x + 1
        if len(offer_properties_list) <= x:
            garaze.append("Missing_Category")
        else:
            if list_of_feature_categories[x] == "Garáž":
                garaze.append(offer_properties_list[x])
            else:
                garaze.append("N/A")
                x = x - 1

        # K DISPOZICI OD
        x = x + 1
        if len(offer_properties_list) <= x:
            k_dispozici_od.append("Missing_Category")
        else:
            if list_of_feature_categories[x] == "K dispozici od":
                k_dispozici_od.append(offer_properties_list[x])
            else:
                k_dispozici_od.append("N/A")
                x = x - 1

        # STÁŘÍ
        x = x + 1
        if len(offer_properties_list) <= x:
            stari.append("Missing_Category")
        else:
            if list_of_feature_categories[x] == "Stáří":
                stari.append(offer_properties_list[x])
            else:
                stari.append("N/A")
                x = x - 1

        # PROVEDENÍ
        x = x + 1
        if len(offer_properties_list) <= x:
            provedeni.append("Missing_Category")
        else:
            if list_of_feature_categories[x] == "Provedení":
                provedeni.append(offer_properties_list[x])
            else:
                provedeni.append("N/A")
                x = x - 1

        # TYP VYTÁPĚNÍ
        x = x + 1
        if len(offer_properties_list) <= x:
            typ_vytapeni.append("Missing_Category")
        else:
            if list_of_feature_categories[x] == "Typ vytápění":
                typ_vytapeni.append(offer_properties_list[x])
            else:
                typ_vytapeni.append("N/A")
                x = x - 1

        # PODLAŽÍ V RÁMCI DOMU
        x = x + 1
        if len(offer_properties_list) <= x:
            podlazi_v_ramci_domu.append("Missing_Category")
            break
        else:
            if list_of_feature_categories[x] == "Podlaží v rámci domu":
                podlazi_v_ramci_domu.append(offer_properties_list[x])
            else:
                podlazi_v_ramci_domu.append("N/A")
                x = x - 1
            break

    # print("Délka seznamu features pro:",url,"je:",len(offer_properties_list)) # ověření délky seznamu, zda obsahuje všech 18 položek
    print(url, "= HOTOVO")
    sleep(5)
print("CELÉ HOTOVO !!!")


""" CONTINUOUS CHECKS """

# Names of categories used in a listing (BEFORE of removal of unrequested items)
print(len(list_of_feature_categories_raw))
print(list_of_feature_categories_raw)

# Names of categories used in a listing (AFTER of removal of unrequested items)
print(len(list_of_feature_categories))
print(list_of_feature_categories)

# Listing property list
print(len(offer_properties_list))

zip_iterator = zip(list_of_feature_categories, offer_properties_list)
features_dictionary = dict(zip_iterator)
for key, value in features_dictionary.items():
    print(key, ":", value)

    list_of_lists = [
        ids,
        dispozice,
        plochy,
        ceny,
        poplatky,
        vratna_kauce,
        mesta,
        mestske_casti,
        typy_vlastnictvi,
        penb,
        vybavenost,
        podlazi,
        balkony,
        terasy,
        sklepy,
        lodzie,
        parkovani,
        vytahy,
        garaze,
        k_dispozici_od,
        stari,
        provedeni,
        typ_vytapeni,
        podlazi_v_ramci_domu,
        urls,
        scraped_times,
    ]
    for x in list_of_lists:
        print(x, sep="/n")

""" V. LIST WITH NAMES OF COLUMNS """

property_names_list = ['Číslo inzerátu',
                       'Dispozice',
                       'Plocha',
                       'Cena',
                       'Poplatky',
                       'Vratná kauce',
                       'Město',
                       'Městská část',
                       'Typ vlastnictví',
                       'Typ budovy',
                       'PENB',
                       'Vybavenost',
                       'Podlaží',
                       'Balkón',
                       'Terasa',
                       'Sklep',
                       'Lodžie',
                       'Parkování',
                       'Výtah',
                       'Garáž',
                       'K dispozici od',
                       'Stáří',
                       'Provedení',
                       'Typ vytápění',
                       'Podlaží v rámci domu',
                       'url',
                       'scraped_times'
                       ]

""" VI. MAKING A DATAFRAME OF NEWEST LISTINGS """
# WARNING: not even one list could stay empty
# => dataframe will not be created
# WARNING: not even one list could stay semi empty
# => dataframe will get messy -> very confusing


B_new_listings_BEZREALITKY_df = pd.DataFrame(
    zip(ids, dispozice, plochy, ceny, poplatky, vratna_kauce, mesta, mestske_casti, typy_vlastnictvi, typy_budovy,
        penb, vybavenost, podlazi, balkony, terasy, sklepy, lodzie, parkovani, vytahy, garaze, k_dispozici_od,
        stari, provedeni, typ_vytapeni, podlazi_v_ramci_domu, urls, scraped_times),
    columns=property_names_list)
print(B_new_listings_BEZREALITKY_df)


""" VII. LOADING OF LISTINGS WAREHOUSE DataFrame (BEZREALITKY) """
B_listings_warehouse_BEZREALITKY_df = pd.read_pickle("dataframes/B_listings_warehouse_BEZREALITKY_df.pkl")
print(B_listings_warehouse_BEZREALITKY_df)


""" VIII. MERGING OF DATAFRAMES WITH CONCAT() METHOD
==> merge of dataframes in order the new one beneath old one
source: https://pandas.pydata.org/pandas-docs/stable/user_guide/merging.html """

B_listings_warehouse_BEZREALITKY_df = pd.concat([B_listings_warehouse_BEZREALITKY_df, B_new_listings_BEZREALITKY_df])
B_listings_warehouse_BEZREALITKY_df.reset_index(drop=True, inplace=True)
print(B_listings_warehouse_BEZREALITKY_df)


""" IX. EXPORT OF UPDATED DATAFRAMES (FOR THE NEXT PROCESSING)"""

# LISTINGS WAREHOUSE DataFrame
B_listings_warehouse_BEZREALITKY_df.to_pickle("dataframes/B_listings_warehouse_BEZREALITKY_df.pkl")

# NEWEST LISTINGS Dataframe
B_new_listings_BEZREALITKY_df.to_pickle("dataframes/B_new_listings_BEZREALITKY_df.pkl")


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
"""
---------------------------------------          PART C: "Updater"         --------------------------------------------
"""

""" I. IMPORT OF DATAFRAME THAT CONTAINS NEWEST LISTINGS """

B_new_listings_BEZREALITKY_df = pd.read_pickle("dataframes/B_new_listings_BEZREALITKY_df.pkl")
print(B_new_listings_BEZREALITKY_df)


""" II. MAKING A TEMPORARY DATAFRAME OF NEW LISTINGS """

# EXTRACTION OF LISTINGS NUMBERS A RELATED URLS OF NEW LISTINGS
new_listings_comparsion_temporary_df = B_new_listings_BEZREALITKY_df[['Číslo inzerátu', 'url']]
print(new_listings_comparsion_temporary_df)


""" III. LOADING OF DATAFRAME CONTAINING ALREADY VISITED LISTINGS URLS """

C_visited_listings_urls_BEZREALITKY_df = pd.read_pickle("dataframes/C_visited_listings_urls_BEZREALITKY_df.pkl")
print(C_visited_listings_urls_BEZREALITKY_df)


""" IV. MERGING OF DATAFRAMES WITH CONCAT() METHOD 
==> merge of dataframes in order the new one beneath old one
SOURCE: https://pandas.pydata.org/pandas-docs/stable/user_guide/merging.html """

C_visited_listings_urls_BEZREALITKY_df = pd.concat(
    [C_visited_listings_urls_BEZREALITKY_df, new_listings_comparsion_temporary_df])


""" V. DATAFRAME INDEX RESET AFTER MERGING """

C_visited_listings_urls_BEZREALITKY_df.reset_index(drop=True, inplace=True)
print(C_visited_listings_urls_BEZREALITKY_df)


""" VI. EXPORT OF UPDATED "VISITED LISTINGS URLS" DATAFRAME (Bezrealitky) """

C_visited_listings_urls_BEZREALITKY_df.to_pickle("dataframes/C_visited_listings_urls_BEZREALITKY_df.pkl")

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
"""
---------------------------------------          PART D: "Evaluator"         -------------------------------------------
"""

""" I. PANDAS DATAFRAME DISPLAY SETTINGS """

# Display all numbers only on one decimal
pd.set_option('precision', 1)

# Display all values in absolute form
# (avoidance of shorten form in case of urls)
pd.set_option('display.max_colwidth', None)


""" II. A bit of data cleaning """

B_listings_warehouse_BEZREALITKY_EV_df = pd.read_pickle("dataframes/B_listings_warehouse_BEZREALITKY_df.pkl")

# Area column data cleaning (removal of m2 suffix) + datatype change to integer
B_listings_warehouse_BEZREALITKY_EV_df['Plocha'] = B_listings_warehouse_BEZREALITKY_EV_df['Plocha'].map(lambda x: str(x)[:-3]).astype(int).values

# Price column data cleaning (removal of Kč suffix) + datatype change to integer
B_listings_warehouse_BEZREALITKY_EV_df['Cena'] = B_listings_warehouse_BEZREALITKY_EV_df['Cena'].map(lambda x: str(x)[:-3]).str.replace('.', '').astype(int).values


""" III. Add new column price per square meter """

# Making a new column "CenaZaMetr" (PricePerSquareMeter)
B_listings_warehouse_BEZREALITKY_EV_df = B_listings_warehouse_BEZREALITKY_EV_df.assign(
    CenaZaMetr=B_listings_warehouse_BEZREALITKY_EV_df['Cena'] / B_listings_warehouse_BEZREALITKY_EV_df['Plocha'])

B_listings_warehouse_BEZREALITKY_EV_df.sort_values(by=['CenaZaMetr'])


""" IV. Export into .csv file """

# Export to .csv file for further (manual) processing
B_listings_warehouse_BEZREALITKY_EV_df.to_csv(r'B_listings_warehouse_BEZREALITKY_EV.csv', index=False, encoding='utf-8-sig')
