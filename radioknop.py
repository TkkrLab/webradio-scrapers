import urllib.request, json, sys, time, socket

def sendCommand(cmd):
  global s
  try:
    print("SEND:",cmd)
    s.send(bytes(cmd+"\n", 'UTF-8'))
    time.sleep(0.1)
    print("RECV: ",s.recv(99999))
  except Exception as e:
    print("Error while sending command to MPD:",e)
    sys.exit(1)

try:
  req = urllib.request.Request(
    "https://www.radioknop.nl/api.php",
    data=None,
    headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    }
  )
  contents = urllib.request.urlopen(req)
except Exception as e:
  print("Error while getting data:",e)
  sys.exit(1)

try:
  data = json.load(contents)
except Exception as e:
  print("Error while decoding JSON:",e)
  sys.exit(1)

playlists = {}

for i in data:
  if not i['genre'] in playlists:
    playlists[i['genre']] = [];
  playlists[i['genre']].append(i)

try:
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect(('piratendoos.tkkrlab', 6600))
except Exception as e:
  print("Error while connecting to MPD:",e)
  sys.exit(1)
  
for i in playlists:
  sendCommand("playlistclear \"Radioknop - " + i + "\"")

for i in playlists:
  for j in playlists[i]:
    sendCommand("playlistadd \"Radioknop - " + i + "\" \"" + j['url']+"#"+j['name'] +"\"")

s.close()
