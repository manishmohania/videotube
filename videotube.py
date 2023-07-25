from tkinter import tix
from tkinter import font
from tkinter.constants import *
import urllib.request
from PIL import Image
from PIL import ImageTk
import io
import json
import subprocess


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


def cmdSearchBtnClicked(keyword = None) :
    searchKey = txtSearch.get()
    
    if (len(searchKey) == 0):
        strStatus.set("No search keyword specified.")
        return

    videosListObj.clear()
    lstVideos.delete(0, END)
    key = urllib.parse.quote(searchKey, safe='')
    urlRequest = urllib.request.urlopen("https://youtube.googleapis.com/youtube/v3/search?type=video&fields=items(id/videoId)&maxResults=25&q="+key+"&key="+YOUR_API_KEY);
    strJson = urlRequest.read()
    
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
    print(viList);


    strURL = "https://www.googleapis.com/youtube/v3/videos?id="+viList+"&part=snippet,statistics,contentDetails&fields=items(id,snippet(title,thumbnails/medium),contentDetails,statistics)&key="+YOUR_API_KEY

    urlRequestStats = urllib.request.urlopen(strURL)
    print(strURL)
    strJson = urlRequestStats.read()
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
            likeCount = i['statistics']['likeCount']
        except:
            likeCount = 0

        try :
            viewCount = i['statistics']['viewCount']
        except:
            viewCount =0

        try :
            vdf = i['contentDetails']['duration']
        except:
            vdf = "Not Known"
        
        
        vItem = VideoItem(videoId, strTitle, tkimgThumbnail, likeCount)

        
        vi = len(videosListObj)
        videosListObj.append(vItem)
        
        
        frmVideoItem = tix.Frame(lstVideos)
        frmVideoItem.bind("<Button-1>", lambda e, lvi= vi : selectVideoItem(lvi))
        frmVideoItem.bind("<Double-Button-1>", lambda e, lvi= vi : cmdVideoSelected(lvi))
        
        lblVideoImg = tix.Label(frmVideoItem, image=tkimgThumbnail)
        lblVideoImg.pack(side=LEFT)
        lblVideoImg.bind("<Button-1>", lambda e, lvi = vi : selectVideoItem(lvi))
        lblVideoImg.bind("<Double-Button-1>", lambda e, lvi = vi : cmdVideoSelected(lvi))

        btnDownload = tix.Button(frmVideoItem, image=downloadImage, command= lambda lvi= vi : cmdDownloadBtnClicked(lvi))
        btnDownload.pack(side=RIGHT, fill="y", expand=True)

        
        msgVideoTitle = tix.Message(frmVideoItem, text=strTitle, width=350)
        
        
        msgVideoTitle.bind("<Button-1>", lambda e, lvi= vi : selectVideoItem(lvi))
        msgVideoTitle.bind("<Double-Button-1>", lambda e, lvi= vi : cmdVideoSelected(lvi))
        msgVideoTitle.pack(side=TOP, expand=True, fill="y")

        lblDuration = tix.Label(frmVideoItem, image=durationImage, text=str(vdf), compound=LEFT)
        lblDuration.bind("<Button-1>", lambda e, lvi= vi : selectVideoItem(lvi))
        lblDuration.bind("<Double-Button-1>", lambda e, lvi= vi : cmdVideoSelected(lvi))
        lblDuration.pack(side=LEFT)

        lblViews = tix.Label(frmVideoItem, image=viewImage, text=str(viewCount), compound=LEFT)
        lblViews.bind("<Button-1>", lambda e, lvi= vi : selectVideoItem(lvi))
        lblViews.bind("<Double-Button-1>", lambda e, lvi= vi : cmdVideoSelected(lvi))
        lblViews.pack(side=LEFT)
        
        lblLike = tix.Label(frmVideoItem, image=likeImage, text=str(likeCount), compound=LEFT)
        lblLike.bind("<Button-1>", lambda e, lvi= vi : selectVideoItem(lvi))
        lblLike.bind("<Double-Button-1>", lambda e, lvi= vi : cmdVideoSelected(lvi))
        lblLike.pack(side=LEFT)


        lstVideos.insert(END,  itemtype="window", window=frmVideoItem)

def cmdVideoSelected(str_selected_index) :
    selectedIndex = int(str_selected_index)
    print(selectedIndex)
    if int(selectedIndex) < 0 :
        return
    v = videosListObj[selectedIndex]
    subprocess.run(["mpv", "--ytdl-format=best", "https://youtube.com/watch?v="+v.videoId ])
    
def cmdDownloadBtnClicked(str_selected_index) :
    selectedIndex = int(str_selected_index)
    print(selectedIndex)
    if int(selectedIndex) < 0 :
        return
    v = videosListObj[selectedIndex]
    subprocess.run(["yt-dlp", "-f", "22/best", "https://youtube.com/watch?v="+v.videoId ])


YOUR_API_KEY='PASTE_YOUR_YOUTUBE_API_KEY_HERE'

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
xScrollbar.config( command = lstVideos.xview )

root.mainloop()
