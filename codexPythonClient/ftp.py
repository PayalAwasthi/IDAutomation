"""
ftp.py

Written by Eric Robinson, Leslie Leifer

Used to put and get files from an ftp server.


"""

import os, sys, os.path, ftplib, time


def goToDir(ftpobj, path):
   """
take any path and try to cd into it.  If the path doesn't exist,
create it.
   """

   tolist = path.split("/")
   for i in range(1, len(tolist)+1):
      tempto = "/".join(tolist[:i])
      if tempto == "":
         tempto = "/"
      try:
         ftpobj.cwd(tempto)
      except:
         ftpobj.mkd(tempto)
         ftpobj.cwd(tempto)


def postFolder(ftpsrv, localpath, remotepath):
   """
   Recursively posts the contents of a folder to an ftp server
   """

   relpath = ""
   toplevel = 1
   for (root, dirlist, filelist) in os.walk(localpath):
      # For each subfolder

      if toplevel:
         newroot = os.path.normpath(os.path.join(remotepath, root))
         # remove the root path from the absolute path to make it relative
         relpath = newroot.replace(localpath, "")
         toplevel = 0
      else:
         relpath = root.replace(localpath, "").replace(relpath, "")

      # Strip any slashes from the relative path
      relpath = relpath.strip(os.sep)

      # On windows, replace backslashes with forward slashes
      relpath = relpath.replace(os.sep, "/")

      # For remote paths, we must use forward slashes, so we join the paths
      # manually instead of with os.path.join
      fullremotedir = "/".join((ftpsrv.pwd(), relpath))

      goToDir(ftpsrv, fullremotedir)

      for filename in filelist:
         # For each file in the subfolder, copy to ftp server
         fulllocalpath = os.path.join(root, filename)
         postFile(ftpsrv, filename, fulllocalpath)


def postFile(ftpsrv, filename, localfilename):
   """
      Uses ntransfercmd to do a more advanced post.
      yields a tuple of information about transfer times
   """
   bitlabel = "bytes"
   ratelabel = "bytes/sec"

   ftpsrv.voidcmd("TYPE I")
   ftpsrv.set_pasv(0)
   fd = open(localfilename, "rb")
   datasock, bytes = ftpsrv.ntransfercmd("STOR %s" % (filename))
   bytes = os.stat(localfilename)[6]
   atime = time.time()

   try:
      while 1:
         buf = fd.read(4096)
         if not len(buf):
            break
         datasock.sendall(buf)
   finally:
      btime = time.time()
      datasock.close()
      fd.close()
      ftpsrv.voidresp()

   timediff = btime - atime
   if timediff > 0.0:
      sendrate = float(bytes) / timediff
   else:
      sendrate = 0.0

   bytes = float(bytes)
   bitlabels = ["KB", "MB", "GB"]
   ratelabels = ["KB/s", "MB/s", "GB/s"]

   while bytes > 1024.0 and len(bitlabels):
      bytes = bytes / 1024.0
      bitlabel = bitlabels.pop(0)

   while sendrate > 1024.0 and len(ratelabels):
      sendrate = sendrate / 1024.0
      ratelabel = ratelabels.pop(0)

   print "%s : %.2f %s at %.2f %s" % (filename, bytes, bitlabel, sendrate, ratelabel)

   return (bytes, sendrate)



class DirEntry:
	"""
	Figure out if it's a file or folder
	"""

	def __init__(self, filename, ftpobj, startingdir = None):
		self.filename = filename
		if startingdir == None:
			startingdir = ftpobj.pwd()
		
		try:
			ftpobj.cwd(filename)
			self.filetype = 'd'
			ftpobj.cwd(startingdir)
		except ftplib.error_perm:
			self.filetype = '-'
		
	def gettype(self):
		return self.filetype
		
	def getfilename(self):
		return self.filename


def download(ftpobj, localpath, remotepath):
   """
      Download either a file or a directory from the FTP server.  If a directory,
      then download all files and subdirs recursively.
   """
   item = DirEntry(remotepath, ftpobj)
   if item.gettype() == "-":
      downloadfile(ftpobj, remotepath, localpath)
   else:
      downloaddir(ftpobj, localpath, remotepath)

		
def downloadfile(ftpobj, remotefile, localfile=None):
	"""
	Download a file
	"""

	if localfile == None:
		localfile = remotefile
	buildfile = open(localfile, "wb")
	ftpobj.retrbinary("RETR %s" % (remotefile), buildfile.write)

def downloaddir(ftpobj, localpath, remotepath, rec = 'True'):
	"""
	Download from a folder location, recursively or not.
	"""

	oldlocaldir = os.getcwd()
	if not os.path.isdir(localpath):
		os.makedirs(localpath)
	olddir = ftpobj.pwd()
	
	try:
		os.chdir(localpath)
		ftpobj.cwd(remotepath)
		filelist = ftpobj.nlst()
		if rec == 'True':
			for file in filelist:
				item = DirEntry(file, ftpobj, ftpobj.pwd())
				if item.gettype() == '-':
					downloadfile(ftpobj, file, file)
				else:
					downloaddir(ftpobj, file, file)
		else:
			for file in filelist:
				item = DirEntry(file, ftpobj, ftpobj.pwd())
				if item.gettype() == '-':
					downloadfile(ftpobj, file, file)
				else:
					pass
	finally:
		os.chdir(oldlocaldir)
		ftpobj.cwd(olddir)
