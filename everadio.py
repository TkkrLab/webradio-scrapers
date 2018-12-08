import urllib.request, json, sys, time, socket
from html.parser import HTMLParser

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
    "http://eve-radio.com/radio/rewind",
    data=None,
    headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    }
  )
  contents = urllib.request.urlopen(req)
except Exception as e:
  print("Error while getting data:",e)
  sys.exit(1)

data = []

class MyHTMLParser(HTMLParser):
    in_erRw = False
    field_counter = 0
    field_depth = 0
    link_counter = 0

    item = {}
      
    def handle_starttag(self, tag, attrs):
        is_div = False
        if (tag=="div"):
          is_div = True
          is_erRW = False
          for i in attrs:
            if (i[0] == 'id'):
              if (i[1] == 'erRW'):
                is_erRW = True

          if (is_erRW):
            if (self.in_erRw):
              print("HTML parser error: encountered erRW start while in block.")
              sys.exit(1)
            self.in_erRw = True
            self.field_counter = 0
            self.field_depth = 0
            self.link_counter = 0
            self.item = {}
          elif (is_div):
            self.field_counter += 1
            self.field_depth += 1

        if (tag=="a"):
          if (self.field_counter == 4):
            if (self.link_counter < 1):
              for i in attrs:
                if (i[0] == 'onclick'):
                  self.item['link'] = i[1].split("'")[1].rstrip('\n').rstrip('\r')

            self.link_counter += 1

    def handle_endtag(self, tag):
        is_div = False
        if (tag=="div"):
          if (self.field_depth >= 0):
            self.field_depth -= 1
          if (self.field_depth < 0):
            self.in_erRw = False
            global data
            data.append(self.item)
     

    def handle_data(self, data):
        if (self.in_erRw):
          if (self.field_counter==1):
            self.item['dj'] = data.rstrip('\n').rstrip('\r')
          if (self.field_counter==2):
            self.item['time'] = data.rstrip('\n').rstrip('\r')
          if (self.field_counter==3):
            self.item['date'] = data.rstrip('\n').rstrip('\r')

parser = MyHTMLParser()

parser.feed(contents.read().decode("utf-8"))

#print(data)

try:
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect(('piratendoos.tkkrlab', 6600))
except Exception as e:
  print("Error while connecting to MPD:",e)
  sys.exit(1)

sendCommand("playlistclear \"EVE-Radio Rewind\"")

for i in data:
  sendCommand("playlistadd \"EVE-Radio Rewind\" \"" + i['link']+"#"+i['dj']+" "+i['time']+" "+i['date'] +"\"")

s.close()
