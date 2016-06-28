from PyLyrics import *
from bs4 import BeautifulSoup
import requests
import time
import os
if os.name == "nt":
    import pywintypes
    import win32gui
else:
    import subprocess
    import re

def getlyrics(songname):
    error = "Error: Could not find lyrics."
    artist = ""
    song = ""
    if songname.count(" - ") == 1:
        artist, song = songname.rsplit(" - ", 1)
    if songname.count(" - ") == 2:
        artist, song, garbage = songname.rsplit(" - ", 2)

    def lyrics_wikia(artist, song):
        try:
            lyrics = PyLyrics.getLyrics(artist, song)
        except Exception:
            lyrics = error
        if "TrebleClef.png" in lyrics and "Instrumental" in lyrics:
            lyrics = "(Instrumental)"
        return(lyrics)

    def lyrics_musixmatch(artist, song):
        try:
            artistm = artist.replace(" ", "-")
            songm = song.replace(" ", "-")
            url = "https://www.musixmatch.com/lyrics/%s/%s" % (artistm, songm)
            lyricspage = requests.get(url)
            soup = BeautifulSoup(lyricspage.text, 'html.parser')
            lyrics = soup.text.split('"body":"')[1].split('","language"')[0]
            lyrics = lyrics.replace("\\n", "\n")
        except Exception:
            lyrics = error
        return(lyrics)

    def lyrics_songmeanings(artist, song):
        try:
            searchurl = "http://songmeanings.com/m/query/?q=%s %s" % (artist, song)
            searchresults = requests.get(searchurl)
            soup = BeautifulSoup(searchresults.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                if "songmeanings.com/m/songs/view/" in link['href']:
                    break
                elif "/m/songs/view/" in link['href']:
                    result = "http://songmeanings.com" + link['href']
                    lyricspage = requests.get(result)
                    soup = BeautifulSoup(lyricspage.text, 'html.parser')
                    break
                else:
                    pass
            templyrics = soup.find_all("li")[4]
            lyrics = templyrics.getText()
        except Exception:
            lyrics = error
        if lyrics == "We are currently missing these lyrics.":
            lyrics = error
        return(lyrics)

    def lyrics_songlyrics(artist, song):
        try:
            artistm = artist.replace(" ", "-")
            songm = song.replace(" ", "-")
            url = "http://www.songlyrics.com/%s/%s-lyrics" % (artistm, songm)
            lyricspage = requests.get(url)
            soup = BeautifulSoup(lyricspage.text, 'html.parser')
            lyrics = soup.find(id="songLyricsDiv").get_text()
        except Exception:
            lyrics = error
        if "Sorry, we have no" in lyrics:
            lyrics = error
        return(lyrics)

    def lyrics_genius(artist, song):
        try:
            searchurl = "http://genius.com/search?q=%s %s" % (artist, song)
            searchresults = requests.get(searchurl)
            soup = BeautifulSoup(searchresults.text, 'html.parser')
            result = str(soup).split('song_link" href="')[1].split('" title=')[0]
            lyricspage = requests.get(result)
            soup = BeautifulSoup(lyricspage.text, 'html.parser')
            lyrics = soup.text.split('Lyrics\n\n\n')[1].split('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n              About')[0]
        except Exception:
            lyrics = error
        return(lyrics)

    lyrics = lyrics_wikia(artist, song)
    if lyrics == error:
        lyrics = lyrics_musixmatch(artist, song)
    if lyrics == error:
        lyrics = lyrics_songmeanings(artist, song)
    if lyrics == error:
        lyrics = lyrics_songlyrics(artist, song)
    if lyrics == error:
        lyrics = lyrics_genius(artist, song)

    lyrics = lyrics.replace("&amp;", "&")
    lyrics = lyrics.replace("`", "'")
    return(lyrics)

def getwindowtitle():
    if os.name == "nt":
        spotify = win32gui.FindWindow('SpotifyMainWindow', None)
        windowname = win32gui.GetWindowText(spotify)
    else:
        command = "xwininfo -tree -root"
        windows = subprocess.check_output(["/bin/bash", "-c", command]).decode("utf-8")
        spotify = ''
        for line in windows.splitlines():
            if '("spotify" "Spotify")' in line:
                if " - " in line:
                    spotify = line
                    break
        if spotify != '':
            windowname = re.findall(r'"(.*?)"', spotify)[0]
        else:
            windowname = ''
    if "—" in windowname:
        windowname = windowname.replace("—", "-")
    if "Spotify - " in windowname:
        windowname = windowname.strip("Spotify - ")
    return(windowname)

def main():
    if os.name == "nt":
        os.system("chcp 65001")
    def clear():
        if os.name == "nt":
            os.system("cls")
        else:
            os.system("clear")
    clear()
    oldsongname = ""
    while True:
        songname = getwindowtitle()
        if oldsongname != songname:
            if songname != "Spotify":
                oldsongname = songname
                clear()
                print(songname+"\n")
                lyrics = getlyrics(songname)
                print(lyrics+"\n")
        time.sleep(1)

if __name__ == '__main__':
    main()
