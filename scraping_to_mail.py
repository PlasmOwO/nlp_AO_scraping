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
from huggingface_hub import whoami
from transformers import pipeline
import numpy
import smtplib, ssl
from dotenv import load_dotenv
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


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
    return AO,liens



def text_to_llm(ao : str) -> dict :
    """Utilise plsuieurs LLM pour classifier, résumer et scorer un appel d'offre

    Args:
        ao (str): Le text d'un appel d'offre

    Returns:
        dict: Les résultats de LLm
    """
    def classifier_appel_offre(prompt_appel_offre : str, model_name : str = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli") : 
        classifier = pipeline("zero-shot-classification", model=model_name)
        candidate_labels = ["Médical", "Génie civil", "Travaux", "Service", "Fourniture"]
        output = classifier(prompt_appel_offre, candidate_labels, multi_label=False)
        return {"Labels" : output['labels'], 
                "Scores" : output['scores']
            }
    def resumer_appel_offre(prompt_appel_offre : str, model_name : str = "plguillou/t5-base-fr-sum-cnndm") :
        summarizer = pipeline("summarization", model=model_name)

        resume = summarizer(prompt_appel_offre, max_length=60, min_length=10, do_sample=False)
        return (resume[0]['summary_text'])
    def scoring_question(summary_prompt : str, model_name : str = "etalab-ia/camembert-base-squadFR-fquad-piaf"):
        nlp = pipeline('question-answering', model=model_name, tokenizer='etalab-ia/camembert-base-squadFR-fquad-piaf')
        return nlp({
            'question': "Dans quelle catégorie se situe l'appel d'offre ?",
            'context': summary_prompt
        })
    
    classes = classifier_appel_offre(ao)
    summary = resumer_appel_offre(ao)
    score = scoring_question(summary)


    return {
        "Classes" : classes,
        "Summary" : summary,
        "Score" : score
    }


def send_alerting_mail(type_appel_offre : str, summary : str, url : str, scoring : dict):
    """Altering par mail en cas de nouvel appel d'offre

    Args:
        type appel offre (str): La classficiation de l'appel d'offre
        summary (str): Le résumé de l'appel d'offre
        url (str): L'url de l'appel d'offre
        scoring (dict): Le score de l'appel d'offre
    """
    
    mail_sender = os.getenv("MAIL_SENDER")  
    mail_password = os.getenv("MAIL_PASSWORD")
    smtp_server = "smtp.office365.com"
    port = 587  # TLS port
    msg = MIMEMultipart()
    msg["From"] = mail_sender
    msg["To"] = mail_sender
    msg["Subject"] = "Nouvel appel d'offre : " + str(type_appel_offre)
    msg.attach(MIMEText(f"""Une nouvelle offre vient d'arriver et peut correspondre à vos critère : \n\n
                        Résumé : {summary} \n\n
                        url : {url} \n\n
                        Scoring de la pertinence du résumé sur la catégorie : {scoring} \n\n
                        """, "plain"))

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls(context=context)
        server.login(mail_sender, mail_password)
        server.sendmail(mail_sender, mail_sender, msg.as_string())


#boucler sur les appels d'offres et passer dans LLm

if __name__ == "__main__":
    load_dotenv()
    ao_list,ao_liens = scraping_ao()
    for idx, ao in enumerate(ao_list):
        LLM_res = text_to_llm(ao)

        if(LLM_res["Classes"]["Labels"][0] == "Fourniture"):
            send_alerting_mail(LLM_res["Classes"]["Labels"][0], LLM_res["Summary"], ao_liens[idx], LLM_res["Score"])
        

