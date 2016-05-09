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
    context = {}
    return render(request, 'data-collection/home.html', context)


@transaction.atomic
def storeGameLevelData(request):
	if request.method != 'POST':
		raise Http404

	#Get the data from the request
	print 'The unique user identification is: ' + request.POST['userName']
	print 'The Game Level is: ' + request.POST['currentLevel']
	print 'The number of Steps taken is: ' + request.POST['stepCount']
	print 'The number of Crashes: ' + request.POST['crashCount']
	print 'The time elapsed: ' + request.POST['timeElapsed']
	print 'The score obtained: ' + request.POST['score']
	print 'The encrypted string: ' + request.POST['testEncrypt']
	print 'The crash location data: ' + request.POST['crashLocations']

	#Open the private key pem file and read key
	fOpen = open('private.pem', 'r')
	privateKey = fOpen.read()

	#Decrypt the data
	rsakey = RSA.importKey(privateKey)
	
	#Decode the encrypted string using base64 encoding
	raw_cipher_data = b64decode(request.POST['testEncrypt'])

	#Decrypt the encrypted string using private key and RSA
	decrypted = rsakey.decrypt(raw_cipher_data)
	
	print 'The decrypted string: '
	print decrypted

	#Parse the crash location information
	echoLocsString = request.POST['crashLocations']
	echoLocs = []
	if echoLocsString != '':
		echoLocsString = echoLocsString.split(';')
		for echo in echoLocsString:
			indices = echo.split(',')

			newCrashLoc = CrashLocation(x=int(float(indices[0])),
						  				y=int(float(indices[1])),
						  				detail=indices[2])
			newCrashLoc.save()
			echoLocs.append(newCrashLoc)

	#Check if the user has played before, and has data saved previously
	user = UserGamePerformance.objects.filter(name=request.POST['userName'])
	if len(user) == 0:
		user = UserGamePerformance(name=request.POST['userName'])
		user.save()
	else:
		user = user[0]

	echoCount = 0
	echoFileNames = request.POST['echoFileNames'].split(',')
	for echoFile in echoFileNames:
		echo = echoFile.split(':')
		print 'Name of echo file played: ' + echo[0] + ', ' + 'Number of times played: ' + echo[1]
		echoCount = echoCount + int(echo[1])

	print 'Total number of echos played in this level: ' + str(echoCount)

	newGameLevel = GameLevel(level = int(request.POST['currentLevel']),
							 numSteps = int(request.POST['stepCount']),
							 numCrashes = int(request.POST['crashCount']),
							 echoFileNames = request.POST['echoFileNames'],
							 numEchoes = echoCount,
							 timeElapsed = int(request.POST['timeElapsed']),
							 score = int(request.POST['score']))
	newGameLevel.save()

	print "saved the game level without crash locations"

	if echoLocs != []:
		newGameLevel.crashLocs.add(*echoLocs)
		newGameLevel.save()

	print "saved the new game level"

	#Add the game to the user's games list
	user.games.add(newGameLevel)

	print "saved the game to the user's games"


	#Should create a new user if does not exist, at the start of the game. Make a request to another method
	#In this method, simply pull that user out, and add the new GameLevel object to his games attribute

	#context = {'testData': 'testValue'}

	#return JsonResponse({'testData': 'testValue'}, status=200)
	return HttpResponse("Success", status=200)

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


def getToken(request):

	#TODO: Need to figure out how to get CSRF token and send back
	#Just use JsonResponse on the context object to send back the JSON object with the token
	context = {}

	return HttpResponse("Success on the GET request", status=200)
