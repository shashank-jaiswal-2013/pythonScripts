'''
	@author Shashank Jaiswal
	@since 01-07-2014
	@version 0.0.0.1
	@description 
				xdg-open functionality on windows (cmd-line).
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

import sys;
import time;
import re;
import os;
import subprocess;
import id3reader;
import sqlite3;
import random;
import mutagen;


searchMode = '';
args = [];
cwd = '';


def add_flac_cover(filename, albumart):
        audio = File(filename)
        image = Picture()
        image.type = 3
        if albumart.endswith('png'):
            mime = 'image/png'
        else:
            mime = 'image/jpeg'
        image.desc = 'front cover'
        with open(albumart, 'rb') as f: # better than open(albumart, 'rb').read() ?
            image.data = f.read()

        audio.add_picture(image)
        audio.save()

def recursivelyListAllFilesInDir(dirAbsName):
        filesListinCDIR = [];
        try:
                for x in os.listdir(dirAbsName):
                        if os.path.isfile(os.path.join(dirAbsName, x)):
                                if(x.endswith('.mp3') and searchMode=='--mp3'):
                                   id3r = id3reader.Reader(os.path.join(dirAbsName, x));
                                   try:
                                           tup = (os.path.join(dirAbsName, x), str(id3r.getValue('album')), str(id3r.getValue('performer')), str(id3r.getValue('title')), str(id3r.getValue('year')));
                                   except UnicodeEncodeError:
                                           tup = (os.path.join(dirAbsName, x), '', '', '', '');
                                   filesListinCDIR.append(tup);
                                else:
                                   filesListinCDIR.append(os.path.join(dirAbsName, x));
                        elif os.path.isdir(os.path.join(dirAbsName, x)):
                                filesListinCDIR += recursivelyListAllFilesInDir(os.path.join(dirAbsName, x));
        except WindowsError:
                print 'Error reading directory: ', dirAbsName;
        return filesListinCDIR;


def openFileFromCurrDir(inp):
        #inp is a string
        inp = inp.lower();
        print 'The regex to search for: ', inp, ' in ', cwd, ' directory'
        filesListinCDIR = [];
        if('--rsv' in args):
                filesListinCDIR = recursivelyListAllFilesInDir(cwd);
        else:
                for x in os.listdir(cwd):
                        if os.path.isfile(x):
                                filesListinCDIR.append(x);
        
        inp = inp.replace('.', '\.')
        inp = inp.replace('*', '.+')
        matchedFiles = [];
        for aFile in filesListinCDIR:
                tupleYesOrNo = False;
                if isinstance(aFile, tuple):
                           aFile = "::".join(aFile);
                           tupleYesOrNo = True;
                match = re.search(inp, aFile.split('\\')[-1].lower());
                if match:
                        if tupleYesOrNo:
                                matchedFiles.append(aFile.split('::')[0]);
                        else:
                                matchedFiles.append(aFile);


        if len(matchedFiles)==0:
                print 'No file matched your criterion'

        elif len(matchedFiles)==1:
                print 'Started', matchedFiles[0];
                if matchedFiles[0].endswith('.mp3'):
                        id3r = id3reader.Reader(matchedFiles[0]);
                        print 'Title:', id3r.getValue('title');
                        print 'Album:', id3r.getValue('album');
                        print 'Artist:', id3r.getValue('performer');
                        print 'Year:', id3r.getValue('Year');
                        subprocess.call('''vlc.py "'''+ matchedFiles[0] + '''"''', shell=True);
                else:
                        os.startfile(matchedFiles[0]);

        elif len(matchedFiles)>1:
                print 'Multiple files matched your criterion';
                count = 0;
                for mm in matchedFiles:
                        count += 1;
                        print str(count), ' - ', mm.split('\\')[-1];
                k = True;
                mode = -1;
                opCode = '-p';
                while(k==True):
                        pp = raw_input('Enter File index followed by operation code, -1 to exit: ');
                        pp = pp.split(' ');
                        try:
                                mode = int(pp[0]);
                                k = False;
                        except ValueError:
                                print 'Input a number...'
                        #if(len(pp)==1 and mode!=-1):
                        #        k = True;
                        #        print 'Input an operation code...'
                        if(len(pp)==2):
                                opCode = pp[1];
                                if not (opCode=='-p' or opCode=='-ut'):
                                        k = True;
                                        print 'Input a valid operation code...'
                        if mode==0 or mode<-1 or mode>len(matchedFiles):
                                k = True;
                                print 'Input a valid number...'

                if(mode>0 and mode<=len(matchedFiles) and opCode!=''):
                        if(opCode=='-p'):
                                print 'Started', matchedFiles[mode-1];
                                if matchedFiles[mode-1].endswith('.mp3'):
                                        id3r = id3reader.Reader(matchedFiles[mode-1]);
                                        print 'Title:', id3r.getValue('title');
                                        print 'Album:', id3r.getValue('album');
                                        print 'Artist:', id3r.getValue('performer');
                                        print 'Year:', id3r.getValue('Year');
                                        subprocess.call('''vlc.py "'''+ matchedFiles[mode-1] + '''"''', shell=True);
                                else:
                                        os.startfile(matchedFiles[mode-1]);
                        elif(opCode=='-ut'):
                                print 'Update', matchedFiles[mode-1];
                                subprocess.call('''start explorer.exe /select,"'''+ matchedFiles[mode-1] + '''"''', shell=True);
                        
        return 'Finished...';




def updateDatabaseForCurrDir(inp):
        filesListinCDIR = [];
        sys.stdout.write("\rUpdating Database: 1%")
        sys.stdout.flush()

        if('--rsv' in args):
                filesListinCDIR = recursivelyListAllFilesInDir(cwd);

        randInt = random.randint(10,25);
        sys.stdout.write("\rUpdating Database: "+str(randInt)+"%")
        sys.stdout.flush()

        numberOfFiles = len(filesListinCDIR);
        dummyCount = 0;
        
        conn = sqlite3.connect(cwd+'\\fileDb.db')
        conn.text_factory = str
        c2 = conn.cursor()
        try:
                c2.execute('''CREATE TABLE files (data)''')
        except:
                '''print('')'''       
        c2.execute('DELETE FROM files')
        conn.commit()

        for aFile in filesListinCDIR:
                dummyCount += 1;
                sys.stdout.write("\rUpdating Database: "+str(randInt+int(dummyCount*(100-randInt)/numberOfFiles))+"%")
                sys.stdout.flush()
                tupleYesOrNo = False;
                if isinstance(aFile, tuple):
                           aFile = "::".join(aFile);
                           tupleYesOrNo = True;
                
                c2.execute('INSERT INTO files(data) VALUES (?)', (aFile,))
        conn.commit();
        conn.close();
        return '\nFinished...';




def openFileFromCurrDirViaDb(inp):
        inp = inp.lower();
        print 'The regex to search for: ', inp, ' in ', cwd, ' directory using Db'

        inp = inp.replace('.', '\.')
        inp = inp.replace('*', '.+')
        matchedFiles = [];
        
        if(os.path.exists(cwd+'\\fileDb.db')==False):
                print '''No database found in current Directory \n remove --fromDb or run "xdg-open.py --cwd --rsv --update"''';
        else:
                conn2 = sqlite3.connect(cwd+'\\fileDb.db')
                conn2.text_factory = str;
                c3 = conn2.cursor()
                res = c3.execute('SELECT * FROM files')
                for row in res:
                        aFile = str(row[0]).lower()
                        match = re.search(inp, aFile.split('\\')[-1].lower());
                        if match:
                                if '::' in aFile:
                                        matchedFiles.append(aFile.split('::')[0]);
                                else:
                                        matchedFiles.append(aFile);


                if len(matchedFiles)==0:
                        print 'No file matched your criterion'

                elif len(matchedFiles)==1:
                        print 'Started', matchedFiles[0];
                        if matchedFiles[0].endswith('.mp3'):
                                id3r = id3reader.Reader(matchedFiles[0]);
                                print 'Title:', id3r.getValue('title');
                                print 'Album:', id3r.getValue('album');
                                print 'Artist:', id3r.getValue('performer');
                                print 'Year:', id3r.getValue('Year');
                                subprocess.call('''vlc.py "'''+ matchedFiles[0] + '''"''', shell=True);
                        else:
                                os.startfile(matchedFiles[0]);

                elif len(matchedFiles)>1:
                        print 'Multiple files matched your criterion';
                        count = 0;
                        for mm in matchedFiles:
                                count += 1;
                                print str(count), ' - ', mm.split('\\')[-1];
                        k = True;
                        mode = -1;
                        opCode = '-p';
                        while(k==True):
                                pp = raw_input('Enter File index followed by operation code, -1 to exit: ');
                                pp = pp.split(' ');
                                try:
                                        mode = int(pp[0]);
                                        k = False;
                                except ValueError:
                                        print 'Input a number...'
                                #if(len(pp)==1 and mode!=-1):
                                #        k = True;
                                #        print 'Input an operation code...'
                                if(len(pp)==2):
                                        opCode = pp[1];
                                        if not (opCode=='-p' or opCode=='-ut'):
                                                k = True;
                                                print 'Input a valid operation code...'
                                if mode==0 or mode<-1 or mode>len(matchedFiles):
                                        k = True;
                                        print 'Input a valid number...'

                        if(mode>0 and mode<=len(matchedFiles) and opCode!=''):
                                if(opCode=='-p'):
                                        print 'Started', matchedFiles[mode-1];
                                        if matchedFiles[mode-1].endswith('.mp3'):
                                                id3r = id3reader.Reader(matchedFiles[mode-1]);
                                                print 'Title:', id3r.getValue('title');
                                                print 'Album:', id3r.getValue('album');
                                                print 'Artist:', id3r.getValue('performer');
                                                print 'Year:', id3r.getValue('Year');
                                                subprocess.call('''vlc.py "'''+ matchedFiles[mode-1] + '''"''', shell=True);
                                        else:
                                                os.startfile(matchedFiles[mode-1]);
                                elif(opCode=='-ut'):
                                        print 'Update', matchedFiles[mode-1];
                                        subprocess.call('''start explorer.exe /select,"'''+ matchedFiles[mode-1] + '''"''', shell=True);
                                
        return 'Finished...';
                                

def start(fileName):
    print 'Started', fileName;
    if fileName.endswith('.mp3'):
        id3r = id3reader.Reader(fileName);
        print 'Title:', id3r.getValue('title');
        print 'Album:', id3r.getValue('album');
        print 'Artist:', id3r.getValue('performer');
        print 'Year:', id3r.getValue('Year');
        subprocess.call('''vlc.py "'''+ fileName + '''"''', shell=True);
    else:
        os.startfile(fileName);
    return 'Finished...';


if __name__ == '__main__':
    args = sys.argv;
    if(len(sys.argv)>=2):
        if(sys.argv[1]=='--cwd' or os.path.isdir(sys.argv[1]) or os.path.isfile(sys.argv[1])):
                if(os.path.isfile(sys.argv[1])):
                        print(start(sys.argv[1]));
                        exit();
                cwd = os.getcwd();
                if(os.path.isdir(sys.argv[1])):
                        cwd = os.path.abspath(sys.argv[1]);
                if not ('--update' in args):
                        if('--mp3' in args):
                                searchMode = '--mp3';
                        if('--fromDb' in args):
                                print(openFileFromCurrDirViaDb(sys.argv[2]));
                        else:
                                print(openFileFromCurrDir(sys.argv[2]));
                else:
                        searchMode = '--mp3';
                        print(updateDatabaseForCurrDir(sys.argv[2]));
        else:
                print '''usage: {--cwd} fileNameRegex'''
    else:
        print '''usage: {--cwd} fileNameRegex'''
