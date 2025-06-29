import datetime
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import datetime
import pprint as pp
import math

def scraping_ao(url = "https://www.boamp.fr/pages/entreprise-accueil/", today = datetime.date.today().strftime("%d/%m/%Y")) -> list:
    """Fonction qui scrape les appels d'offres et renvoie une liste avec le texte

    Args:
        url (str, optional): URL de base de l'appel du site d'appel d'offre. Defaults to "https://www.boamp.fr/pages/entreprise-accueil/".
        today (_type_, optional): Date. Defaults to datetime.date.today().strftime("%d/%m/%Y").

    Returns:
        list: Liste de textes des appels d'offres
    """
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.binary_location ="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)

    #recherche des AO aujourd'hui
    time.sleep(3)
    driver.find_element(By.XPATH, './/a[@class="fr-btn"]').click()
    time.sleep(3)
    driver.find_element(By.XPATH, './/button[@class="fr-accordion__btn ng-binding"]').click()
    time.sleep(5)
    driver.find_element(By.XPATH, './/div[@class="odswidget-timerange__from"]/input').send_keys(today)
    time.sleep(3)
    driver.find_element(By.XPATH, './/div[@class="odswidget-timerange__to"]/input').send_keys(today)
    time.sleep(5)
    driver.find_element(By.XPATH, './/a[@class="fr-btn"]').click()
    time.sleep(3)


    #nb pages :
    nb_pages = math.ceil(int(driver.find_element(By.XPATH, './/p[@class="fr-m-0 fr-text--lg ng-scope"]').text[:-31])/10)


    j=5
    liens=[]
    #liste de liens d'appels d'offres
    for i in range (1, nb_pages+1):
        if i > 6 and i != nb_pages-5:
            # print(i)
            driver.find_element(By.XPATH, './/div[@class="fr-container no-print"]/nav/ul/li[6]').click()
            time.sleep(5)
            liens.extend([lien.get_attribute('href') for lien in driver.find_elements(By.XPATH, './/a[@class="fr-btn fr-my-1w ng-binding"]')])
        elif i == nb_pages-5:
            # print(i)
            j = j + 1
            driver.find_element(By.XPATH, './/div[@class="fr-container no-print"]/nav/ul/li[' + str(j) + ']').click()
            time.sleep(5)
            liens.extend([lien.get_attribute('href') for lien in driver.find_elements(By.XPATH, './/a[@class="fr-btn fr-my-1w ng-binding"]')])
        else:
            # print(i)
            driver.find_element(By.XPATH, './/div[@class="fr-container no-print"]/nav/ul/li[' + str(i) + ']').click()
            time.sleep(10)
            liens.extend([lien.get_attribute('href') for lien in driver.find_elements(By.XPATH, './/a[@class="fr-btn fr-my-1w ng-binding"]')]) # les liens


    AO = []
    #AO liste = texte "clean" des X appels d'offres
    for lien in liens:
        driver.get(lien)
        time.sleep(5)
        driver.find_element(By.XPATH, './/button[@class="fr-btn fr-my-1w ng-binding"]').click()
        time.sleep(10)
        text_ao = driver.find_element(By.XPATH, './/div[@class="ng-scope"]').text
        AO.append(text_ao[text_ao.find("Avis n°"):text_ao.find("Date d'envoi du présent avis à la publication")])
        with open ('AO.log', 'a') as f:
            f.write("Appel d'offre : " + lien + " traité\n")
    driver.quit()
    return AO


print(scraping_ao())

