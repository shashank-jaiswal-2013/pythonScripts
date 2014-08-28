'''
	@author Shashank Jaiswal
	@since 01-07-2014
	@version 0.0.0.1
	@description 
				This module builds on BaseHTTPServer by implementing the
				standard GET and HEAD requests.

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


__version__ = "0.1"

__all__ = ["basicHTTPRequestHandler"]

import os
import posixpath
import BaseHTTPServer
import urllib
import cgi
import sys
import shutil
import mimetypes
from hurry.filesize import size
from mutagen import File
import base64
import time

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class basicHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    """basic HTTP request handler with GET and HEAD commands.

    This serves files from the current directory and any of its
    subdirectories.  The MIME type for files is determined by
    calling the .guess_type() method.

    The GET and HEAD requests are identical except that the HEAD
    request omits the actual contents of the file.

    """

    server_version = "basicHTTP/" + __version__

    def do_GET(self):
        """Serve a GET request."""
        f = self.send_head()
        if f:
            self.copyfile(f, self.wfile)
            f.close()

    def do_HEAD(self):
        """Serve a HEAD request."""
        f = self.send_head()
        if f:
            f.close()

    def send_head(self):
        """Common code for GET and HEAD commands.

        This sends the response code and MIME headers.

        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.

        """
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            if not self.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                return self.list_directory(path)
        ctype = self.guess_type(path)
        try:
            # Always read in binary mode. Opening files in text mode may cause
            # newline translations, making the actual size of the content
            # transmitted *less* than the content-length!
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None
        self.send_response(200)
        self.send_header("Content-type", ctype)
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f

    def list_directory(self, path):
        """Helper to produce a directory listing (absent index.html).

        Return value is either a file object, or None (indicating an
        error).  In either case, the headers are sent, making the
        interface the same as for send_head().

        """
        try:
            list = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None
        list.sort(key=lambda a: a.lower())
        f = StringIO()
        displaypath = cgi.escape(urllib.unquote(self.path))
        f.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write("<html>\n<meta name='author' content='Shashank Jaiswal'/>\n<title>Directory listing for %s</title>\n" % displaypath)
        f.write("<style>body{ font-family:Helvetica, sans-serif;font-style:italic;font-size:12px;}li{font-style:italic;list-style:square;margin:10px;background-color:whitesmoke;padding:10px;}li:nth-child(even) { background: white; }a{color:#333;text-decoration:none;}#fileOpen{color:#222;font-style:bold;float:right;}#fileSize{color:#222;font-style:bold;float:right;min-width:50px;background-color:#FACFD4;border-radius:5px;margin-right:10px;text-align:center;padding: 4px 0px; margin-top: -4px;}#fileType{color:#222;font-style:bold;float:right;min-width:50px;background-color:#B6F1F1;border-radius:5px;margin-right:10px;text-align:center;padding: 3px 0px; margin-top: -3px;}#fileModifiedTime{color:#222;font-style:bold;float:right;min-width:150px;background-color:#AEE4FF;border-radius:5px;margin-right:10px;text-align:center;padding: 2px 0px; margin-top: -2px;}details div{margin-left:40px;height:340px;} details summary:focus{outline:0;}#image{float:right;margin-top:-40px;width:300px;height:300px;background-repeat:no-repeat;background-size:300px 100%;outline: 3px solid #727272;outline-offset:1px;}</style>");
        f.write("<body>\n<h2>Directory listing for %s</h2>\n" % displaypath)
        #f.write("<body>\n<h2>Directory listing for %s</h2><span id='fileOpen'><audio controls><source id='aaa' src='' type='audio/mpeg'>Your browser does not support the audio element.</audio></span>\n" % displaypath)
        #f.write("<script>function doThis(fileUrl){console.log(fileUrl);if(fileUrl.lastIndexOf('.mp3')==3){document.getElementById('aaa').src=fileUrl;}}</script>");
        f.write("<hr>\n<ul>\n")
        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            
            fsize = "";
            fileInfo = "";
            fileOpen = "";
            fileType = "";
            fileModifiedTime = "";

            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
                fsize = "";
            else:
                fsize = "<span id='fileSize'>"+str(size(os.path.getsize(fullname)))+"</span>";
                fileType = "<span id='fileType'>"+os.path.splitext(fullname)[1]+"</span>";
                fileModifiedTime = "<span id='fileModifiedTime'>"+time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(fullname)))+"</span>";
                mm = self.fileInformation(fullname);
                if not (mm=="" or mm=="<b>Mp3 Tags::</b><br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Title: <br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Album: <br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Artist: <br><div id='image' style='background-image:url(data:image/jpg;base64,)'></div>"):
                    fileInfo = "<div>"+ mm + "</div>";

            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            f.write('''<li><details><summary><a href='%s'>%s</a>%s %s %s</summary>%s</details>\n''' % (urllib.quote(linkname), cgi.escape(displayname), fsize, fileType, fileModifiedTime, fileInfo));
        f.write("</ul>\n<hr>\n</body>\n</html>\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        encoding = sys.getfilesystemencoding()
        self.send_header("Content-type", "text/html; charset=%s" % encoding)
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f


    def fileInformation(self, fullname):
        stringToReturn = "";
        if(fullname.endswith('.mp3')):
            file = File(fullname)
            artwork = "";
            title = "";
            album = "";
            artist = "";
            if file.tags:
                if file.tags.has_key('APIC:'):
                    artwork = file.tags['APIC:'].data
                if file.tags.has_key('TIT2'):
                    title = file.tags['TIT2'].text[0]
                if file.tags.has_key('TPE1'):
                    artist = file.tags['TPE1'].text[0]
                if file.tags.has_key('TALB'):
                    album = file.tags['TALB'].text[0]
            stringToReturn += "<b>Mp3 Tags::</b><br>";
            stringToReturn += "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Title: "+str(title)+"<br>";
            stringToReturn += "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Album: "+str(album)+"<br>";
            stringToReturn += "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Artist: "+str(artist)+"<br>";
            stringToReturn += "<div id='image' style='background-image:url(data:image/jpg;base64,"+base64.b64encode(artwork)+")'></div>"
        return stringToReturn;

    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.

        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)

        """
        # abandon query parameters
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        path = posixpath.normpath(urllib.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = os.getcwd()
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        return path

    def copyfile(self, source, outputfile):
        """Copy all data between two file objects.

        The SOURCE argument is a file object open for reading
        (or anything with a read() method) and the DESTINATION
        argument is a file object open for writing (or
        anything with a write() method).

        The only reason for overriding this would be to change
        the block size or perhaps to replace newlines by CRLF
        -- note however that this the default server uses this
        to copy binary data as well.

        """
        shutil.copyfileobj(source, outputfile)

    def guess_type(self, path):
        """Guess the type of a file.

        Argument is a PATH (a filename).

        Return value is a string of the form type/subtype,
        usable for a MIME Content-type header.

        The default implementation looks the file's extension
        up in the table self.extensions_map, using application/octet-stream
        as a default; however it would be permissible (if
        slow) to look inside the data to make a better guess.

        """

        base, ext = posixpath.splitext(path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        else:
            return self.extensions_map['']

    if not mimetypes.inited:
        mimetypes.init() # try to read system mime.types
    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
        '': 'application/octet-stream', # Default
        '.py': 'text/plain',
        '.c': 'text/plain',
        '.h': 'text/plain',
        '.cpp': 'text/plain',
        '.java': 'text/plain',
        '.php': 'text/plain',
        '.json': 'text/plain',
        '.js': 'text/plain',
        '.css': 'text/plain',
        '.html': 'text/html',
        '.m': 'text/plain',
        '.txt': 'text/plain',
        '.ini': 'text/plain',
        '.jpg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp',
        '.ogg': 'audio/ogg',
        '.mp3':'audio/mpeg, audio/x-mpeg, audio/x-mpeg-3, audio/mpeg3, text/plain',
        '.mp4':'video/mp4',
        '.m4a':'audio/mp4',
        '.avi':'video/avi',
        '.pdf':'application/pdf',
        })


def test(HandlerClass = basicHTTPRequestHandler,ServerClass = BaseHTTPServer.HTTPServer):
    BaseHTTPServer.test(HandlerClass, ServerClass)


if __name__ == '__main__':
    test()
