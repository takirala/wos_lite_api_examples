#! /usr/bin/python

from lxml import etree
from io import StringIO

import sys
import os.path
import re
import logging


# logger = logging.getLogger(__name__)

def main(argv):
    # logger.setLevel(logging.DEBUG)
    fileFound = False

    if len(argv) >= 1:
        print "File : ", argv[0]
        fileFound = os.path.isfile(argv[0])

    if not fileFound:
        # logger.debug("Enter a valid input file")
        sys.exit(0)

    # Read the SOAP Envelope from arguments.
    env = Envelope("sample_output.xml")

    # Parse the required fields.
    env.parseRecords()

    # Process the records.
    env.processRecords()


class Envelope:
    'Thomas Reuters SOAP Envelope output'
    def __init__(self, input):
        self.input = input;
        envelope = etree.parse(input)
        self.envelope = envelope

    def parseRecords(self):
        content = self.envelope.getroot().find(".//return")

        if content is None:
            print "No return element parsed."
            sys.exit(0)

        iter = content.xpath(ns.records)

        records = []
        for e in iter:
            records.append(e)
        self.records = records

    def processRecords(self):
        self.createModsFile()
        print len(self.records)
        for record in self.records:
            mods = self.getMods(record)
            self.modsCollection.insert(-1, mods)
        self.writeToFile()

    def getMods(self, record):
        mods = etree.Element(ns.mods)
        mods.attrib[ns.ID] = record.find(ns.uid).text

        children = record.getchildren()

        sources = {}
        others = {}
        for c in children:
            if c is None:
                print 'Empty'
                continue

            tag = c.tag
            if (tag == ns.title):
                # No need to check the label tag. Single title as of now.
                value = c.find(ns.value).text
                ele = ModsXML.getTitleElement(value)
                if not ele is None:
                    mods.insert(0, ele)

            elif tag == ns.authors:
                # No need to check the label tag. Single title as of now.
                valueItr = c.findall(ns.value)
                for val in valueItr:
                    family = val.text.split(',', 1)[0]
                    given = val.text.split(',')
                    given = given[1:len(given) + 1]
                    name = ModsXML.getAuthor(family, given)
                    mods.insert(-1, name)

            elif tag == ns.source or tag == ns.other:
                # We need to parse entire document. Dynamic conversion not feasible.
                # Label is the key, value is the value.
                label = c.find(ns.label).text
                value = c.find(ns.value).text
                if tag == ns.source:
                    sources[label] = value
                else:
                    others[label] = value
            else:
                print 'Not yet handled ', tag
        self.updateSources(sources, mods)
        self.updateOthers(others, mods)

        return mods

    def updateSources(self, sources, mods):

        # Update part element - page, issue, volume.
        part = Envelope.getPart(sources)
        mods.insert(-1,part)
        return

    def updateOthers(self, sources, mods):
        return

    @staticmethod
    def getPart(sources):

        part = etree.Element(ns.part)
        year = sources[ns.PublishedBiblioYear]
        month = sources[ns.PublishedBiblioDate]
        date = etree.Element(ns.date)
        date.text = year + ' ' + month

        part.insert(-1,date)

        # Volume
        if not sources[ns.Volume] is None:
            volumeDetail = Envelope.getDetail(ns.volume, sources[ns.Volume])
            part.insert(-1,volumeDetail)

        # Issue
        if not sources[ns.Issue] is None:
            volumeDetail = Envelope.getDetail(ns.issue, sources[ns.Issue])
            part.insert(-1, volumeDetail)

        # Extent
        if not sources[ns.Pages] is None:
            extent = Envelope.getExtent(sources[ns.Pages])
            part.insert(-1, extent)

        return part

    @staticmethod
    def getDetail(type, number):
        detail = etree.Element(ns.detail)
        detail.attrib[ns.type] = type
        numberElement = etree.Element(ns.number)
        numberElement.text = number
        detail.insert(0,numberElement)
        return detail

    @staticmethod
    def getExtent(pages):

        #pagesSplit = pages.split('-')
        pagesSplit = re.findall(r'\d+', pages)
        print pagesSplit
        start = int(pagesSplit[0])
        end = int(pagesSplit[1])
        extent = etree.Element(ns.extent)
        extent.attrib[ns.unit] = ns.page
        startElement = etree.Element(ns.start)
        endElement = etree.Element(ns.end)
        totalElement = etree.Element(ns.total)
        startElement.text = str(start)
        endElement.text = str(end)
        totalElement.text = str(end - start)
        extent.insert(0,totalElement)
        extent.insert(0,endElement)
        extent.insert(0,startElement)
        return extent

    def createModsFile(self):
        modsCollection = etree.Element(ns.modsCollection)
        modsCollection.attrib[ns.xmlns] = ns.xmlnsmods
        self.doc = etree.ElementTree(modsCollection)
        self.modsCollection = modsCollection

    def writeToFile(self):
        print(etree.tostring(self.doc, pretty_print=True))
        outFile = open(self.input + "-python.xml", 'w')
        self.doc.write(outFile, xml_declaration=True)




class ModsXML:
    @staticmethod
    def getTitleElement(titleStr):
        titleInfo = etree.Element(ns.titleInfo)
        title = etree.SubElement(titleInfo, ns.title)
        title.text = titleStr
        return titleInfo

    @staticmethod
    def getAuthor(familyName, givenNames=[]):
        name = etree.Element(ns.name)
        name.attrib[ns.type] = ns.personal
        for givenName in givenNames:
            given = etree.Element(ns.namePart)
            given.attrib[ns.type] = ns.given
            given.text = givenName.strip()
            name.insert(-1, given)

        family = etree.Element(ns.namePart)
        family.text = familyName
        family.attrib[ns.type] = ns.family
        name.insert(-1, family)
        role = etree.Element(ns.role)
        role.insert(-1, ModsXML.getRoleTerm(ns.marcrelator, ns.type, ns.author))
        name.insert(-1, role)
        return name

    @staticmethod
    def getRoleTerm(authority, type, text):
        roleTerm = etree.Element(ns.roleTerm)
        roleTerm.attrib[ns.authority] = authority
        roleTerm.attrib[ns.type] = type
        roleTerm.text = text
        return roleTerm


class ns:

    # Input related tags
    label = 'label'
    xmlns = 'xmlns'
    xmlnsmods = 'http://www.loc.gov/mods/v3'
    modsCollection = 'modsCollection'
    ID = 'ID'
    uid = 'uid'
    mods = 'mods'
    records = 'records'
    title = 'title'
    source = 'source'
    authors = 'authors'
    other = 'other'
    value = 'value'

    #Sources - input
    Issue = 'Issue'
    Pages = 'Pages'
    PublishedBiblioDate = 'Published.BiblioDate'
    PublishedBiblioYear = 'Published.BiblioYear'
    SourceTitle = 'SourceTitle'
    Volume = 'Volume'

    #Others - input
    IdentifierEissn = 'Identifier.Eissn'
    IdentifierIds = 'Identifier.Ids'
    IdentifierIssn = 'Identifier.Issn'
    ResearcherIDDisclaimer = 'ResearcherID.Disclaimer'

    # Output related tags
    # Mods XML Tags
    titleInfo = 'titleInfo'
    marcrelator = 'marcrelator'
    type = 'type'
    author = 'author'
    roleTerm = 'roleTerm'
    authority = 'authority'
    name = 'name'
    personal = 'personal'
    given = 'given'
    family = 'family'
    role = 'role'
    namePart = 'namePart'
    part = 'part'
    date = 'date'
    issue = 'issue'
    volume = 'volume'
    page = 'page'
    unit = 'unit'
    start = 'start'
    end = 'end'
    total = 'total'
    number = 'number'
    detail = 'detail'
    extent = 'extent'


if __name__ == '__main__':
    main(sys.argv[1:])
