from tkinter import tix
from tkinter import font
from tkinter.constants import *
import urllib.request
from PIL import Image
from PIL import ImageTk
import io
import json
import subprocess
import threading
import time


class VideoItem :
    def __init__(self, videoId, title, imgThumbnail, likeCount):
        self.videoId=videoId
        self.title=title
        self.imgThumbnail = imgThumbnail
        self.likeCount = likeCount

def selectVideoItem(i) :
    lstVideos.focus_set()
    lstVideos.selection_clear()
    lstVideos.selection_set(i)

def strCount(icnt) :
    cnt = int(icnt)
    if (int(cnt / (100 * 10 * 100000)) > 0) :
        return "100M+"
    elif (int(cnt / (10 * 10 * 100000)) > 0) :
        return "10M+"
    elif (int(cnt / (1 * 10 * 100000)) > 0) :
        return "1M+"
    elif (int(cnt / (100 * 1000)) > 0) :
        return "100K+"
    elif (int(cnt/ (10 * 1000)) > 0) :
        return "10K+"
    else :
        return str(cnt)

def hDuration(tDuration) :
    h = ''
    for c in tDuration :
        if (c == 'P' or c == 'T') :
            continue
        elif (c == 'D' or c == 'H' or c == 'M' or c == 'S') :
            h = h + c + ' '
        else :
            h = h + c

    return h


def cmdSearchBtnClicked(e = None) :
    searchKey = txtSearch.get()
    
    if (len(searchKey) == 0):
        lblStatusStringVar.set("No search keyword specified.")
        return

    t = threading.Thread(target=searchVideo, args=(searchKey,))
    t.start()

def searchVideo(searchKey) :
    lblStatusStringVar.set("Searching for videos by keyword: " + searchKey)
    try :
        videosListObj.clear()
        lstVideos.delete(0, END)
        key = urllib.parse.quote(searchKey, safe='')
        vURL = "https://youtube.googleapis.com/youtube/v3/search?type=video&fields=items(id/videoId)&maxResults=25&q="+key+"&key="+YOUR_API_KEY
        lblStatusStringVar.set("Requesting URL: " + vURL)
        urlRequest = urllib.request.urlopen(vURL)
        strJson = urlRequest.read()
        lblStatusStringVar.set("Request Complete.")
        
        jsonObj = json.loads(strJson)

        videoIdList = []
        for i in jsonObj['items']:
            try :
                videoIdList.append(i['id']['videoId'])
            except:
                continue;

        if (len(videoIdList) <= 0) :
            return;

        viList = ",".join(videoIdList)
        quotedViList = urllib.parse.quote(viList, safe='')

        strURL = "https://www.googleapis.com/youtube/v3/videos?id="+quotedViList+"&part=snippet,statistics,contentDetails&fields=items(id,snippet(title,thumbnails/medium),contentDetails,statistics)&key="+YOUR_API_KEY
        lblStatusStringVar.set("Requesting URL: " + strURL)
        
        urlRequestStats = urllib.request.urlopen(strURL)
        strJson = urlRequestStats.read()
        lblStatusStringVar.set("Request Complete. Will now render video thumbnails with statistics and controls")
        jsonObj = json.loads(strJson)
        for i in jsonObj['items']:
            try :
                videoId = i['id']
            except:
                continue;

            strThumbnail = i['snippet']['thumbnails']['medium']['url']
            strTitle = i['snippet']['title']
            
            urlThumbnail = urllib.request.urlopen(strThumbnail)
            pimgThumbnail = Image.open(io.BytesIO(urlThumbnail.read()))
            tkimgThumbnail = ImageTk.PhotoImage(pimgThumbnail)

            try :
                likeCount = strCount(i['statistics']['likeCount'])
            except:
                likeCount = 0

            try :
                viewCount = strCount(i['statistics']['viewCount'])
            except:
                viewCount =0

            try :
                vdf = hDuration(i['contentDetails']['duration'])
            except:
                vdf = "Not Known"
            
            
            vItem = VideoItem(videoId, strTitle, tkimgThumbnail, likeCount)

            
            vi = len(videosListObj)
            videosListObj.append(vItem)
            
            
            frmVideoItem = tix.Frame(lstVideos, width="800")
            frmVideoItem.bind("<Button-1>", lambda e, lvi= vi : selectVideoItem(lvi))
            frmVideoItem.bind("<Double-Button-1>", lambda e, lvi= vi : cmdVideoSelected(lvi))
            
            lblVideoImg = tix.Label(frmVideoItem, image=tkimgThumbnail)
            lblVideoImg.pack(side=LEFT)
            lblVideoImg.bind("<Button-1>", lambda e, lvi = vi : selectVideoItem(lvi))
            lblVideoImg.bind("<Double-Button-1>", lambda e, lvi = vi : cmdVideoSelected(lvi))

            frmStats = tix.Frame(frmVideoItem)
            lblDuration = tix.Label(frmStats, image=durationImage, text=str(vdf), compound=LEFT)
            lblDuration.bind("<Button-1>", lambda e, lvi= vi : selectVideoItem(lvi))
            lblDuration.bind("<Double-Button-1>", lambda e, lvi= vi : cmdVideoSelected(lvi))
            lblDuration.pack(side=LEFT)

            lblViews = tix.Label(frmStats, image=viewImage, text=str(viewCount), compound=LEFT)
            lblViews.bind("<Button-1>", lambda e, lvi= vi : selectVideoItem(lvi))
            lblViews.bind("<Double-Button-1>", lambda e, lvi= vi : cmdVideoSelected(lvi))
            lblViews.pack(side=LEFT)
            
            lblLike = tix.Label(frmStats, image=likeImage, text=str(likeCount), compound=LEFT)
            lblLike.bind("<Button-1>", lambda e, lvi= vi : selectVideoItem(lvi))
            lblLike.bind("<Double-Button-1>", lambda e, lvi= vi : cmdVideoSelected(lvi))
            lblLike.pack(side=LEFT)
            frmStats.pack(side=BOTTOM)
            
            btnDownload = tix.Button(frmVideoItem, image=downloadImage, command= lambda lvi= vi : cmdDownloadBtnClicked(lvi))
            btnDownload.pack(side=LEFT, fill="y", expand=True)

            
            msgVideoTitle = tix.Message(frmVideoItem, text=strTitle, width=220)
            
            msgVideoTitle.bind("<Button-1>", lambda e, lvi= vi : selectVideoItem(lvi))
            msgVideoTitle.bind("<Double-Button-1>", lambda e, lvi= vi : cmdVideoSelected(lvi))
            msgVideoTitle.pack(side=LEFT )

            lstVideos.insert(END,  itemtype="window", window=frmVideoItem)
            lblStatusStringVar.set("Rendering Complete.. ")
            lblStatusStringVar.set("Search completed. Double click on video to play video.")
    except Exception as error:
            lblStatusStringVar.set("Search Failed with errors ..")
            print("An error occurred: ", error)

def xMoveTo(op, number, what=None) :
    if (op=="moveto") :
        lstVideos.xview(op, number)
    elif (op=="scroll") :
        lstVideos.xview(op, number, "units")

def playVideo (v) :
    lblStatusStringVar.set("Playing video: "+v.title)
    try :
        qvid = urllib.parse.quote(v.videoId, safe='')
        subprocess.run(["mpv", "--ytdl-format=best", "https://youtube.com/watch?v="+qvid ])
        lblStatusStringVar.set("Video Playback Complete..")
    except Exception as error:
        lblStatusStringVar.set("Video Playback Completed with errors..")
        print("An error occurred", error)
    
def cmdVideoSelected(str_selected_index) :
    selectedIndex = int(str_selected_index)
    if int(selectedIndex) < 0 :
        return
    v = videosListObj[selectedIndex]

    t = threading.Thread(target=playVideo, args=(v,))
    t.start()

def downloadVideo (v) :
    lblStatusStringVar.set("Downloading video: "+v.title)
    try :
        qvid = urllib.parse.quote(v.videoId, safe='')
        subprocess.run(["yt-dlp", "-f", "bv*[height<=720]+ba/b[height<=720] / wv*+ba/w", "https://youtube.com/watch?v="+qvid ])
        lblStatusStringVar.set("Video download complete")
    except Exception as error:
        lblStatusStringVar.set("Video download completed with errors..")
        print("An error occurred", error)
    
def cmdDownloadBtnClicked(str_selected_index) :
    selectedIndex = int(str_selected_index)
    if int(selectedIndex) < 0 :
        return
    v = videosListObj[selectedIndex]
    
    t = threading.Thread(target=downloadVideo, args=(v,))
    t.start()
    

YOUR_API_KEY='PASTE_YOUR_API_KEY_HERE'

videosListObj = []

root = tix.Tk()
root.tk.eval('package require Tix')
root.geometry("700x550")

likeImage=tix.PhotoImage(file="images/like_50_50.png")
viewImage=tix.PhotoImage(file="images/views_50_50.png")
durationImage=tix.PhotoImage(file="images/duration_50_50.png")
downloadImage=tix.PhotoImage(file="images/download_50_50.png")

defaultFont = font.nametofont("TkDefaultFont")
defaultFont.configure(size=defaultFont.cget("size")+2)

lblfrmSearch = tix.LabelFrame(root, {"label" : "Enter the keyword to search for youtube videos"})

frmSearch= lblfrmSearch.subwidget(name="frame");

txtSearch = tix.Entry(frmSearch, width=60)


entryDefaultFont = font.nametofont(txtSearch.cget("font"))
entryDefaultFont.configure(size=entryDefaultFont.cget("size")+2)

txtSearch.bind("<Return>", cmdSearchBtnClicked)
txtSearch.focus_set()
btnSearch = tix.Button(frmSearch, text="Search", command=cmdSearchBtnClicked);
txtSearch.pack(side=LEFT)
btnSearch.pack()

lblfrmSearch.pack()

xScrollbar = tix.Scrollbar(root, orient=HORIZONTAL)
xScrollbar.pack(side=BOTTOM, fill="x")

lstVideos = tix.TList(root, command=cmdVideoSelected,  xscrollcommand=xScrollbar.set)
lstVideos.pack(expand="yes", fill="both")
xScrollbar.config( command = xMoveTo )

lblStatusStringVar = tix.StringVar()
lblStatusStringVar.set("Enter the keyword to search for youtube videos")
lblStatus = tix.Label(root,  textvariable=lblStatusStringVar)
lblStatus.pack()

root.mainloop()
