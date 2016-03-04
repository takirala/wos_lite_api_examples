

#how to encode your user:password
#openssl base64 -in user.txt -out user64enc.txt

#auth curl require
curl -H "Authorization: Basic <your user:password base64 encoded>" -d "@msg.xml" -X POST  "http://search.webofknowledge.com/esti/wokmws/ws/WOKMWSAuthenticate"

#search
#sample cookie/SID you get back from auth request
#1WXUaeJFVbBPuqLdjue
curl -H "Cookie: SID=<the SID you get back from auth request goes here>" -d "@search.xml" -X POST  "http://search.webofknowledge.com/esti/wokmws/ws/WokSearchLite"
