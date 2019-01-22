from xml.dom.minidom import getDOMImplementation, parseString
import os.path, time

class VersionInfo(object):
   """
      Class for creating a VersionInfo.xml file, which is a hierarchical list of
      all components included in a build, and their version information.

      Also used for parsing VersionInfo.xml files and modifying or updating them.
   """

   class ManifestError(Exception): pass
   class ManifestVersionError(ManifestError): pass

   def __init__(self, xmlfile=None):
      """
         Instantiate class by creating the DOM object and the major elements
      """

      if xmlfile == None:
         self.impl = getDOMImplementation()

         self.vinfo = self.impl.createDocument(None, "manifest", None)
         self.manifest = self.vinfo.documentElement
         self.manifest.setAttribute("version", "2.0")
         self.versioninfo = self.vinfo.createElement("versioninfo")
         self.manifest.appendChild(self.versioninfo)
         self.buildlist = []

      else:
         if os.path.exists(xmlfile):
            # If the file exists, read it in and try to store it as a string.
            # Read in the file and remove extra spaces and line breaks
            xmlstringlist = []
            xmlfileobj = file(xmlfile)
            for line in xmlfileobj:
               # Normally, we strip all white space out, but some teams
               # give us files with tags spanning multiple lines.  When
               # we strip all the whitespace out of these, we get attributes
               # that run into each other.  To solve this, if a stripped
               # line ends with a ", then we append a space to make sure
               # the next line doesn't put an attribute name right next
               # to the quote character.
               templine = line.strip()
               if templine.endswith("\""):
                  templine = templine + " "
               xmlstringlist.append(templine)
            xmlfileobj.close()

            xmlstring = "".join(xmlstringlist)
         else:
            # The file doesn't exist, so let's see if it's an xmlstring
            xmlstring = xmlfile

         self.vinfo = parseString(xmlstring)
         self.manifest = self.vinfo.documentElement
         self.manifest.normalize()

         self.manifestversion = self.manifest.getAttribute("version")
         try:
            self.manifestversion = float(self.manifestversion)
         except:
            raise ManifestVersionError, "Manifest version %s does not seem to be a number" % (self.manifestversion)

         self.buildlist = []
         verinfolist = self.manifest.getElementsByTagName("versioninfo")
         if len(verinfolist) == 0:
            raise ManifestError, "No <versioninfo> tag found in file %s" % (xmlfile)
         elif len(verinfolist) > 1:
            raise ManifestError, "Multiple <versioninfo> tags found in file %s" % (xmlfile)
         self.versioninfo = verinfolist[0]
         for element in self.versioninfo.childNodes:
            if element.nodeType == element.ELEMENT_NODE and element.tagName == "build":
               self.buildlist.append(self.Build(element))



   def addBuild(self, product, version, subproduct, buildnum, datetime, compilertarget, licensemodel, format, platform, lang):
      """
         Add a new build object to the DOM representation.
      """

      build = self.vinfo.createElement("build")

      build.setAttribute("product", product)
      build.setAttribute("version", version)
      build.setAttribute("subproduct", subproduct)
      build.setAttribute("build", buildnum)
      build.setAttribute("datetime", datetime)
      build.setAttribute("compilertarget", compilertarget)
      build.setAttribute("licensemodel", licensemodel)
      build.setAttribute("format", format)
      build.setAttribute("platform", platform)
      build.setAttribute("lang", lang)

      node = self.versioninfo.appendChild(build)

      return self.Build(node)


   def toXML(self, encoding="UTF-8"):
      """
         Returns a long string with a prettified XML representation of the object.
         Can be written directly to a file.
      """
      return self.vinfo.toprettyxml(" ", "\n", encoding)


   def version(self):
      """
         Returns the version of the manifest xml schema, which is an
         attribute of the manifest document tag.
      """
      return self.manifestversion

   def builds(self, product=None):
      """
         Returns a list of Build objects, filtered by product name if necessary
      """
      if product == None:
         return self.buildlist
      else:
         resultlist = []
         for build in self.buildlist:
            if build.product == product:
               resultlist.append(build)
         return resultlist

   def simpleVersionStrings(self, product=None):
      """
         Returns a list of strings with simply the product name and version numbers.
         Suitable for using in a VersionInfo.txt file or such.
      """
      resultlist = []
      for build in self.builds(product):
         text = "%s %s" % (build.product, build.fullversion)
         resultlist.append(text)
      return resultlist

   def simpleVersionDates(self, product=None):
      """
         Returns a list of strings with simply the product build dates.
         Suitable for using in a VersionInfo.txt file or such.
      """
      resultlist = []
      for build in self.builds(product):
         text = "%s" % (build.datetime)
         resultlist.append(text)
      return resultlist

   def target(self):
      """
         Returns the target value from a 1.0 or 1.1 manifest build
      """
      build = self.buildlist[0]
      if build.manifestversion < 2.0:
         return build.target
      else:
         return None

   def removeComponents(self):
      """
         Remove the components of components of the builds
         This method uses the getElementsByTagName method to get all the
         nodes named "components".  In this list, the very first entry
         will be the components node for our build.  The rest will be components
         nodes of all the components of our build.  Since these "components of
         components" are never used by Codex, we can safely strip them out
         before passing the xml content with addBuild.
      """
      clist = self.vinfo.getElementsByTagName("components")
      while len(clist) > 1:
         # Remove entries until there's only one left (the first one)
         # We do this by getting the parent node of each entry and then
         # calling removeChild() on the parent.  Then we unlink the dead
         # node to get rid of it completely.
         p = clist[1].parentNode
         z = p.removeChild(clist[1])
         z.unlink()
         # Call the list method again to update the list.
         clist = self.vinfo.getElementsByTagName("components")


   class Build(object):
      """
         Class for parsing a build DOM object read from a VersionInfo.xml file.
      """

      def __init__(self, element):
         """
            Instantiate the class by parsing the buildnode and assigning variable
            values based on the node's attributes.
         """
         self.element = element

         # The manifest version is located in the manifest tag, which does us
         # no good here.  We need to determine what version of build tag this is,
         # so we look for specific attributes associated with eaach version.

         if element.hasAttribute("version_major"):
            self.manifestversion = 1.0
         elif element.hasAttribute("version") and element.hasAttribute("target"):
            self.manifestversion = 1.1
         elif element.hasAttribute("compilertarget"):
            self.manifestversion = 2.0
         else:
            raise ManifestError, "Unknown or missing attributes in build tag"

         self.product = element.getAttribute("product").encode('ascii')
         self.version = element.getAttribute("version").encode('ascii')

         if self.manifestversion == 1.0:
            # Combine the various version attributes into one.
            version_major = element.getAttribute("version_major").encode('ascii')
            version_minor = element.getAttribute("version_minor").encode('ascii')
            version_sub = element.getAttribute("version_sub").encode('ascii')

            if version_sub == "0":
               version_old = "%s.%s" % (version_major, version_minor)
            else:
               version_old = "%s.%s.%s" % (version_major, version_minor, version_sub)

            if not version_old.startswith("."):
               self.version = self.version_old
               element.setAttribute("version", self.version)

            if element.hasAttribute("version_major"):
               element.removeAttribute("version_major")
            if element.hasAttribute("version_minor"):
               element.removeAttribute("version_minor")
            if element.hasAttribute("version_sub"):
               element.removeAttribute("version_sub")

         if self.version == "":
            raise ManifestError, "No version attributes found in build tag"

         if self.manifestversion < 2.0:
            self.version_build = element.getAttribute("version_build").encode('ascii')
            self.build = self.version_build
            self.date = element.getAttribute("date").encode('ascii')
            self.time = element.getAttribute("time").encode('ascii')
            tempdate = time.strptime("%s %s" % (self.date, self.time), "%Y%m%d %H%M%S")
            self.datetime = time.strftime("%Y/%m/%d:%H:%M:%S", tempdate)
            self.target = element.getAttribute("target").encode('ascii')
            self.phase_major = element.getAttribute("phase_major").encode('ascii')
            self.phase_minor = element.getAttribute("phase_minor").encode('ascii')
         else:
            self.subproduct = element.getAttribute("subproduct").encode('ascii')
            self.build = element.getAttribute("build").encode('ascii')
            self.datetime = element.getAttribute("datetime").encode('ascii')
            self.compilertarget = element.getAttribute("compilertarget").encode('ascii')
            self.licensemodel = element.getAttribute("licensemodel").encode('ascii')
            self.format = element.getAttribute("format").encode('ascii')
            self.platform = element.getAttribute("platform").encode('ascii')

         self.fullversion = "%s %s" % (self.version, self.build)

         self.lang = element.getAttribute("lang").encode('ascii')

         # The repositories list stores the repository tag contents.

         self.repositories = []
         self.components = []
         self.directcomponents = []
         self.fileinfo = []
         self.metadata = {}
         self.componentsnode = None
         self.directcomponentsnode = None
         self.metadatanode = None
         self.fileinfonode = None

         for e in element.childNodes:
            if e.nodeType == e.ELEMENT_NODE:
               if e.tagName == "repository":
                  repository = {}
                  repository["scheme"] = e.getAttribute("scheme").encode('ascii')
                  repository["authority"] = e.getAttribute("authority").encode('ascii')
                  repository["path"] = e.getAttribute("path").encode('ascii')
                  repository["query"] = e.getAttribute("query").encode('ascii')

                  repository["URI"] = "%s://%s%s%s" % (repository["scheme"],
                                                       repository["authority"],
                                                       repository["path"],
                                                       repository["query"])

                  self.repositories.append(repository)

               if e.tagName == "components":
                  self.componentsnode = e
                  for comp in e.childNodes:
                     if comp.nodeType == comp.ELEMENT_NODE and comp.tagName == "build":
                        self.components.append(VersionInfo.Build(comp))

               if e.tagName == "directcomponents":
                  self.directcomponentsnode = e
                  for comp in e.childNodes:
                     if comp.nodeType == comp.ELEMENT_NODE and comp.tagName == "build":
                        self.directcomponents.append(VersionInfo.Build(comp))

               if e.tagName == "metadata":
                  self.metadatanode = e
                  for m in e.childNodes:
                     if m.nodeType == m.ELEMENT_NODE and m.tagName == "item":
                        k = m.getAttribute("key").encode('ascii')
                        v = m.getAttribute("value").encode('ascii')
                        self.metadata[k] = v

               if e.tagName == "fileinfo":
                  self.fileinfonode = e
                  for f in e.childNodes:
                     if f.nodeType == f.ELEMENT_NODE and f.tagName == "file":
                        n = f.getAttribute("name").encode('ascii')
                        m = f.getAttribute("md5").encode('ascii')
                        self.fileinfo.append((n, m))


      def _addComp(self, component):
         """
            Appends a component to the list of components.
            The component must be a DOM element object, as read from
            another XML file most likely.
         """
         if self.componentsnode == None:
            impl = getDOMImplementation()
            doc = impl.createDocument(None, "manifest", None)
            compgroup = doc.createElement("components")
            self.node.appendChild(compgroup)

         compgroup.appendChild(component)


      def addComponent(self, xmlfile, product=None):
         """
            Parse an xml file and add the build info from the file to our components list.
         """
         if not os.path.exists(xmlfile):
            raise ValueError, "File %s does not exist" % (xmlfile)
         buildfile = VersionInfo(xmlfile)

         if self.componentsnode == None:
            impl = getDOMImplementation()
            doc = impl.createDocument(None, "manifest", None)
            compgroup = doc.createElement("components")
            self.element.appendChild(compgroup)
            self.componentsnode = compgroup

         for buildobj in buildfile.builds(product):
            self.componentsnode.appendChild(buildobj.element)
            self.components.append(buildobj)


      def addDirectComponent(self, xmlfile, product=None):
         """
            Parse an xml file and add the build info from the file to our direct components list.
         """
         if not os.path.exists(xmlfile):
            raise ValueError, "File %s does not exist" % (xmlfile)
         buildfile = VersionInfo(xmlfile)

         if self.directcomponentsnode == None:
            impl = getDOMImplementation()
            doc = impl.createDocument(None, "manifest", None)
            compgroup = doc.createElement("directcomponents")
            self.element.appendChild(compgroup)
            self.directcomponentsnode = compgroup

         for buildobj in buildfile.builds(product):
            self.directcomponentsnode.appendChild(buildobj.element)
            self.directcomponents.append(buildobj)


      def addRepository(self, scheme, authority, path, query):
         """
            Add a repository to a build element
         """
         impl = getDOMImplementation()
         doc = impl.createDocument(None, "manifest", None)
         element = doc.createElement("repository")
         element.setAttribute("authority", authority)
         element.setAttribute("path", path)
         element.setAttribute("query", query)
         element.setAttribute("scheme", scheme)

         repository = {}
         repository['scheme'] = scheme
         repository['authority'] = authority
         repository['path'] = path
         repository['query'] = query
         repository['URI'] = "%s://%s%s%s" % (scheme, authority, path, query)

         self.element.appendChild(element)
         self.repositories.append(repository)


      def addMetadata(self, key, value):
         """
            Add a metadata entry to the build element
         """
         impl = getDOMImplementation()
         doc = impl.createDocument(None, "manifest", None)
         element = doc.createElement("item")
         element.setAttribute("key", key)
         element.setAttribute("value", value)

         if self.metadatanode == None:
            metanode = doc.createElement("metadata")
            metanode = self.element.appendChild(metanode)
            self.metadatanode = metanode

         self.metadatanode.appendChild(element)

         self.metadata[key] = value


      def addFile(self, path, md5, size=None):
         """
            Add a file entry to the build element
         """
         impl = getDOMImplementation()
         doc = impl.createDocument(None, "manifest", None)
         element = doc.createElement("file")
         element.setAttribute("name", path)
         element.setAttribute("md5", md5)
         if size:
            element.setAttribute("size", str(size))

         if self.fileinfonode == None:
            fileinfonode = doc.createElement("fileinfo")
            fileinfonode = self.element.appendChild(fileinfonode)
            self.fileinfonode = fileinfonode

         self.fileinfonode.appendChild(element)

         self.fileinfo.append((path, md5))


      def setCompilerTarget(self, compilertarget):
         """
            Set the compiler target attribute of the build tag to a new value
         """
         self.element.setAttribute("compilertarget", compilertarget)
         self.compilertarget = compilertarget


      def setLicenseModel(self, licensemodel):
         """
            Set the licensemodel attribute of the build tag to a new value
         """
         self.element.setAttribute("licensemodel", licensemodel)
         self.licensemodel = licensemodel


      def setFormat(self, format):
         """
            Set the format attribute of the build tag to a new value
         """
         self.element.setAttribute("format", format)
         self.format = format


      def setLang(self, lang):
         """
            Set the lang attribute of the build tag to a new value
         """
         self.element.setAttribute("lang", lang)
         self.lang = lang


      def setPlatform(self, platform):
         """
            Set the platform attribute of the build tag to a new value
         """
         self.element.setAttribute("platform", platform)
         self.platform = platform



def getVersionStrings(xmlfile, product=None):
   """
      Parse a file and return a list of version strings (product name plus version)
   """
   if not os.path.exists(xmlfile):
      raise ValueError, "File %s does not exist" % (xmlfile)
   buildfile = VersionInfo(xmlfile)
   return buildfile.simpleVersionStrings(product)


def getVersionDate(xmlfile, product=None):
   """
      Parse a file and return a list of version dates
   """
   if not os.path.exists(xmlfile):
      raise ValueError, "File %s does not exist" % (xmlfile)
   buildfile = VersionInfo(xmlfile)
   return buildfile.simpleVersionDates(product)


def getTarget(xmlfile):
   """
      Parse a file and return the target value if the file is a 1.0 or 1.1 manifest.
   """
   if not os.path.exists(xmlfile):
      raise ValueError, "File %s does not exist" % (xmlfile)
   buildfile = VersionInfo(xmlfile)
   return buildfile.target()


def getFiles(xmlfile):
   """
      Parse a file and return a list of files with md5 info
   """
   if not os.path.exists(xmlfile):
      raise ValueError, "File %s does not exist" % (xmlfile)
   buildfile = VersionInfo(xmlfile)
   return buildfile.builds()[0].fileinfo


if __name__ == "__main__":

   testfile = "VersionInfo.xml"
   print getFiles(testfile)


   #vinfoobj = VersionInfo()
   #buildobj = vinfoobj.addBuild("Design Premium", "CS4", "Application", "20080311.m.154", "2008/3/11:15:00:00", "None", "Retail", "RIBS Installer", "win32", "en_US,fr_Ca,es_MX,en_GB")
   #buildobj.addMetadata("AdobeCode", "45FB0721-29BD-4C62-98C5-D1396787462F")
   #print vinfoobj.toXML()

