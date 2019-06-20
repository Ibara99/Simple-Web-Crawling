# For DataFrame Purpose
import numpy as numpy
import pandas as pd
import sqlite3

# For crawling purpose
import requests
from bs4 import BeautifulSoup

# For Graoh purpose
import networkx as nx
import matplotlib.pyplot as plt

def simplifiedURL(url):
    '''
    asumsi: alamat url tidak mengandung http(s) (misalnya "true-http-website.com"
            atau www (misalnya "true-www-website.com")
    '''
    try:
    # cek 1 : www
        if "www." in url:
            ind = url.index("www.")+4
            url = url[ind:]
        if "http" in url:
            ind = url.index(":")+3
            url = url[ind:]
        # cek 3 : tanda / di akhir
        if url[-1] == "/":
            url = url[:-1]
        # Cek 4 : cuma domain utama
        parts = url.split("/")
        url = parts[0]
        return "http://"+url
    except ValueError:
        pass

def crawl(url, max_deep,  show=False, deep=0, done=[]):
    # returnnya ada di edgelist, 
    global edgelist

    # menambah counter kedalaman
    deep += 1
    
    # menyamakan format url, agar tidak ada url yg dobel
    url = simplifiedURL(url)
    #menampilkan proses

    if not url in done:
        # crawl semua link
        links = getAllLinks(url)
        done.append(url)
        if show:
            if deep == 1:
                print(url)
            else:
                print("|", end="")
                for i in range(deep-1): print("--", end="")
                print(url)
            
        for link in links:
            # Membentuk format jalan (edge => (dari, ke))
            link = simplifiedURL(link)
            edge = (url,link)
            # Mengecek jalan, apabila belum dicatat, maka dimasukkan ke list
            if not edge in edgelist:
                edgelist.append(edge)
            # Cek kedalaman, jika belum sampai terakhir, maka crawling.
            if (deep != max_deep):
                crawl(link, max_deep, show, deep, done)
			
def getAllLinks(src):
    # Pencegahan eror apabila link yang diambil mati
    try:
        # Get page html
        page = requests.get(src)

        # Mengubah html ke object beautiful soup
        soup = BeautifulSoup(page.content, 'html.parser')

        # GET all tag <a>
        tags = soup.findAll("a")

        links = []
        for tag in tags:
            # Pencegahan eror apabila link tidak memiliki href
            try:
                # Get all link
                link = tag['href']
                if not link in links and 'http' in link:
                    links.append(link)
            except KeyError:
                pass
        return links
    except:
        #print("Error 404 : Page "+src+" not found")
        return list()

# Inisialisasi variabel awal
conn = sqlite3.connect('test.db')
#root = "https://www.trunojoyo.ac.id/"
root = "http://garuda.ristekdikti.go.id/"
nodelist = [root]
edgelist = []
choice = input("Update data? Y/N").lower()

if choice == 'y':
    conn.execute('drop table if exists edgelist')
    conn.execute('''CREATE TABLE edgelist
                 (src          TEXT     NOT NULL,
                 dest         TEXT     NOT NULL);''')
    #crawl
    crawl(root, 3, show=True)
    for edge in edgelist:
        conn.execute("INSERT INTO edgelist \
                        VALUES (?, ?)", (edge[0], edge[1]));
    conn.commit()
else:
    cursor = conn.execute("SELECT * from edgelist")
    cursor = cursor.fetchall()
    if cursor.isEmpty(): raise sqlite3.Error("Database Kosong")
    for row in cursor:
        edgelist.append((row[0], row[1]))
edgelistFrame = pd.DataFrame(edgelist, None, ("From", "To"))

#membuat Graph
g = nx.from_pandas_edgelist(edgelistFrame, "From", "To", None, nx.DiGraph())

# hitung pagerank
damping = 0.85
max_iterr = 100
error_toleransi = 0.0001
pr = nx.pagerank(g, alpha = damping, max_iter=max_iterr, tol=error_toleransi)

# Creating Data Frame pagerank
nodelist = g.nodes
data = []
for i, key in enumerate(nodelist):
    data.append((pr[key], key))

# mengurutkan PageRank
#urut = data.copy()
for x in range(len(data)):
    for y in range(len(data)):
        if data[x][0] > data[y][0]:
            data[x],data[y] = data[y], data[x]
           
data = pd.DataFrame(data, None, ("PageRank", "Node"))

#buat graph baru dengan label yg sudah diurutkan
g = nx.DiGraph()
g.add_nodes_from(data.Node)
g.add_edges_from(edgelist)
#ibn 1010
# deklarasi pos (koordinat) (otomatis)
pos = nx.spring_layout(g)

# Membuat Label && print pagerank
nodelist = g.nodes
label= {}
for i, key in enumerate(nodelist):
    label[key]=i

# Draw Graph
#plt.figure(1)
#plt.title('circle_layout')
nx.draw(g, pos)
nx.draw_networkx_labels(g, pos, label, font_color="b")

# show figure
print(data)
plt.axis("off")
plt.show()
