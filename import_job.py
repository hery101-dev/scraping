import pandas as pd
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
from fuzzywuzzy import process
import random
import locale
import numpy as np



locale.setlocale(locale.LC_ALL, 'french')
# Charger le fichier Excel
file_path = 'excel_data/offres(101-150).xlsx'
df_offres = pd.read_excel(file_path)

months_fr_to_en = {
    'Jan': '01', 'Fév': '02', 'Mar': '03', 'Avr': '04',
    'Mai': '05', 'Jun': '06', 'Jul': '07', 'Aoû': '08',
    'Sep': '09', 'Oct': '10', 'Nov': '11', 'Déc': '12'
}

try:
    # Connexion à MySQL
    conn = mysql.connector.connect(host='localhost', user='root', password='', database='nexthoperecrut')
    cursor = conn.cursor()

    cursor.execute("SELECT category_name FROM categories")
    categories = [row[0] for row in cursor.fetchall()]
    def assign_category(title):
        # Trouve la catégorie la plus similaire au titre de l'offre
        category, score = process.extractOne(title, categories)
        return category if score > 60 else 'Autre'
    
    cursor.execute("SELECT id FROM user WHERE roles LIKE '%ROLE_RECRUITER%'")
    recruiter = [row[0] for row in cursor.fetchall()]

    def convert_date(date_str, default_date=datetime.today()):
        if pd.isnull(date_str):
            return default_date
        try:
            return datetime.strptime(str(date_str), '%d/%m/%Y').strftime('%Y-%m-%d')
        except ValueError:
            return default_date
        

    for index, row in df_offres.iterrows():

        # print(f"Ligne {index}, Created At: {row['Created At']}, Deadline: {row['Deadline']}")

        title = row['Title'] if pd.notnull(row['Title']) else ''
        description = row['Description'] if pd.notnull(row['Description']) else ''
        recruiter_id = random.choice(recruiter)

        category_name = assign_category(row['Title'])

        # Récupérer l'ID de la catégorie correspondante
        cursor.execute("SELECT id FROM categories WHERE category_name = %s", (category_name,))
        category_result = cursor.fetchone()

        if category_result:
            category_id = category_result[0]
        else:
            print(f"Catégorie '{category_name}' non trouvée pour la ligne {index}")
            continue

        createdAt = convert_date(row['Created At'], datetime.today())
        deadlineAt = convert_date(row['Deadline'], datetime.today() + timedelta(days=30))

        # Trouver l'ID de l'entreprise par le nom
        cursor.execute("SELECT id FROM company WHERE company_name = %s", (row['Company Name'],))
        company_result = cursor.fetchone()
        if not company_result:
            print(f"Entreprise '{row['Company Name']}' introuvable.")
            continue
        company_id = company_result[0]

        # Insérer l'offre d'emploi
        cursor.execute("INSERT INTO job_offer (category_id, company_id, user_id, title, description, created_at, deadline_at) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                       (category_id, company_id, recruiter_id, title, description, createdAt, deadlineAt))
        job_offer_id = cursor.lastrowid

        # Trouver l'ID du contrat par le type de contrat
        cursor.execute("SELECT id FROM contrat WHERE type = %s", (row['Contract'],))
        contrat_result = cursor.fetchone()
        if not contrat_result:
            print(f"Contrat '{row['Contract']}' introuvable.")
            continue
        contrat_id = contrat_result[0]

        # Associer l'offre d'emploi au contrat
        cursor.execute("INSERT INTO contrat_job_offer (job_offer_id, contrat_id) VALUES (%s, %s)", 
                       (job_offer_id, contrat_id))

    conn.commit()

except Error as e:
    print(f"Erreur lors de la connexion à MySQL: {e}")
    conn.rollback()

finally:
    if conn.is_connected():
        cursor.close()
        conn.close()
        print("La connexion MySQL est fermée.")
