# wos_lite_api_examples

## What does this tool do?
This tool converts the soapEnvelope format from Thomas Reuters WOS API to MODS XML format. This is a single executable python file that takes mandatory input file argument (soapEnvelope) and an optional output file argument.

## How to run?

Navigate to soap2mods directory and run the below command

    ./soap2mods.py <inputfile> <outputfile>

outputfile argument is optional in the above command. The default convention followed for generating the output file is the '.xml' in input file name is replaced by '_mods.xml' in the output file name.

After the above tool is run, the mods xml file should be generated. This file could be passed to xml2bib tool (courtesy of bibutils) to convert this in to bibtex format.

## Notes

WOS v3.0 API Guide - http://ipscience-help.thomsonreuters.com/wosWebServicesLite/WebServicesLiteOverviewGroup/Introduction.html
