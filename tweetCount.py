'''
	@author Shashank Jaiswal
	@since 01-07-2014
	@version 0.0.0.1
	@warning Strictly for COMMON_CATHODE Only
	@description 
				Tweet counter using beaglebone black
				Author: Shashank Jaiswal <shashank_jaiswal@live.com>
				Copyright (c): 2014 Shashank Jaiswal, all rights reserved
				Version: 0.0.0.1

					 * This library is free software; you can redistribute it and/or
					 * modify it under the terms of the GNU Lesser General Public
					 * License as published by the Free Software Foundation; either
					 * version 2.1 of the License, or (at your option) any later version.
					 *
					 * This library is distributed in the hope that it will be useful,
					 * but WITHOUT ANY WARRANTY; without even the implied warranty of
					 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
					 * Lesser General Public License for more details.
					 *
					 * You should have received a copy of the GNU Lesser General Public
					 * License along with this library; if not, write to the Free Software
					 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

					You may contact the author at: shashank_jaiswal@live.com
'''


import urllib2
import json
import time
import base64
import urllib
from hashlib import sha1
import hmac
import binascii
import uuid


'''
	Global Variables::
		proxy_host : <your proxy server host>
		proxy_port : <your proxy server port>
		proxy_user : <your proxy server username>
		proxy_pass : <your proxy server password>
'''
proxy_host = "";
proxy_port = 0;
proxy_user = "";
proxy_pass = "";





def main():
	'''
		Proxy authentication
	'''
	proxy = urllib2.ProxyHandler({'https': 'http://'+proxy_user+':'+proxy_pass+'@'+proxy_host+':3128'})
	auth = urllib2.HTTPBasicAuthHandler()
	opener = urllib2.build_opener(proxy, auth, urllib2.HTTPHandler)




	'''Twitter authentication
		You can get the keys at <https://dev.twitter.com/console>
		Read more at:: <https://dev.twitter.com/docs/auth/authorizing-request>
					   Methods of obtaining oauth token:: <https://dev.twitter.com/docs/auth/obtaining-access-tokens>
					   How to obtain oauth token and secret for personal use:: <https://dev.twitter.com/docs/auth/tokens-devtwittercom>
			oauth_consumer_key:: Obtain at <https://dev.twitter.com/apps>
			oauth_signature_method:: "HMAC-SHA1" (Default used by twitter)
			oauth_timestamp= int(time.time())  (Time of making request)
			oauth_nonce = str(uuid.uuid4().hex) (Random alphanumeric string)
			oauth_version="1.0";               (Oauth version used by twitter)
			oauth_token :: 	Obtain at <https://dev.twitter.com/apps>
			oauth_token_secret :: Obtain at <https://dev.twitter.com/apps>	
	'''
	oauth_consumer_key = "uMtcFbG3tovhwgRT1c67jnekn";
	oauth_consumer_secret = "FNKqV4hvW6MOd3LILhjJuWbBAq4ee1CvppWPMdkD8vJiCxJJeO";
	oauth_signature_method="HMAC-SHA1";
	oauth_timestamp= str(int(time.time()));
	oauth_nonce= str(uuid.uuid4().hex);
	oauth_version="1.0";
	oauth_token = "2195509134-QUo6iQPxnNtoYF45xfCskosw7olHRZD5JGcAfZI";
	oauth_token_secret = "MO13kfSJ4N8j8eW8TwS7KKuI4S61fuSM1xASTwkJwdOwl";




	'''
		Generate oauth_signature ::
						url:: url from which to fetch the data
		Read more at :: 
						How to create signature ::   			<https://dev.twitter.com/docs/auth/creating-signature>
						How to percent encode url :: 			<http://stackoverflow.com/questions/1695183/how-to-percent-encode-url-parameters-in-python>
						How to implement HMAC-SHA1 algorithm :: <http://stackoverflow.com/questions/8338661/implementaion-hmac-sha1-in-python>

	'''
	url = "https://api.twitter.com/1.1/statuses/home_timeline.json"
	httpMethod = 'get';
	parameterString = 'oauth_consumer_key='+oauth_consumer_key+'&'+'oauth_nonce='+oauth_nonce+'&'+'oauth_signature_method='+oauth_signature_method+'&'+'oauth_timestamp='+oauth_timestamp+'&'+'oauth_token='+oauth_token+'&'+'oauth_version='+oauth_version;
	signatureBaseString = httpMethod.upper()+'&'+urllib.quote(url,'')+'&'+urllib.quote(parameterString);
	signingKey = urllib.quote(oauth_consumer_secret)+'&'+urllib.quote(oauth_token_secret);
	hashed = hmac.new(signingKey, signatureBaseString, sha1);
	oauth_signature = urllib.quote(binascii.b2a_base64(hashed.digest()).rstrip('\n'), '');
	

	'''
		Headers to be sent to <http://api.twitter.com>
		Read more at ::
						How to create authorization header::  <https://dev.twitter.com/docs/auth/authorizing-request>
	'''
	auth_header = '''OAuth oauth_consumer_key="'''+oauth_consumer_key+'''",oauth_signature_method="'''+oauth_signature_method+'''",oauth_timestamp="'''+oauth_timestamp+'''",oauth_nonce="'''+oauth_nonce+'''",oauth_version="'''+oauth_version+'''",oauth_token="'''+oauth_token+'''",oauth_signature="'''+oauth_signature+'''"''';
	user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1944.0 Safari/537.36'
	headers={'User-Agent':user_agent,'Authorization':auth_header} 





	'''
		Sending a GET request to twitter 
	'''
	request=urllib2.Request(url,None,headers) #The assembled request
	conn = opener.open(request);
	return_str = conn.read();    #contains your json data ... parse that to get the tweet count


	#print return_str
	f = open("json.json", "wb");
	f.write(return_str);
	f.close();

	data = json.loads(return_str);
	print len(data);
	return len(data);




def display(num):
	if(len(str(num)==2)):
		firstDigit = str(num)[0];
		secondDigit = str(num)[1];
		displayDigit(binaryRepresenation(firstDigit),1);
		displayDigit(binaryRepresenation(secondDigit),2);
	if(len(str(num)==1)):
		firstDigit = str(0);
		secondDigit = str(num)[0];
		displayDigit(binaryRepresenation(firstDigit),1);
		displayDigit(binaryRepresenation(secondDigit),2);





def displayDigit(binaryString, displayNum):
	pinSeries = "P8";
	if(displayNum==2):
		pinSeries = "P9";

	if len(binaryString==8):
		for i in range(8):
			pin = pinSeries + "_1" + str(i);
			if(binaryString[i]=='1'):
				GPIO.output(pin, GPIO.HIGH);
			elif(binaryString[i]=='0'):
				GPIO.output(pin, GPIO.LOW);






def binaryRepresenation(fDigit):
	'''
		0 abcdefg
		0 1111110 : 126 -> "0"
		0 0110000 :  96 -> "1"
		0 1101101 : 109 -> "2"
		0 1111001 : 121 -> "3"
		0 0110011 :  51 -> "4"
		0 1011011 :  91 -> "5"
		0 1011111 :  95 -> "6"
		0 1110000 : 112 -> "7"
		0 1111111 : 127 -> "8"
		0 1111011 : 123 -> "9"
	'''
	arr = [126,96,109,121,51,91,95,112,127,123];
	num_fDigit = int(fDigit);
	binaryRep = str(bin(arr[num_fDigit]))[2:].zfill(8);
	return binaryRep;




def mainLoop():
	import Adafruit_BBIO.GPIO as GPIO
	import time

	"First Seven Segment Display Pins"
	GPIO.setup("P8_10", GPIO.OUT);
	GPIO.setup("P8_11", GPIO.OUT);
	GPIO.setup("P8_12", GPIO.OUT);
	GPIO.setup("P8_13", GPIO.OUT);
	GPIO.setup("P8_14", GPIO.OUT);
	GPIO.setup("P8_15", GPIO.OUT);
	GPIO.setup("P8_16", GPIO.OUT);
	GPIO.setup("P8_17", GPIO.OUT);
	
	"Second Seven Segment Display Pins"
	GPIO.setup("P9_10", GPIO.OUT);
	GPIO.setup("P9_11", GPIO.OUT);
	GPIO.setup("P9_12", GPIO.OUT);
	GPIO.setup("P9_13", GPIO.OUT);
	GPIO.setup("P9_14", GPIO.OUT);
	GPIO.setup("P9_15", GPIO.OUT);
	GPIO.setup("P9_16", GPIO.OUT);
	GPIO.setup("P9_17", GPIO.OUT);

	while True:
		tweetCount = main();
		display(tweetCount);
		time.sleep(5);


	
if __name__=='__main__':
	main();

