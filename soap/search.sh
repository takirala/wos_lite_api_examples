#!/bin/bash

#search
#sample cookie/SID you get back from auth request
#1WXUaeJFVbBPuqLdjue
#curl -H "Cookie: SID=<the SID you get back from auth request goes here>" -d "@search.xml" -X POST  "http://search.webofknowledge.com/esti/wokmws/ws/WokSearchLite"

echo -n "Enter the auth token >"
#read SID
SID = "4WZv8sC3Qini7N5wiqZ"

function perform_search() {
	curl -H "Cookie: SID=<the SID you get back from auth request goes here>" -d "@search.xml" -X POST  "http://search.webofknowledge.com/esti/wokmws/ws/WokSearchLite"
	echo "searched"
}

while :
do
	read next
	if [ "$next" == "exit" ]
	then
		break
	elif [ "$next" == "search" ]
	then
		perform_search
	else
		echo "entered"+$next
	fi
done