import youtube_dl
  
ydl = youtube_dl.YoutubeDL({
    #'format': 'video[height<=360,ext=mp4]'
    'format': '18'
})

with ydl:
    result = ydl.download(
        ['http://www.youtube.com/watch?v=_bN4spt3744']
    )

print(result)
