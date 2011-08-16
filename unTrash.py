from googlevoice import *
voice = Voice()
voice.login()

trash, msgs = voice.search('from:x in:Trash')

while (msgs.totalSize != 0):
    print msgs.totalSize
    for msg in msgs.messages:
        if msg.isTrash:
            msg.delete(0)
            
    trash, msgs = voice.search('from:x in:Trash')




