from django.shortcuts import render, redirect, get_object_or_404

# Django transaction system so we can use @transaction.atomic
from django.db import transaction

from django.http import HttpResponse, Http404, JsonResponse

from models import *

from django.core.exceptions import ObjectDoesNotExist

from Crypto.PublicKey import RSA
from base64 import b64decode

@transaction.atomic
def home(request):
	'''Renders a static homepage for the server'''
	context = {}
	return render(request, 'data-collection/home.html', context)


@transaction.atomic
def storeGameLevelData(request):
	'''Stores game data from the app for a single attempt at any level into
	the centralized server database.

	Currently, the following data is being sent from the app to be stored
	(the name of the key in the POST request is listed in brackets): 
	 - Username (userName)
	 - Current Level (currentLevel)
	 - Number of Crashes (crashCount)
	 - Number of Steps (stepCount)
	 - Time taken to complete level (timeElapsed)
	 - Score in game level (score)
	 - Coordinates and English representation of crash locations (crashLocations)
	 - File names of the echoes played and number of times played (echoFileNames)
	 '''
	if request.method != 'POST':
		raise Http404

	#Decrypt the encrypted string using private key and RSA
	decrypted = decryptData(request.POST['testEncrypt'])	#For test purposes

	#Parse the crash location information
	echoLocs = parseCrashLocs(request.POST['crashLocations'])

	#Get total echo count and print each echo details
	echoCount = parseEchoFileNames(request.POST['echoFileNames'])

	#Get the data from the request and print (For debugging/testing). Comment if necessary.
	printData(request, echoCount)

	#Save all data besides crash locations
	newGameLevel = GameLevel(level = int(request.POST['currentLevel']),
							 numSteps = int(request.POST['stepCount']),
							 numCrashes = int(request.POST['crashCount']),
							 echoFileNames = request.POST['echoFileNames'],
							 numEchoes = echoCount,
							 timeElapsed = int(request.POST['timeElapsed']),
							 score = int(request.POST['score']))
	newGameLevel.save()

	#Save the crash locations
	if echoLocs != []:
		newGameLevel.crashLocs.add(*echoLocs)
		newGameLevel.save()

	#Check if the user has played before, and has data saved previously
	user = UserGamePerformance.objects.filter(name=request.POST['userName'])
	if len(user) == 0:
		user = UserGamePerformance(name=request.POST['userName'])
		user.save()
	else:
		user = user[0]

	#Add the game to the user's games list
	user.games.add(newGameLevel)

	return HttpResponse("Success", status=200)

def decryptData(data):
	'''Decrypts an encrypted input string sent from the app using the
	RSA cryptosystem's corresponding private key'''
	#Open the private key pem file and read key
	fOpen = open('private.pem', 'r')
	privateKey = fOpen.read()

	#Import the private key
	rsakey = RSA.importKey(privateKey)
	
	#Decode the encrypted string using base64 encoding
	raw_cipher_data = b64decode(data)

	#Decrypt the encrypted string using private key and RSA
	decrypted = rsakey.decrypt(raw_cipher_data)

	return decrypted

def parseCrashLocs(data):
	'''Parses the POST request input of the crash locations into a format
	to be stored in the database models'''
	echoLocs = []
	if data != '':
		echoLocsString = data.split(';')
		for echo in echoLocsString:
			indices = echo.split(',')

			newCrashLoc = CrashLocation(x=int(float(indices[0])),
						  				y=int(float(indices[1])),
						  				detail=indices[2])
			newCrashLoc.save()
			echoLocs.append(newCrashLoc)

	return echoLocs

def parseEchoFileNames(data):
	'''Parses and prints name of echoes played and number of times they were
	played. Returns the total number of times all echoes were played.'''
	echoCount = 0
	echoFileNames = data.split(',')
	for echoFile in echoFileNames:
		echo = echoFile.split(':')
		#Print details
		print 'Name of echo file played: ' + echo[0] + ', ' + 'Number of times played: ' + echo[1]
		echoCount = echoCount + int(echo[1])

	return echoCount


def generate_RSA(bits=2048):
    '''
    Generate an RSA keypair with an exponent of 65537 in PEM format
    param: bits The key length in bits
    Return private key and public key
    '''
    new_key = RSA.generate(bits, e=65537) 
    public_key = new_key.publickey().exportKey("PEM") 
    private_key = new_key.exportKey("PEM") 
    print public_key
    print private_key
    #return private_key, public_key
    return

def getPublicKey(request):
	context ={}
	fOpen = open('public.pem', 'r')

	publickey = fOpen.read().replace('\n', '')

	context['key'] = publickey

	return JsonResponse(context, status=200)

def printData(request, echoCount):
	'''Prints the request and parsed data for debugging/testing'''
	print 'The unique user identification is: ' + request.POST['userName']
	print 'The Game Level is: ' + request.POST['currentLevel']
	print 'The number of Steps taken is: ' + request.POST['stepCount']
	print 'The number of Crashes: ' + request.POST['crashCount']
	print 'The time elapsed: ' + request.POST['timeElapsed']
	print 'The score obtained: ' + request.POST['score']
	print 'The encrypted string: ' + request.POST['testEncrypt']
	print 'The crash location data: ' + request.POST['crashLocations']
	print 'Total number of echos played in this level: ' + str(echoCount)
