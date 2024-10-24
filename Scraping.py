import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv
import os
import random
import time

# Lista de User-Agents para rotar
user_agents = [
	'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, como Gecko) Chrome/91.0.4472.124 Safari/537.36',
	'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, como Gecko) Chrome/90.0.4430.212 Safari/537.36',
	'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, como Gecko) Firefox/89.0',
	'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
	'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
	'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, como Gecko) Chrome/91.0.4472.124 Safari/537.36',
	'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, como Gecko) Chrome/92.0.4515.107 Safari/537.36',  # Nuevo User-Agent
]

def google_search(query):
	url = f"https://www.google.com.mx/search?q={query.replace(' ', '+')}"
	headers = {
		'User-Agent': random.choice(user_agents),  # Escoge un User-Agent aleatorio
	}
	try:
		response = requests.get(url, headers=headers)
		response.raise_for_status()  # Lanza una excepción para códigos de error HTTP
		soup = BeautifulSoup(response.text, 'html.parser')

		links = []
		for g in soup.find_all('div', class_='g'):
			anchor = g.find('a')
			if anchor and 'href' in anchor.attrs:
				link = anchor['href']
				links.append(link)
				if len(links) >= 10:
					break
		return links
	except requests.exceptions.RequestException as e:
		print(f"Error en la solicitud para la consulta '{query}': {e}")
		return None

# Leer el archivo CSV
file_path = 'KW_scraping.csv'

try:
	df = pd.read_csv(file_path)
except FileNotFoundError:
	print(f"Error: El archivo '{file_path}' no se encuentra en el directorio actual.")
	exit()
except pd.errors.EmptyDataError:
	print(f"Error: El archivo '{file_path}' está vacío.")
	exit()

# Suponiendo que la columna con las consultas se llama 'Query'
if 'Query' not in df.columns:
	print("Error: El archivo CSV debe contener una columna llamada 'Query'.")
	exit()

queries = df['Query'].tolist()

results = []
batch_size = 300
file_count = 1

for i, query in enumerate(queries):
	search_results = google_search(query)
	if search_results is None:
		# Guardar los resultados obtenidos hasta ahora y salir
		break
	for result in search_results:
		results.append([query, result])

	# Guardar los resultados en un CSV cada 'batch_size' consultas
	if (i + 1) % batch_size == 0:
		csv_file = f"google_search_results_full_part{file_count:02}.csv"
		try:
			with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
				writer = csv.writer(file)
				writer.writerow(["Query", "URL"])
				writer.writerows(results)
			print(f"Los resultados se han guardado en '{csv_file}'")
			results = []  # Resetear la lista de resultados
			file_count += 1
		except Exception as e:
			print(f"Error al guardar el archivo CSV: {e}")

	# Espera entre 5 y 10 segundos antes de hacer la siguiente solicitud
	#time.sleep(random.uniform(5, 10))

# Guardar cualquier resultado restante que no haya sido guardado
if results:
	csv_file = f"google_search_results_full_part{file_count:02}.csv"
	try:
		with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
			writer = csv.writer(file)
			writer.writerow(["Query", "URL"])
			writer.writerows(results)
		print(f"Los resultados se han guardado en '{csv_file}'")
	except Exception as e:
		print(f"Error al guardar el archivo CSV: {e}")

# Verificar si el archivo se crea correctamente
if os.path.exists(csv_file):
	print(f"El archivo '{csv_file}' se ha creado correctamente en el directorio actual.")
else:
	print("No se pudo encontrar el archivo CSV en el directorio actual.")
