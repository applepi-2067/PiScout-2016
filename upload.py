import os
import requests
import server
import serverinfo

n = 1
print("Attemting to upload matches...")
if os.path.isfile('queue.txt'):
	try:
    with open("queue.txt", "r") as file:
			for line in file:
				requests.post(serverinfo.server + "/submit", data={'event':server.CURRENT_EVENT, 'data': line, 'auth': serverinfo.AUTH})
				print("Uploaded entry number " + str(n))			
				n += 1
    os.remove('queue.txt')  
  except:
    print("Failed miserably. Are you connected to the internet?")
else:
	print("The match queue doesn't exist.")
  
n=0
if os.path.isfile('pitQueue.txt'):
	try:
    with open("pitQueue.txt", "r") as file:
			for line in file:
				requests.post(serverinfo.server + "/submit", data={'event':server.CURRENT_EVENT, 'pitData': line, 'auth': serverinfo.AUTH})
				print("Uploaded pit entry number " + str(n))			
				n += 1
    os.remove('pitQueue.txt')  
  except:
    print("Failed miserably. Are you connected to the internet?")
else:
	print("The pit queue doesn't exist.")
    
print("Finished.")
input("Press Enter to exit")
