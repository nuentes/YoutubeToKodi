#********************USER CONFIG********************#
#enter your API key, refresh interval, and the
#directory where you'd like to put the files
key = "AIzaSyB1sD79USBsvw3DrNsmH5vkSpjZXWGDpa4"
minutes = 60
DestDir = "/media/andre/2TB/Completed/Youtube/"
#******************END USER CONFIG******************#

import requests
import json
import urllib
import time
import os
import sys
import shutil
import re

reload(sys)
sys.setdefaultencoding('utf8')

def fileNameCreator(name):
    name = name.replace('"','')
    name = name.replace('<','')
    name = name.replace('>','')
    name = name.replace('\\','')
    name = name.replace('/','')
    name = name.replace(':','')
    name = name.replace('*','')
    name = name.replace('?','')
    name = name.replace('|','')
    name = name.replace('  ',' ')
    return name

def updateListFile():
    #write the array to list.txt
    listFile = open(full_path + "/list.txt","wb")
    listFile.truncate()
    i=0
    while i < myLen:
        listFile.write(arr[i] + "/" + arr[i+1] + "\r\n")
        i = i+2
    listFile.close()

def sanitizer(txt):
    #clean up the plots/descriptions - scrub out and links, remove line breaks
    endSearch = False
    txt2 = ""
    lines = txt.split('\n')
    for x in range(0,len(lines)):
        if lines[x].find("http:") > -1:
            endSearch = True
        elif endSearch == False:
            txt2 = txt2 + " " + lines[x]
    txt2 = txt2[1:]
    txt2 = txt2.replace("\n"," ")
    txt2 = txt2.replace("  "," ")
    txt2 = txt2.replace("  "," ")
    return txt2

#find and/or create file with usernames and latest upload
full_path = os.path.dirname(os.path.realpath(__file__))
if not os.path.isfile(full_path + "/" + "list.txt"):
    print "There is no list.txt file.  You must create this file and place it in the same directory as this script. Then just add each channel or UserID as separate lines in the file"
else:
    while minutes == minutes:
        arr = open(full_path + "/list.txt","r").read().split()
        #determine if we have searched for each of these shows before - if we haven't make it look like we have
        myLen = len(arr) * 2
        i=0
        while i < myLen:
            var = arr[i].find('/')
            if var == -1:
                try:
                    arr.insert(i + 1, "xyz")
                except:
                    arr.append("xyz")
            else:
                a = arr[i].split("/")
                arr[i] = a[0]
                try:
                    arr.insert(i + 1, a[1])
                except:
                    arr.append("test")
            i = i+2
        updateListFile()
        i = 0
        #loop through the shows and collect data
        while i < len(arr):
            try:
                #this should work if the input is a username
                r = requests.get("https://www.googleapis.com/youtube/v3/channels?key="+key+"&forUsername="+arr[i]+"&part=id")
                text = json.loads(r.text)
                channelId = text['items'][0]['id']
            except:
                #if it didn't work, we'll assume it was a channelId
                channelId = arr[i]

            #Get the playlist
            try:
                r = requests.get("https://www.googleapis.com/youtube/v3/channels?id="+channelId+"&key="+key+"&part=snippet,contentDetails,brandingSettings")
            except:
                print arr[i] + " is not a valid username or Channel ID"
                break
            text = json.loads(r.text)
            items = text['items'][0]
            uploadPlaylist = items['contentDetails']['relatedPlaylists']['uploads']
            #add the data for the channel if it doesn't already exist
            channelName = items['snippet']['title']
            if not os.path.exists(DestDir + channelName):
                os.makedirs(DestDir + channelName)
            if not os.path.isfile(DestDir + channelName + "/tvshow.nfo"):
                myFile = os.path.join(DestDir + channelName, "/tvshow.nfo")
                plot = sanitizer(items['snippet']['description'].encode('utf-8').strip())
                with open(DestDir + channelName + "/tvshow.nfo", 'a') as file:
                    file.write('<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\r\n')
                    file.write('<tvshow>\r\n')
                    file.write('	<title>' + channelName + '</title>\r\n')
                    file.write('	<plot>' + plot + '</plot>\r\n')
                    file.write('	<studio>YouTube</studio>\r\n')
                    file.write('</tvshow>')
                    file.close()
                urllib.urlretrieve(items['brandingSettings']['image']['bannerTvImageUrl'], os.path.join(DestDir + channelName, "fanart.jpg"))
                urllib.urlretrieve(items['snippet']['thumbnails']['high']['url'], os.path.join(DestDir + channelName, "folder.jpg"))
                shutil.copy2(DestDir + channelName + "/folder.jpg", DestDir + channelName + "/poster.jpg")
					
            #Get the data of the videos and add to a file.
            r = requests.get("https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId="+uploadPlaylist+"&key="+key+"&maxResults=50")
            text = json.loads(r.text)
            items = text['items']
            lastSavedID = arr[i+1]
            endLoop = False
            if items[0]['snippet']['resourceId']['videoId'] == lastSavedID or endLoop:
                endLoop = True
            else:
                #add the strm, nfo, and thumbnail files
                for j in range(0,len(items)):
                    videoId = items[j]['snippet']['resourceId']['videoId']
                    if videoId == lastSavedID or endLoop:
                        endLoop = True
                    else:
                        if j == 0:
                            arr[i+1] = videoId
                            updateListFile()
                        #without duration, these never get marked as watched.  The PlaylistItem API was not giving me video duration
                        r = requests.get("https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails&id="+videoId+"&key="+key)
                        text = json.loads(r.text)
                        thisVideoData = text['items'][0]
                        myDate = thisVideoData['snippet']['publishedAt'][:10]
                        myYear = myDate[:4]
                        path = DestDir + channelName + "/" + myYear + "/"
                        title = fileNameCreator(thisVideoData['snippet']['title'].encode('utf-8').strip())
                        DateAndTitle = myDate + " " + title
                        if not os.path.exists(path):
                            os.makedirs(path)
                        myFile = os.path.join(path, DateAndTitle + ".nfo")
                        myFile = os.path.join(path, DateAndTitle + ".strm")
                        myFile = open(path + DateAndTitle + ".strm","w")
                        myFile.write("plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid=" + videoId)
                        myFile.close()
                        duration = thisVideoData['contentDetails']['duration']
                        durH = re.search('(\d+)H', duration)
                        durM = re.search('(\d+)M', duration)
                        durS = re.search('(\d+)S', duration)
                        if durH and durM:
                            duration = str(int(durH.group(0)[:-1]) * 60 + int(durM.group(0)[:-1]))
                        elif durH:
                            duration = str(int(durH.group(0)[:-1]) * 60)
                        elif durM and durS:
                            duration = durM.group(0)[:-1] + ":" + durS.group(0)[:-1].zfill(2)
                        elif durM:
                            duration = durM.group(0)[:-1] + ":00"
                        else:
                            duration = "0:" + durS.group(0)[:-1].zfill(2)
                        print "Adding " + channelName + " episode " + title
                        description = sanitizer(items[j]['snippet']['description'].encode('utf-8').strip())
                        with open(path + DateAndTitle + ".nfo", 'a') as file:
                            file.write('<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\r\n')
                            file.write('<episodedetails>\r\n')
                            file.write('	<title>' + title + '</title>\r\n')
                            file.write('	<season>' + myYear + '</season>\r\n')
                            file.write('	<episode>' + myDate[5:] + '</episode>\r\n')
                            file.write('	<plot>' + description + '</plot>\r\n')
                            file.write('	<aired>' + myDate + '</aired>\r\n')
                            file.write('	<runtime>' + duration + '</runtime>\r\n')
                            file.write('	<studio>youtube</studio>\r\n')
                            file.write('</episodedetails>')
                            file.close()
                        myFile.close()
                        #And download the episode thubnail
                        urllib.urlretrieve(thisVideoData['snippet']['thumbnails']['high']['url'], os.path.join(path, DateAndTitle +".jpg"))
            i = i+2
        time.sleep(minutes*60)
