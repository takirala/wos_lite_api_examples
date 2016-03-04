# show what we're doing
set -o verbose

#how to encode your user:password
openssl base64 -in uf_tr_credentials.txt -out b64_uf_tr_credentials.txt

tr_uf_credentials=`cat b64_uf_tr_credentials.txt`

#auth curl require
curl -H "Authorization: Basic ${tr_uf_credentials}" -d "@msg.xml" -X POST  "http://search.webofknowledge.com/esti/wokmws/ws/WOKMWSAuthenticate"

#search
#sample cookie/SID you get back from auth request
#1WXUaeJFVbBPuqLdjue
#curl -H "Cookie: SID=<the SID you get back from auth request goes here>" -d "@search.xml" -X POST  "http://search.webofknowledge.com/esti/wokmws/ws/WokSearchLite"
