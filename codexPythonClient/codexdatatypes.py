"""
		codexdatatypes.py
		
		Used to define classes used as return values from codex.py calls.
		
		Based on the Codex 2.0 API details document present at:
		https://zerowing.corp.adobe.com/display/codex/Codex+2.0+API+Details
"""

import types

class Product:
	"""
		Complex datatype containing all metadata about a particular product, including name, type, link, and description.  

		<product name="Photoshop" type="Point Product" id="34">
		  <link>http://photoshop.corp.adobe.com</link>
		  <description>This is a description of Photoshop</description>
		</product>
	"""

	def __init__(self, name, type, id, link, description, sapcode, watsonproduct, watsonfamily, latestversionid, deprecated):
		self._name = name
		self._type = type
		self._id = id
		self._link = link
		self._description = description
		if self._description:
			self._description = self._description.encode("UTF-8")
		self._sapcode = sapcode
		self._watsonproduct = watsonproduct
		self._watsonfamily = watsonfamily
		self._latestversionid = latestversionid
		self._deprecated = deprecated


class Subproduct:
	"""
		Complex datatype containing all metadata about a particular Subproduct, including name, id, and description.  

		<subproduct id="1" name="Core">
			<description>This is the core portion of the application</description>
		</subproduct>
	"""

	def __init__(self, id, name, description):
		self._id = id
		self._name = name
		self._description = description


class Server:
	"""
		Complex datatype containing all metadata about a particular server, including name, id, and webname.

		<server name="hermes.corp.adobe.com" id="1" webname="http://webhermes.corp.adobe.com" />
	"""

	def __init__(self, name, id, webname):
		self._name = name
		self._id = id
		self._webname = webname
class Location:	def __init__(self, id, query, path, server, uri, protocol, status):		self._query = query		self._path = path		self._server = server		self._uri = uri		self._protocol = protocol		self._status = status

class Version:
	"""
		Complex datatype containing all metadata about a particular product version, including product name, version string, codename, link, and description.  

		<version product="Photoshop" name="10.0" codename="RedPill" id="34" unified_id="0">
		  <link>http://photoshop.corp.adobe.com</link>
		  <description>This is a description of Photoshop 10.0</description>
		</version>
	"""

	def __init__(self, product, name, codename, id, unified_id, link, description):
		self._product = product
		self._name = name
		self._codename = codename
		self._id = id
		self._unified_id = unified_id
		self._link = link
		self._description = description


class CertLevel:
	"""
		Complex datatype containing all metadata about a particular certification level, including name, id, and web color.  

		<certlevel name="Not Tested" id="10" color="#FFFFFF" />
	"""

	def __init__(self, name, id, color):
		self._name = name
		self._id = id
		self._color = color


class Status:
	"""
		Complex datatype containing all metadata about a particular status type, including name, id, and availability.  

		<status name="Available" id="1" isavailable="1" />
	"""

	def __init__(self, name, id, isavailable):
		self._name = name
		self._id = id
		self._isavailable = isavailable


class CompilerTarget:
	"""
		Complex datatype containing all metadata about a particular compiler target, including name and id.  

		<compilertarget name="Debug" id="1" />
	"""

	def __init__(self, name, id):
		self._name = name
		self._id = id


class LicenseModel:
	"""
		Complex datatype containing all metadata about a particular license model, including name and id.  

		<licensemodel name="Retail" id="1" />
	"""

	def __init__(self, name, id):
		self._name = name
		self._id = id


class Format:
	"""
		Complex datatype containing all metadata about a particular format, including name and id.  

		<format name="Raw Build" id="1" />
	"""

	def __init__(self, name, id):
		self._name = name
		self._id = id


class Platform:
	"""
		Complex datatype containing all metadata about a particular platform, including name, id, and description.  

		<platform name="win32" id="1" description="Windows OS (32-bit CPU)" />
	"""

	def __init__(self, name, id, description):
		self._name = name
		self._id = id
		self._description = description


class PlatformGroupRecord:
	"""
		representation of a specific platform group record:

		<platformgrouprecord id="1" groupid="1" platform="win32" />
	"""

	def __init__(self, id, groupid, platform):
		self._id = id
		self._groupid = groupid
		self._platform = platform


class PlatformGroup:
	"""
		Complex datatype containing all metadata about a particular platform group, including name, id, product, version.  Also contains records of type Platform Group Record.  

		<platformgroup name="Win/Mac" id="1" product="BIB" version ="6.0" >
		   <platformgrouprecord id="1" groupid="1" platform="win32" />
		   <platformgrouprecord id="2" groupid="1" platform="osx10" />
		</platformgroup>
	"""

	def __init__(self, name, id, product, version, platformGroupRecordList):
		self._name = name
		self._id = id
		self._product = product
		self._version = version
		self._platformGroupRecordList = platformGroupRecordList


class Contact:
	"""
		Complex datatype containing all metadata about a particular contact, including name, id, and type.  

		<contact name="errobins" id="1" type="Release Engineer" />
	"""

	def __init__(self, name, id, type):
		self._name = name
		self._id = id
		self._type = type


class ContactType:
	"""
		Complex datatype containing all metadata about a particular contact type, including name and id.  

		<contacttype name="Release Engineer" id="1" />
	"""

	def __init__(self, name, id):
		self._name = name
		self._id = id


class Language:
	"""
		Complex datatype containing all metadata about a particular language, including name, id, and code.  

		<language name="U.S. English" id="1" code="en_US" />
	"""

	def __init__(self, name, id, code):
		self._name = name
		self._id = id
		self._code = code


class ProductType:
	"""
		Complex datatype containing all metadata about a particular product type, including name, id, and description.  

		<producttype name="Library" id="1" description="A component that is compiled, linked, or otherwise built into a project." />
	"""

	def __init__(self, name, id, description):
		self._name = name
		self._id = id
		self._description = description


class PickupOption:
	"""
		Complex datatype containing all metadata about a particular pickup option, including name and id.  

		<pickupoption name="Latest" id="1" />
	"""

	def __init__(self, name, id):
		self._name = name
		self._id = id


class Server:
	"""
		Complex datatype containing all metadata about a particular server, including name, id, and webname.  

		<server name="hermes.corp.adobe.com" id="1" webname="http://webhermes.corp.adobe.com" />
	"""

	def __init__(self, name, id, webname):
		self._name = name
		self._id = id
		self._webname = webname


class ProfileRecord:
	"""
		Complex datatype containing all metadata about a particular profile record, including id, product, version, parameters for query, etc.  

		<profilerecord id="1" profileid="34" product="Bridge" version="2.0" pickupoption="Latest" certlevel="Suite Installer Ready" compiletarget="Release" licensemodel="Retail" format="RIBS Installer" build="" parentprofile="" />
	"""

	def __init__(self, id, profileid, product, version, subproduct, pickupoption, certlevel, compiletarget, licensemodel, format, build, parentprofile):
		self._id = id
		self._profileid = profileid
		self._product = product
		self._version = version
		self._subproduct = subproduct
		self._pickupoption = pickupoption
		self._certlevel = certlevel
		self._compiletarget = compiletarget
		self._licensemodel = licensemodel
		self._format = format
		self._build = build
		self._parentprofile = parentprofile


class Profile:
	"""
		Complex datatype containing all metadata about a particular profile, including name, product, version, description, etc.  Also contains profile record tags for listing the contents of each profile  

		<profile name="English_Win Builds" product="Photoshop" version="CS3" id="34" description="Used for English Windows builds" parentproduct="Master Collection" parentversion="CS3" >
		   <profilerecords>
		      <profilerecord id="1" profileid="34" product="Bridge" version="2.0" pickupoption="Latest" certlevel="Suite Installer Ready" compiletarget="Release" licensemodel="Retail" format="RIBS Installer" build="" parentprofile="" />
		      <profilerecord id="2" profileid="34" product="STI_Camera_Raw" version="4.0" pickupoption="Specific Build" certlevel="" compiletarget="Release" licensemodel="Retail" format="RIBS Installer" build="135" parentprofile="" />
		   </profilerecords>
		</profile>
	"""

	def __init__(self, name, product, version, id, description, parentproduct, parentversion, profileRecordsList):
		self._name = name
		self._product = product
		self._version = version
		self._id = id
		self._description = description
		self._parentproduct = parentproduct
		self._parentversion = parentversion
		self._profileRecordsList = profileRecordsList


class ProfileData:
	"""
		Complex datatype containing all metadata about a particular profile, including name, product, version, description, etc.  Does NOT contain profile record tags.  

		<profiledata name="English_Win Builds" product="Photoshop" version="CS3" id="34" description="Used for English Windows builds" parentproduct="Master Collection" parentversion="CS3" />
	"""

	def __init__(self, name, product, version, id, description, parentproduct, parentversion):
		self._name = name
		self._product = product
		self._version = version
		self._id = id
		self._description = description
		self._parentproduct = parentproduct
		self._parentversion = parentversion


class MetadataKey:
	"""
		Complex datatype containing all metadata about a particular metadata key, including name, id, product, and version.  

		<metadatakey name="AdobeCode" id="1" product="" version="" />
	"""

	def __init__(self, name, id, product, version):
		self._name = name
		self._id = id
		self._product = product
		self._version = version


class Build:
	"""
		Complex datatype containing all metadata about a particular build, including name, type, product, version, source, location, etc.  

		<build id="34" product="Design Premium" version="CS3" build="20071029.m.34" platform="win32" language="en_US,en_GB" compilertarget="Release" licensemodel="Retail" format="RIBS Installer" certlevel="Not Tested" status="Available" date="2007/10/29:11:23:54">
		  <location protocol="ftp" server="pele.corp.adobe.com" path="DesignPremium/CS3/Win/en_US/20071029.m.34/Retail" query="" />
		  <sources>
		     <source protocol="p4" server="yorktown.corp.adobe.com:1820" path="//suites/main/..." query="@123423" />
		  </sources>
		  <notes>
		     <note id=123>This build contains a lot of products and is very good.  You should use it.</note>
		  </notes>
		  <metadata>
		     <item id="456" key="AdobeCode" value="661C5DAC-2334-4D28-A638-6FC1F3065926" />
		  </metadata>
		</build>
	"""

	def __init__(self, id, product, version, subproduct, build, platform, language, compilertarget, licensemodel, format, certlevel, status, date, datemodified, user):
		self._id = id
		self._product = product
		self._version = version
		self._subproduct = subproduct
		self._build = build
		self._platform = platform
		self._language = language
		self._compilertarget = compilertarget
		self._licensemodel = licensemodel
		self._format = format
		self._certlevel = certlevel
		self._status = status
		self._date = date
		self._datemodified = datemodified
		self._user = user
		
		self._location = {}
		self._sources = []
		self._notes = []
		self._metadata = []
		self._partlist = []
		self._fileinfo = []

	def addLocation(self, protocol, server, path, query):
		"store the location of this build in a dictionary"
		self._location = {'protocol':protocol, 'server':server, 'path':path, 'query':query} 
		
	def addSource(self, protocol, server, path, query):
		"add a source entry for this build, stored as a dictionary"
		self._sources.append({'protocol':protocol, 'server':server, 'path':path, 'query':query})
		
	def addNote(self, id, note):
		"add a note to this build, stored as a dictionary"
		self._notes.append({'id':id, 'note':note})
		
	def addMetadata(self, id, key, value):
		"add metadata info to this build, stored as a dictionary"
		self._metadata.append({'id':id, 'key':key, 'value':value})

	def addFileInfo(self, filename, size, md5):
		"add fileinfo to this build, stored as a dictionary"
		self._fileinfo.append({'filename':filename, 'size':size, 'md5':md5})

	def addPart(self, partobj):
		self._partlist.append(partobj)


class Part:
	"""
		Complex datatype containing all metadata about a particular build part, including name, type, product, version, etc.  

	"""

	def __init__(self, id, buildid, product, version, subproduct, revision, partnumber, platform, language, compilertarget, licensemodel, format, status, date, datemodified, user):
		self._id = id
		self._product = product
		self._version = version
		self._subproduct = subproduct
		self._revision = revision
		self._partnumber = partnumber
		self._platform = platform
		self._language = language
		self._compilertarget = compilertarget
		self._licensemodel = licensemodel
		self._format = format
		self._status = status
		self._date = date
		self._datemodified = datemodified
		self._user = user
		
		self._location = {}
		self._metadata = []
		self._fileinfo = []

	def addLocation(self, protocol, server, path, query, uri):
		"store the location of this build in a dictionary"
		self._location = {'protocol':protocol, 'server':server, 'path':path, 'query':query, 'uri':uri} 
		
	def addMetadata(self, id, key, value):
		"add metadata info to this part, stored as a dictionary"
		self._metadata.append({'id':id, 'key':key, 'value':value})

	def addFileInfo(self, filename, size, md5):
		"add fileinfo to this part, stored as a dictionary"
		self._fileinfo.append({'filename':filename, 'size':size, 'md5':md5})


class OldDataSet(types.DictType):
	"""
		Complex datatype used by GetNewData method
	"""
	def __init__(self, product, version, target):
		self._attrs = {}
		self._attrs['product'] = product
		self._attrs['version'] = version
		self._attrs['target'] = target