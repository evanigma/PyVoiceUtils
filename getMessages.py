from googlevoice import Voice
import sys
import urllib2
import BeautifulSoup

class Txt(object):  
    def unescape(self, s):
        s = s.replace("&lt;", "<")
        s = s.replace("&gt;", ">")

        s = s.replace("&amp;", "&")
        return s
        
    def __init__(self, name, time, text):
        self.name = name.split(' ')[0].strip(':')
        self.time = time
        self.text = self.unescape(text)

class Convo(object):    
    def __init__(self, msg):
        self.startTime = msg.displayStartDateTime
        self.phoneNumber = msg.phoneNumber
        self.txts = []
        
    def __cmp__(self, other):
        return cmp(self.startTime, other.startTime)
        
    def addText(self, txt):
        if (len(self.txts) != 0 and len(self.txts[-1].text) >= 153 and self.txts[-1].time == txt.time):
            self.txts[-1].text += txt.text
        else:
            self.txts.append(txt)
        
    #def __str__(self):
    def printMe(self):          
        print self.startTime
        
        i = 0
        while i < len(self.txts) and self.txts[i].name == 'Me':
            i += 1
        
        if i != len(self.txts):
            nameLength = len(self.txts[i].name)
        else:
            nameLength = 5
            
        format = '%8s: %'+str(nameLength)+'s: %s'
        
        for txt in self.txts:
            try:
                print format % (txt.time, txt.name, txt.text)
            except UnicodeEncodeError, e:
                txt.text = ''.join([x for x in txt.text if ord(x) < 128])
                print format % (txt.time, txt.name, txt.text)

#This function written by:
#John Nagle
#   nagle@animats.com
#
def extractsms(htmlsms) :
    """
    extractsms  --  extract SMS messages from BeautifulSoup tree of Google Voice SMS HTML.

    Output is a list of dictionaries, one per message.
    """
    msgitems = []										# accum message items here
    #	Extract all conversations by searching for a DIV with an ID at top level.
    tree = BeautifulSoup.BeautifulSoup(htmlsms)			# parse HTML into tree
    conversations = tree.findAll("div",attrs={"id" : True},recursive=False)
    for conversation in conversations :
        #	For each conversation, extract each row, which is one SMS message.
        rows = conversation.findAll(attrs={"class" : "gc-message-sms-row"})
        for row in rows :								# for all rows
            #	For each row, which is one message, extract all the fields.
            msgitem = {"id" : conversation["id"]}		# tag this message with conversation ID
            spans = row.findAll("span",attrs={"class" : True}, recursive=False)
            for span in spans :							# for all spans in row
                cl = span["class"].replace('gc-message-sms-', '')
                msgitem[cl] = (" ".join(span.findAll(text=True))).strip()	# put text in dict
            msgitems.append(msgitem)					# add msg dictionary to list
    return msgitems
    
voice = Voice()
voice.login()

try:

    convos = {}

    html, messageData = voice.search('from:x -in:Trash')

    while (messageData.totalSize != 0):    
        messages = extractsms(html)

        for msg in messageData.messages:
            convos[msg.id] = Convo(msg)
            
        for msg in messages:
            convos[msg['id']].addText(Txt(msg['from'],msg['time'], msg['text']))
            
        for msg in messageData.messages:
            msg.delete()
            
        html, messageData = voice.search('from:x -in:Trash')
    
except: pass

for convo in sorted(convos.values()):
    convo.printMe()
    print ""


