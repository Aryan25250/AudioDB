from flask import Flask, render_template, request
import requests
import sqlite3

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        artist_name = request.form['artist']
        albums = search_albums(artist_name)
        save_albums_to_db(artist_name, albums)

        def sort(v):
            if "sort" in request.form and request.form["sort"] in v:
                return v[request.form["sort"]]
            else:
                return v["intYearReleased"]


        if "reverse" in request.form:
            isReversed = True
            if request.form["oldSort"] == request.form["sort"]:
                isReversed = not request.form["reverse"] == "True"

            print(isReversed)

            albums.sort(key=sort,reverse=request.form["reverse"]=="True")
            return render_template('results.html', artist=artist_name, albums=albums, oldSort=request.form["sort"], reverse=isReversed)
        else:
            albums.sort(key=sort,reverse=False)
            if "sort" in request.form:
                return render_template('results.html', artist=artist_name, albums=albums, oldSort=request.form["sort"], reverse=False)
            else:
                return render_template('results.html', artist=artist_name, albums=albums,reverse=False)

    return render_template('index.html')


def search_albums(artist_name):
    API_KEY = '523532'
    URL = f'https://theaudiodb.com/api/v1/json/{API_KEY}/searchalbum.php?s={artist_name}'
    response = requests.get(URL)
    data = response.json()
    albums = data['album']
    return albums


def save_albums_to_db(artist_name, albums):
    conn = sqlite3.connect('albums.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS albums
                 (artist TEXT, album TEXT, year INTEGER)''')

    for album in albums:
        c.execute("INSERT INTO albums VALUES (?,?,?)", (artist_name, album['strAlbum'], album['intYearReleased']))
    conn.commit()
    conn.close()


if __name__ == '__main__':
    app.run(debug=True)