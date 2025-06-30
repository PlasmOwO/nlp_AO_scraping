# nlp_AO_scraping
Projet universitaire de scraping d'appel d'offre pour de l'alerting

Pour lancer le code (tout en 1): 
```pip install -r requirements.txt```  

Pour les notebooks permettant de tester itérativement : 
* Scraping : ```Scrapping.ipynb```
* LLMs stuff : ``llm_test.ipynb```
* Mail alerting : ```alerting_mail.ipynb```

Renseigner le fichier DOTENV : 
```.env
MAIL_SENDER = "...."
MAIL_PASSWORD = "...."
```
(fonctionne uniquement avec des adresses YNOV.com)
Puis lancer le fichier python : scraping_to_mail.py

Ce code va scraper plusieurs appels d'offres et seul ceux qui correspondent a la catégorie fourniture seront envoyé en alerte par mail.




