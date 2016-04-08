from lxml import etree
from io import StringIO

import sys
import os.path
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
        for c in children:
            self.getForChild(c)

        return mods

    def getForChild(self, src):
        if src is None:
            print 'Empty'
            return

        tag = src.tag
        if(tag == ns.title):
            print tag
        elif tag == ns.source:
            print tag
        elif tag == ns.authors:
            print tag
        elif tag == ns.other:
            print tag
        else:
            print 'Not yet handled ', tag


    def createModsFile(self):
        modsCollection = etree.Element(ns.modsCollection)
        modsCollection.attrib[ns.xmlns] = ns.xmlnsmods
        self.doc = etree.ElementTree(modsCollection)
        self.modsCollection = modsCollection

    def writeToFile(self):
        outFile = open(self.input + "-python.xml", 'w')
        self.doc.write(outFile,xml_declaration=True)


class ns:
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

if __name__ == '__main__':
    main(sys.argv[1:])