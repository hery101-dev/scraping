import pandas as pd
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import locale
locale.setlocale(locale.LC_TIME, 'fr_FR')


try:
    # Charger le fichier Excel
    df = pd.read_excel('excel_data/categorie.xlsx')

    # Connexion à MySQL
    conn = mysql.connector.connect(host='localhost', user='root', password='', database='nexthoperecrut')
    
    # Vérifier si la connexion est réussie
    if conn.is_connected():
        print('Connexion réussie à MySQL')
        
        cursor = conn.cursor()

        for index, row in df.iterrows():
            # Vérifier si le nom de l'entreprise existe déjà dans la base de données
            cursor.execute("SELECT COUNT(*) FROM categories WHERE category_name = %s", (row['Categorie'],))
            result = cursor.fetchone()

            if result[0] == 0:  # Si le nom de l'entreprise n'existe pas, l'insérer
                cursor.execute("INSERT INTO categories (category_name) VALUES (%s)", (row['Categorie'],))
            else:
                print(f"Le categorie '{row['Categorie']}' existe déjà dans la base de données.")

        conn.commit()
        cursor.close()
        print("Les données ont été traitées avec succès.")
        
    else:
        print("Connexion échouée.")

except Error as e:
    print(f"Erreur lors de la connexion à MySQL: {e}")

finally:
    if conn.is_connected():
        conn.close()
        print("La connexion MySQL est fermée.")
