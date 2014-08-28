'''
	@author Shashank Jaiswal
	@since 01-07-2014
	@version 0.0.0.1
	@description 
				Downloads album-art for particular album/movie. Makes use of mediawiki-api
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

import os
import hashlib;
import sys;
import urllib2;
import urllib;
import json;
import re;

'''
	Global Variables::
		proxy_host : <your proxy server host>
		proxy_port : <your proxy server port>
		proxy_user : <your proxy server username>
		proxy_pass : <your proxy server password>
'''
proxy_host = "";
proxy_port = 80;
proxy_user = "";
proxy_pass = "";


def main(directory):
	'''
		Proxy authentication
	'''
	proxy = urllib2.ProxyHandler({'http': 'http://'+proxy_user+':'+proxy_pass+'@'+proxy_host+':3128'})
	auth = urllib2.HTTPBasicAuthHandler()
	opener = urllib2.build_opener(proxy, auth, urllib2.HTTPHandler)
	user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1944.0 Safari/537.36'
	headers={'User-Agent':user_agent,}
	
	if(directory=='--cwd'):
		directory = os.getcwd();

	if os.path.exists(directory):
		if os.path.isdir(directory):
			i = directory.split("\\")[-1];
			url = '';
			request = '';
			starContent = '';
			p = '';
			image_buffer = '';
			imageFilename = '';
			index = -1;
			counter = -1;
			image = [];
			try:
				url = "http://en.wikipedia.org/w/api.php?format=json&action=query&titles="+urllib.quote(i)+"&prop=pageimages&redirects";
				request=urllib2.Request(url,None,headers)
				p = json.loads(opener.open(request).read());
				try:
					starContent = p["query"]["pages"][str(p["query"]["pages"].keys()[0])]["pageimage"];
				except:
					pass;
				if(starContent):
					image = ['', starContent];
				else:
					#print "Hello";
					url = "http://en.wikipedia.org/w/api.php?format=json&action=query&titles="+urllib.quote(i)+"&prop=revisions&rvprop=content&redirects";
					request=urllib2.Request(url,None,headers)
					p = json.loads(opener.open(request).read());
					try:
						starContent = p["query"]["pages"][str(p["query"]["pages"].keys()[0])]["revisions"][0]["*"];
					except:
						pass;
					#print starContent;
					match = re.search('image.+jpg', starContent);
					if match:
						image = str(match.group()).split(" = ");
					else:
						#print "Hello";
						index = -1;
						counter = -1;
						for s2 in starContent.split("\n*"):
							#print counter, s2;
							counter += 1;
							match = re.search('film', s2);
							if(match):
								index = counter;
						link = starContent.split("\n*")[index];
						#print link;
						match = re.search('\[\[.+\]\]', link);
						if match:
							filename = match.group();
							filename = filename.split('|')[0];
							filename = filename.replace('[[', '');
							filename = filename.replace(']]', '');
						try:
							url = "http://en.wikipedia.org/w/api.php?format=json&action=query&titles="+urllib.quote(filename)+"&prop=revisions&rvprop=content&redirects";
							request=urllib2.Request(url,None,headers)
							p2 = json.loads(opener.open(request).read());
						
							starContent = p2["query"]["pages"][str(p2["query"]["pages"].keys()[0])]["revisions"][0]["*"];
							match = re.search('image.+jpg', starContent);
							if match:
								image = str(match.group()).split(" = ");
						except:
							image = [''];

				if(len(image)==2):
					imageFilename = image[1].replace(' ', '_');
					digest = str(hashlib.md5(imageFilename).hexdigest());
					folder = digest[0] + '/' + digest[:2] + '/' + urllib.quote(imageFilename);
					url = 'http://upload.wikimedia.org/wikipedia/en/' + folder;
					try:
						request=urllib2.Request(url,None,headers)
						image_buffer = opener.open(request).read();
					except:
						url = 'http://upload.wikimedia.org/wikipedia/commons/' + folder;
						request=urllib2.Request(url,None,headers)
						image_buffer = opener.open(request).read();
					
					print url;
					d = os.getcwd();
					os.chdir(directory);
					f = open(i+'.jpg','wb')
					f.write(image_buffer);
					f.close();
					os.chdir(d);
			except:
				pass;
				


if __name__ == '__main__':
	if(len(sys.argv)==2):
		if(sys.argv[1].startswith('-dir=')):
			main(sys.argv[1].split('=')[1]);
		else:
			print 'Usage:: script.py -dir=fullDirectoryPath';
	else:
		print 'Usage:: script.py -dir=fullDirectoryPath'
