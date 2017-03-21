#!/usr/bin/env python
import sys
import os
import requests

#WOK_SEARCH_URL = 'http://search.isiknowledge.com/esti/wokmws/ws/WokSearch'
WOK_SEARCH_URL = 'http://search.webofknowledge.com/esti/wokmws/ws/WokSearchLite'

class Template():
    search_template = '''
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
            xmlns:woksearchlite="http://woksearchlite.v3.wokmws.thomsonreuters.com">
            <soapenv:Header/>
            <soapenv:Body>
            <woksearchlite:search>
                 <queryParameters>
                    <databaseId>{databaseId}</databaseId>
                    <userQuery>{userQuery}</userQuery>
                    <editions>
                       <collection>{collection}</collection>
                       <edition>{edition}</edition>
                    </editions>
                    <timeSpan>
                        <begin>{begin}</begin>
                        <end>{end}</end>
                    </timeSpan>
                    <queryLanguage>{queryLanguage}</queryLanguage>
                 </queryParameters>
                 <retrieveParameters>
                    <firstRecord>{firstRecord}</firstRecord>
                    <count>{count}</count>
                 </retrieveParameters>     
            </woksearchlite:search>
            </soapenv:Body>
        </soapenv:Envelope>
    '''

def perform_date_search(SID):
    params = {}
    params['databaseId'] = 'WOS'
    params['collection'] = 'WOS'
    params['edition'] = 'SCI'
    params['queryLanguage'] = 'en'
    params['userQuery'] = raw_input('Enter query: ')
    params['begin'] = raw_input('Enter start date in format YYYY-MM-DD: ')
    params['end'] = raw_input('Enter end date in format YYYY-MM-DD: ')
    params['firstRecord'] = '1'
    params['count'] = '1'

    headers = {'Cookie': 'SID='+SID}
    data = Template.search_template.format(**params)
    result = requests.post(WOK_SEARCH_URL, data=data, headers=headers)
    #print(result.text)
    print(find_parameter(result.text, 'queryId'))
    print(find_parameter(result.text, 'recordsFound'))
    print(find_parameter(result.text, 'recordsSearched'))

def find_parameter(body, param):
    try:
        start = '<' + param + '>';
        end = '</' + param + '>';
        startIndex = body.index(start)    
        endIndex = body.index(end)
        return body[startIndex:endIndex]
    except ValueError:
        return ""

def main():
    SID = raw_input('Enter the auth token: ')
    perform_date_search(SID)


if __name__ == '__main__':
    main()