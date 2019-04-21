''' #Running program akan sangat lama. Silakan ditinggal mandi.
    yang akan kita lakuin di sini:
    1. crawling
    2. Membentuk VSM (TF-IDF)
    3. Seleksi fitur (Pake Pearson)
    4. Clustering / Klasifikasi
'''
# For crawling purpose
import requests
from bs4 import BeautifulSoup
# For db purpose
import sqlite3
import csv
# For text mining purpose
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
# For processing purpose
from math import log10
import numpy as np 
from sklearn.metrics import silhouette_samples, silhouette_score
import skfuzzy as fuzz
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import confusion_matrix

#from sklearn.feature_extraction.text import CountVectorizer
#from sklearn.feature_extraction.text import TfidfTransformer
#from sklearn.feature_selection import SelectKBest
#from sklearn.feature_selection import chi2


def write_csv(nama_file, isi, tipe='w'):
    'tipe=w; write; tipe=a; append;'
    with open(nama_file, mode=tipe) as tbl:
        tbl_writer = csv.writer(tbl, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in isi:
            tbl_writer.writerow(row)

def crawl(src, kategori='NA'):
    global c
    page = requests.get(src)

    # Mengubah html ke object beautiful soup
    soup = BeautifulSoup(page.content, 'html.parser')

    # Find all item
    items = soup.findAll(class_='article-item')
    '''
    tmp = soup.find(class_='inline field')
    maxPage = int(tmp.findAll('label')[-1].getText()[2:])
    now = int(tmp.find(id='page')['value'])
    '''

    #print ('Proses : %.2f' %((c/maxPage)*100) + '%'); c+=1
    for item in items:
        judul = item.find(class_='title-article').getText()
        authors = item.find(class_="author-article").findAll(class_='title-author')
        author = ''
        for i in authors: author = author+i.getText()+'; '
        abstrack = item.find(class_='article-abstract').find('p').getText()

        #pengecekan data redundant
        cursor = conn.execute('select * from jurnal2 where judul=?', (judul,))
        cursor = cursor.fetchall()
        if (len(cursor) == 0):
            conn.execute("INSERT INTO jurnal2 \
                        VALUES (?, ?, ?, ?)", (judul, author, abstrack, kategori));
    #nextPage
    '''
    if (now != maxPage):
        nextPage = tmp.findAll(class_='ui mini icon button')[-1]['href']
        crawl(nextPage)
    '''
def preprosesing(txt):
    SWfactory = StopWordRemoverFactory()
    stopword = SWfactory.create_stop_word_remover()

    Sfactory = StemmerFactory()
    stemmer = Sfactory.create_stemmer()
    hasil = ''
    for i in txt.split():
        if i.isalpha():
            # Menghilangkan Kata tidak penting
            stop = stopword.remove(i)
            stem = stemmer.stem(stop)
            hasil += stem  + ' '
    return hasil

#VSM
def tokenisasi(txt, ngram=1):
    token = []
    start=0
    end=ngram
    txtSplit = txt.split()
    while end <= len(txtSplit):
        tmp = txtSplit[start:end]
        frase = '' 
        for i in tmp:
            frase += i+ ' ' 
        token.append(frase)
        end+=1; start +=1;
    return token
def countWord(txt, ngram=1):
    '''
        Fungsi ini digunakan untuk menghitung setiap kata pada satu string
    '''
    d = dict()
    token = tokenisasi(txt, ngram)
    for i  in token:
        if d.get(i) == None:
            d[i] = txt.count(i)
    return d

def add_row_VSM(d):
    '''
        Fungsi ini digunakan untuk membangun VSM
    '''
    #init baris baru
    VSM.append([])
    # memasukkan kata berdasarkan kata yang telah ditemukan sebelumnya
    for i in VSM[0]:
        if d.get(i) == None:
            VSM[-1].append(0)
        else :
            VSM[-1].append(d.pop(i));

    # memasukkan kata baru 
    for i in d:
        VSM[0].append(i) #fitur baru
        for j in range(1, len(VSM)-1):
            #VSM[j].insert(-2,0)
            VSM[j].append(0)
        VSM[-1].append(d.get(i))

def pearsonCalculate(data, u,v):
    "i, j is an index"
    atas=0; bawah_kiri=0; bawah_kanan = 0
    for k in range(len(data)):
        atas += (data[k,u] - meanFitur[u]) * (data[k,v] - meanFitur[v])
        bawah_kiri += (data[k,u] - meanFitur[u])**2
        bawah_kanan += (data[k,v] - meanFitur[v])**2
    bawah_kiri = bawah_kiri ** 0.5
    bawah_kanan = bawah_kanan ** 0.5
    return atas/(bawah_kiri * bawah_kanan)
def meanF(data):
    meanFitur=[]
    for i in range(len(data[0])):
        meanFitur.append(sum(data[:,i])/len(data))
    return np.array(meanFitur)
def seleksiFiturPearson(data, threshold):
    global meanFitur
    meanFitur = meanF(data)
    u=0
    while u < len(data[0]):
        dataBaru=data[:, :u+1]
        meanBaru=meanFitur[:u+1]
        v = u
        while v < len(data[0]):
            if u != v:
                value = pearsonCalculate(data, u,v)
                if value < threshold:
                    dataBaru = np.hstack((dataBaru, data[:, v].reshape(data.shape[0],1)))
                    meanBaru = np.hstack((meanBaru, meanFitur[v]))
            v+=1
        data = dataBaru
        meanFitur=meanBaru
        if u%50 == 0 : print("proses : ", u, data.shape)
        u+=1
    return data
conn = sqlite3.connect('test.db')
choice = input("Update data? Y/N").lower()
if choice == 'y':
    conn.execute('drop table if exists jurnal2')
    conn.execute('''CREATE TABLE jurnal2
                 (JUDUL          TEXT     NOT NULL,
                 PENULIS         TEXT     NOT NULL,
                 ABSTRAK         TEXT     NOT NULL,
                 KATEGORI        TEXT     NOT NULL);''')
    c=1;    src = 'http://garuda.ristekdikti.go.id/journal/view/5995' #teknik
    crawl(src, 'teknik');    conn.commit()
    c=1;    src = 'http://garuda.ristekdikti.go.id/journal/view/14064' #biologi
    crawl(src, 'biologi');    conn.commit()
    c=1;    src = 'http://garuda.ristekdikti.go.id/journal/view/10172' #Pendidikan
    crawl(src, 'pendidikan');    conn.commit()    
    c=1;    src = 'http://garuda.ristekdikti.go.id/journal/view/11646' #teknik
    crawl(src, 'teknik');    conn.commit()
    c=1;    src = 'http://garuda.ristekdikti.go.id/journal/view/6233' # biologi
    crawl(src, 'biologi');    conn.commit()
    c=1;    src = 'http://garuda.ristekdikti.go.id/journal/view/7689' #pendidikan
    crawl(src, 'pendidikan');    conn.commit()
    
    c=1;    src = 'http://garuda.ristekdikti.go.id/journal/view/12003' #teknik
    crawl(src, 'teknik');    conn.commit()
    c=1;    src = 'http://garuda.ristekdikti.go.id/journal/view/13196' #biologi
    crawl(src, 'biologi');    conn.commit()
    c=1;    src = 'http://garuda.ristekdikti.go.id/journal/view/9944' #pendidikan
    crawl(src, 'pendidikan');    conn.commit()

print("Building VSM...")
cursor = conn.execute("SELECT * from jurnal2")
cursor = cursor.fetchall()
#cursor = cursor[:60]
pertama = True
corpus = list()
label = list()
c=1
n = int(input("ngram : "))
#n=1
for row in cursor:
    print ('Proses : %.2f' %((c/len(cursor))*100) + '%'); c+=1
    label.append(row[-1])
    txt = row[-2]

    cleaned = preprosesing(txt)
    cleaned = cleaned[:-1]
    corpus.append(cleaned)

    d = countWord(cleaned, n)
    if pertama:
        pertama = False
        VSM = list((list(), list()))
        for key in d:
            VSM[0].append(key)
            VSM[1].append(d[key])
    else:
        add_row_VSM(d)
    
write_csv("bow_manual_%d.csv"%n, VSM)
label = np.array(label)
feature_name = VSM[0]
bow = np.array(VSM[1:])

df = list()
total_doc = bow.shape[0]
for kolom in range(len(bow[0])):
    total = 0
    for baris in range(len(bow)):
        if (bow[baris, kolom] > 0):
            total +=1
    df.append(total)
df = np.array(df)

idf = list()
for i in df:
    tmp = 1 + log10(total_doc/(1+i))
    idf.append(tmp)
idf = np.array(idf)

tfidf = bow * idf

write_csv("tfidf%d.csv"%n, [feature_name])
write_csv("tfidf%d.csv"%n, tfidf, 'a')

xBaru2 = seleksiFiturPearson(tfidf, 0.9)
xBaru1 = seleksiFiturPearson(xBaru2, 0.8)

'''
    Skenario:
    1. Cluster tanpa diseleksi
    2. Cluster dengan Seleksi Pearson, dengan threshold 0.8
    2. Cluster dengan Seleksi Pearson, dengan threshold 0.9
    2. Cluster dengan Seleksi Pearson, dengan threshold 0.95
'''

print("Cluster Tanpa Seleksi fitur")
cntr, u, u0, distant, fObj, iterasi, fpc =  fuzz.cmeans(tfidf.T, 3, 2, 0.00001, 1000, seed=0)
membership = np.argmax(u, axis=0)

silhouette = silhouette_samples(tfidf, membership)
s_avg = silhouette_score(tfidf, membership, random_state=10)

for i in range(total_doc):
    print("c "+str(membership[i]))#+"\t" + str(silhouette[i]))
print(s_avg)

#kmeans = KMeans(n_clusters=3, random_state=0).fit(tfidf)
#print(kmeans.labels_)

write_csv("Cluster%d.csv"%n, [["Cluster"]])
write_csv("Cluster%d.csv"%n, [membership],        "a")
write_csv("Cluster%d.csv"%n, [["silhouette"]],    "a")
write_csv("Cluster%d.csv"%n, [silhouette],        "a")
write_csv("Cluster%d.csv"%n, [["Keanggotaan"]],   "a")
write_csv("Cluster%d.csv"%n, u,                   "a")
write_csv("Cluster%d.csv"%n, [["pusat Cluster"]], "a")
write_csv("Cluster%d.csv"%n, cntr,                "a")

#----------------------------------
print("Cluster dgn Seleksi Fitur : 0.8")
cntr, u, u0, distant, fObj, iterasi, fpc =  fuzz.cmeans(xBaru1.T, 3, 2, 0.00001, 1000, seed=0)
membership = np.argmax(u, axis=0)

silhouette = silhouette_samples(xBaru1, membership)
s_avg = silhouette_score(xBaru1, membership, random_state=10)

for i in range(total_doc):
    print("c "+str(membership[i]))#+"\t" + str(silhouette[i]))
print(s_avg)
#kmeans = KMeans(n_clusters=3, random_state=0).fit(xBaru)
#print(kmeans.labels_)

write_csv("Cluster%dFS8.csv"%n, [["Cluster"]])
write_csv("Cluster%dFS8.csv"%n, [membership],        "a")
write_csv("Cluster%dFS8.csv"%n, [["silhouette"]],    "a")
write_csv("Cluster%dFS8.csv"%n, [silhouette],        "a")
write_csv("Cluster%dFS8.csv"%n, [["Keanggotaan"]],   "a")
write_csv("Cluster%dFS8.csv"%n, u,                   "a")
write_csv("Cluster%dFS8.csv"%n, [["pusat Cluster"]], "a")
write_csv("Cluster%dFS8.csv"%n, cntr,                "a")
    



print("Cluster dgn Seleksi Fitur : 0.9")
cntr, u, u0, distant, fObj, iterasi, fpc =  fuzz.cmeans(xBaru2.T, 3, 2, 0.00001, 1000)
membership = np.argmax(u, axis=0)

silhouette = silhouette_samples(xBaru2, membership)
s_avg = silhouette_score(xBaru2, membership, random_state=10)

for i in range(total_doc):
    print("c "+str(membership[i]))#+"\t" + str(silhouette[i]))
print(s_avg)

write_csv("Cluster%dFS9.csv"%n, [["Cluster"]])
write_csv("Cluster%dFS9.csv"%n, [membership],        "a")
write_csv("Cluster%dFS9.csv"%n, [["silhouette"]],    "a")
write_csv("Cluster%dFS9.csv"%n, [silhouette],        "a")
write_csv("Cluster%dFS9.csv"%n, [["Keanggotaan"]],   "a")
write_csv("Cluster%dFS9.csv"%n, u,                   "a")
write_csv("Cluster%dFS9.csv"%n, [["pusat Cluster"]], "a")
write_csv("Cluster%dFS9.csv"%n, cntr,                "a")


#----------------------------------
# Klasifikasi
#----------------------------------

x_train, x_test, y_train, y_test = train_test_split(xBaru1, label, test_size=0.33, random_state=0)

model = MultinomialNB().fit(x_train, y_train)
predicted = model.predict(x_test)

akurasi = np.mean(predicted == y_test)
cm = confusion_matrix(y_test, predicted)

print("akurasi : %.2f"%akurasi)
print("confusion matrix:")
print(cm)
