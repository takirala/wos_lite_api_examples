#! /usr/bin/python

from lxml import etree
from io import StringIO

import sys
import os.path
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main(argv):
    logger.setLevel(logging.DEBUG)
    fileFound = False

    if len(argv) >= 1:
        logger.debug("File : ", argv[0])
        fileFound = os.path.isfile(argv[0])

    if not fileFound:
        logger.debug("Enter a valid input file")
        sys.exit(0)

    # Read the SOAP Envelope from arguments.
    env = Envelope(argv[0])

    outputName = argv[0].replace('.xml','_mods.xml')
    if(len(argv) > 1):
        outputName = argv[1]

    logger.info("Input file : " + argv[0] + " Output file " + outputName)
    # Parse the required fields.
    env.parseRecords()

    # Process the records.
    env.processRecords(outputName)


class Envelope:
    'Thomas Reuters SOAP Envelope output'

    def __init__(self, input):
        self.input = input;
        envelope = etree.parse(input)
        self.envelope = envelope

    def parseRecords(self):
        content = self.envelope.getroot().find(".//return")

        if content is None:
            logger.debug("No return element parsed.")
            sys.exit(0)

        iter = content.xpath(ns.records)

        records = []
        for e in iter:
            records.append(e)
        self.records = records

    def processRecords(self, outputName):
        self.createModsFile()
        logger.info("Number of records : " + str(len(self.records)))
        for record in self.records:
            mods = self.getMods(record)
            self.modsCollection.append(mods)
        self.writeToFile(outputName)

    def getMods(self, record):
        mods = etree.Element(ns.mods)
        mods.attrib[ns.ID] = record.find(ns.uid).text

        children = record.getchildren()

        sources = {}
        others = {}
        for c in children:
            if c is None:
                logger.error('Empty element found' + c) #Not possible
                continue

            tag = c.tag
            if (tag == ns.title):
                # No need to check the label tag. Single title as of now.
                value = c.find(ns.value).text
                ele = ModsXML.getTitleElement(value)
                if not ele is None:
                    mods.append(ele)

            elif tag == ns.authors:
                # No need to check the label tag. Single title as of now.
                valueItr = c.findall(ns.value)
                for val in valueItr:
                    family = val.text.split(',', 1)[0]
                    given = val.text.split(',')
                    given = given[1:len(given) + 1]
                    name = ModsXML.getAuthor(family, given)
                    mods.append(name)

            elif tag == ns.source or tag == ns.other:
                # We need to parse entire document. Dynamic conversion not feasible.
                # Label is the key, value is the value.
                label = c.find(ns.label).text
                value = c.find(ns.value).text
                if tag == ns.source:
                    sources[label] = value
                else:
                    others[label] = value

        self.updateSources(sources, others, mods)

        return mods

    def updateSources(self, sources, others, mods):

        # Update originInfo element TODO Place information to be parsed
        originInfo = ModsXML.getOriginInfo(sources)
        mods.append(originInfo)

        # Add resource type. TODO only text as of now.
        rsrcType = ModsXML.getResourceType(sources)
        mods.append(rsrcType)

        # add genre element.
        genre = ModsXML.getGenre(sources)
        mods.append(genre)

        # Add language element
        language = ModsXML.getLanguage('English','eng')
        mods.append(language)

        # Add journal information.
        relatedItem = ModsXML.getRelatedItem(sources, others)
        mods.append(relatedItem)

        id = mods.attrib[ns.ID]
        identifer = etree.Element(ns.identifier)
        identifer.attrib[ns.type] = ns.citekey
        identifer.text = id
        mods.append(identifer)

        # TODO Abstract and keywords are not available yet.

        # Update part element - page, issue, volume.
        part = ModsXML.getPart(sources)
        mods.append(part)
        return

    def updateOthers(self, sources, mods):
        return

    def createModsFile(self):
        modsCollection = etree.Element(ns.modsCollection)
        modsCollection.attrib[ns.xmlns] = ns.xmlnsmods
        self.doc = etree.ElementTree(modsCollection)
        self.modsCollection = modsCollection

    def writeToFile(self, outputName):
        logger.debug(etree.tostring(self.doc, pretty_print=True))
        outFile = open(outputName, 'w')
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

        # Multiple given name elements
        for givenName in givenNames:
            given = etree.Element(ns.namePart)
            given.attrib[ns.type] = ns.given
            given.text = givenName.strip()
            name.append(given)

        # Single family name element
        family = etree.Element(ns.namePart)
        family.text = familyName
        family.attrib[ns.type] = ns.family
        name.append(family)

        # Single role element
        role = etree.Element(ns.role)
        role.append(ModsXML.getRoleTerm(ns.marcrelator, ns.type, ns.author))
        name.append(role)

        return name

    @staticmethod
    def getRoleTerm(authority, type, text):
        roleTerm = etree.Element(ns.roleTerm)
        roleTerm.attrib[ns.authority] = authority
        roleTerm.attrib[ns.type] = type
        roleTerm.text = text
        return roleTerm

    @staticmethod
    def getExtent(pages):
        pagesSplit = re.findall(r'\d+', pages)
        start = int(pagesSplit[0])
        end = int(pagesSplit[1])
        extent = etree.Element(ns.extent)
        extent.attrib[ns.unit] = ns.page
        startElement = etree.Element(ns.start)
        endElement = etree.Element(ns.end)
        totalElement = etree.Element(ns.total)
        startElement.text = str(start)
        endElement.text = str(end)
        totalElement.text = str(end - start + 1)
        extent.append(startElement)
        extent.append(endElement)
        extent.append(totalElement)
        return extent

    @staticmethod
    def getDate(sources):
        year = sources[ns.PublishedBiblioYear]
        month = sources[ns.PublishedBiblioDate]
        date = etree.Element(ns.date)
        date.text = year + ' ' + month
        return date

    @staticmethod
    def getDetail(type, number):
        detail = etree.Element(ns.detail)
        detail.attrib[ns.type] = type
        numberElement = etree.Element(ns.number)
        numberElement.text = number
        detail.append(numberElement)
        return detail

    @staticmethod
    def getGenre(sources):
        genre = etree.Element(ns.genre)
        genre.text = ns.journalArticle
        return genre

    @staticmethod
    def getLanguage(text, code):
        language = etree.Element(ns.language)

        langTerm1 = etree.Element(ns.languageTerm)
        langTerm1.attrib[ns.type] = ns.text
        langTerm1.text = text

        langTerm2 = etree.Element(ns.languageTerm)
        langTerm2.attrib[ns.type] = ns.code
        langTerm2.attrib[ns.authority] = ns.iso639_2b
        langTerm2.text = code

        language.append(langTerm1)
        language.append(langTerm2)

        return language

    @staticmethod
    def getRelatedItem(sources, others):
        relatedItem = etree.Element(ns.relatedItem)
        relatedItem.attrib[ns.type] = ns.host

        if ns.SourceTitle in sources:
            journalTitle = ModsXML.getTitleElement(sources[ns.SourceTitle])
            relatedItem.append(journalTitle)


        # Add originInfo with publisher information. TODO

        # Add genre as periodical TODO update dynamically
        genre = etree.Element(ns.genre)
        genre.attrib[ns.authority] = ns.marcgt
        genre.text = ns.periodical
        relatedItem.append(genre)

        # Add genre as academic journal. TODO update dynamically
        genre = etree.Element(ns.genre)
        genre.text = ns.academicArticle
        relatedItem.append(genre)

        if ns.IdentifierIssn in others:
            issn = ModsXML.getIssn(others)
            relatedItem.append(issn)

        return relatedItem


    @staticmethod
    def getIssn(others):
        issn = etree.Element(ns.identifier)
        issn.attrib[ns.type] = ns.issn
        issn.text = others[ns.IdentifierIssn]
        return issn

    @staticmethod
    def getOriginInfo(sources):
        originInfo = etree.Element(ns.originInfo)
        dateIssued = etree.Element(ns.dateIssued)
        dateIssued.text = ModsXML.getDate(sources).text
        originInfo.append(dateIssued)
        # TODO Add place and placeTerm element
        return originInfo

    @staticmethod
    def getResourceType(sources):
        rsrcType = etree.Element(ns.typeOfResource)
        rsrcType.text = ns.text
        return rsrcType

    @staticmethod
    def getPart(sources):

        part = etree.Element(ns.part)

        part.append(ModsXML.getDate(sources))

        # Volume
        if ns.Volume in sources:
            volumeDetail = ModsXML.getDetail(ns.volume, sources[ns.Volume])
            part.append(volumeDetail)

        # Issue
        if ns.Issue in sources:
            volumeDetail = ModsXML.getDetail(ns.issue, sources[ns.Issue])
            part.append(volumeDetail)

        # Extent
        if ns.Pages in sources:
            extent = ModsXML.getExtent(sources[ns.Pages])
            part.append(extent)

        return part

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

    # Sources - input
    Issue = 'Issue'
    Pages = 'Pages'
    PublishedBiblioDate = 'Published.BiblioDate'
    PublishedBiblioYear = 'Published.BiblioYear'
    SourceTitle = 'SourceTitle'
    Volume = 'Volume'

    # Others - input
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
    genre = 'genre'
    typeOfResource = 'typeOfResource'
    originInfo = 'originInfo'
    dateIssued = 'dateIssued'
    language = 'language'
    languageTerm = 'languageTerm'
    code = 'code'
    iso639_2b = 'iso639-2b'
    relatedItem = 'relatedItem'
    host = 'host'
    identifier = 'identifier'
    citekey = 'citekey'
    issn = 'issn'

    # Journal genres
    academicArticle = 'academicArticle'
    periodical = 'periodical'
    marcgt = 'marcgt'

    # Resource Types.
    text = 'text'

    # Genre
    journalArticle = 'journal article'


if __name__ == '__main__':
    main(sys.argv[1:])
