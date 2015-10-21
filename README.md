# YoutubeToKodi
This python script will download metadata and images for Youtube channels so you can import them into Kodi as TV Shows.

How to use it:

1) Place the python script anywhere

2) add a list.txt file to the same path

3) add Youtube UserID's and/or channel ID's into the text file (new line for each channel)

4) Edit the user config section of the script to input.

    a) Google API Key
    
    b) refresh interval
    
    c) Destination for the files
    
5) run the script

6) While that's running, add the Destination Directory as a source to Kodi, and set it to scan as a TV show using local data


Known Issues:

1) The developer doesn't know python

2) Currently I've only tested in linux, and I have no idea if it will work in Windows

3) episode numbering is strange

    I can't find any information online about how to complete the episode field of the nfo file
    
4) episodes not automatically marked as watched after completion.

    I thought this would be resolved by adding the runtime field to the episode nfo file, but I was wrong
    
5) no duration for short videos

    at least on my skin, if the duration is under 1 minute, the duration appears as blank
    
6) requires your own Google API Key

7) Initial config isn't exactly a breeze
