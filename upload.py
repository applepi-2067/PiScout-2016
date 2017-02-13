import os
import requests
import server

n = 1
print("Attemting to upload matches...")
if os.path.isfile('queue.txt'):
	with open("queue.txt", "r") as file:
		try:
			for line in file:
				requests.post("http://34.199.157.169/submit", data={'event':server.CURRENT_EVENT, 'data': line})
				print("Uploaded entry number " + str(n))			
				n += 1
		except:
			print("Failed miserably. Are you connected to the internet?")
	os.remove('queue.txt')
else:
	print("The match queue doesn't exist.")
print("Finished.")
input("Press Enter to exit")
