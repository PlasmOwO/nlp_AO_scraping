# nlp_AO_scraping
Projet universitaire de scraping d'appel d'offre pour de l'alerting

Pour lancer le code : 
```pip install -r requirements.txt```  

Renseigner le fichier DOTENV : 
```.env
MAIL_SENDER = "...."
MAIL_PASSWORD = "...."
```

Puis lancer le fichier python : scraping_to_mail.py

Ce code va scraper plusieurs appels d'offres et seul ceux qui correspondent a la catégorie fourniture seront envoyé en alerte par mail.



------OLD 
INstaller fasttext wheel :--> Need visual studio build tools, cocher Desktop developement with C++ (6GB)

pip install ipywidgets
pip install torch
pip install sentencepiece
pip install transformers
pip install huggingface_hub[hf_xet]
pip install mistral_inference
pip install -U "huggingface_hub[cli]"
pip3 install -U xformers --index-url https://download.pytorch.org/whl/cu126
pip install accelerate

pip install "transformers==4.39.3"

pip install protobuf


