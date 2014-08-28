'''
	@author Shashank Jaiswal
	@since 01-07-2014
	@version 0.0.0.1
	@description 
				Password generator using HMAC-SHA1
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


import urllib
from hashlib import sha1
import hmac
import binascii
import sys


def main(signingKey, signatureBaseString):
	'''
		Generate password ::
						signingKey:: key against which to encrypt data
						signatureBaseString:: data to be encrypted
		Read more at :: 
						How to implement HMAC-SHA1 algorithm :: <http://stackoverflow.com/questions/8338661/implementaion-hmac-sha1-in-python>

	'''
	hashed = hmac.new(signingKey, signatureBaseString, sha1);
	password = urllib.quote(binascii.b2a_base64(hashed.digest()).rstrip('\n'), '');
	
	return password;


	
if __name__=='__main__':
	if(len(sys.argv)==3):
		if((sys.argv[1].startswith('-base=') and sys.argv[2].startswith('-key=')) or (sys.argv[2].startswith('-base=') and sys.argv[1].startswith('-key='))):
			key = sys.argv[1];
			base = sys.argv[2];
			if(sys.argv[1].startswith('-base')):
				key = sys.argv[2];
				base = sys.argv[1];

			print(main(key.split('=')[1], base.split('=')[1]));
		else:
			print "script.py -key=xxxx -base=xxxx";
	else:
		print "script.py -key=xxxx -base=xxxx";
