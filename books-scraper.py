import requests
from bs4 import BeautifulSoup
import re
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate(r"C:\Users\Muhammad Maaz Ahmed\Downloads\serviceAccountKey.json")
app = firebase_admin.initialize_app(cred)
db = firestore.client()

data = []
titles = []
base_url = "https://books.toscrape.com"

# for formatting title according to url
def convert_text(text):
  formatted_string = text.lower()
  formatted_string = formatted_string.replace(" ", "-")
  formatted_string = re.sub(r'[^\w\s-]', '', formatted_string)
  return formatted_string

def convert_to_absolute_url(base_url, relative_url):
  path_segments = relative_url.split("/")
  clean_path_segments = [segment for segment in path_segments if segment != ".."]
  absolute_url = "/".join([base_url] + clean_path_segments)
  return absolute_url

# getting titles for making urls
def getTitles(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    h3_tags = soup.find_all('h3')
    title_tags = [tag.a['title'] for tag in h3_tags if tag.a]
    for title in title_tags:
        modified_title = convert_text(title)
        titles.append(modified_title)


def getCompleteBooksData(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    # title
    fetched_title = soup.find('h1')
    # price
    price = soup.find('p', class_="price_color")
    # description
    all_p_tags = soup.find_all('p')
    description = next((tag for tag in all_p_tags if not tag.attrs), None)
    # book id
    table = soup.find('table')
    all_trs = table.find_all('tr') if table else None
    first_tr = table.find('tr') if table else None
    bookId = first_tr.find('td')
    # availibility
    second_last_tr = all_trs[-2] if all_trs and len(all_trs) >= 2 else None
    availibility = second_last_tr.find("td")
    # image url
    img_tag = soup.find('img')
    src = img_tag.get('src')
    url = convert_to_absolute_url(base_url, src)
    book = {"bookId": bookId.string, "title": fetched_title.string, "price": price.string, "description": description.string, "availibility": availibility.string, "imgUrl": url}
    data.append(book)

for i in range(1,3):
    url = f"https://books.toscrape.com/catalogue/page-{i}.html"
    getTitles(url)


i = 0
bookNum = 1000

while i < 25:
  url = f"https://books.toscrape.com/catalogue/{titles[i]}_{bookNum}/index.html"
  print(url)
  getCompleteBooksData(url)
  i += 1
  bookNum -= 1

for j in range(len(data)):
   print(data[j])
   db.collection("books").document(data[j]["bookId"]).set(data[j])

