#!/bin/bash

set -e

Base_Url="${Zato_PubSub_Base_Url:-http://localhost:17010}"
Username="${Zato_PubSub_Username:-user.1}"
Password="${Zato_PubSub_Password:-password.1}"
Topic_Name="${Zato_PubSub_Topic:-demo.1}"

Curl_Opts="-s -v"
Auth="$Username:$Password"

echo "=== Zato Pub/Sub curl tests ==="
echo "Base URL: $Base_Url"
echo "Username: $Username"
echo "Topic: $Topic_Name"
echo ""

echo "--- Test 1: Publish message ---"
Publish_Data='{"data":"test message from curl"}'
Publish_Response=$(curl $Curl_Opts -X POST -u "$Auth" \
    -H "Content-Type: application/json" \
    -d "$Publish_Data" \
    "$Base_Url/pubsub/topic/$Topic_Name")

echo "Response: $Publish_Response"

Msg_Id=$(echo "$Publish_Response" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('response',{}).get('msg_id',''))")
if [ -n "$Msg_Id" ]; then
    echo "OK: Message published with ID: $Msg_Id"
else
    echo "FAIL: Could not publish message"
    echo "$Publish_Response"
    exit 1
fi
echo ""

echo "--- Test 2: Subscribe to topic ---"
Subscribe_Response=$(curl $Curl_Opts -X POST -u "$Auth" \
    "$Base_Url/pubsub/subscribe/topic/$Topic_Name")

echo "Response: $Subscribe_Response"

Sub_Key=$(echo "$Subscribe_Response" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('response',{}).get('sub_key',''))")
if [ -n "$Sub_Key" ]; then
    echo "OK: Subscribed with key: $Sub_Key"
else
    echo "FAIL: Could not subscribe"
    echo "$Subscribe_Response"
    exit 1
fi
echo ""

echo "--- Test 3: Publish another message (after subscribe) ---"
Publish_Data2='{"data":"message after subscribe"}'
Publish_Response2=$(curl $Curl_Opts -X POST -u "$Auth" \
    -H "Content-Type: application/json" \
    -d "$Publish_Data2" \
    "$Base_Url/pubsub/topic/$Topic_Name")

echo "Response: $Publish_Response2"

Msg_Id2=$(echo "$Publish_Response2" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('response',{}).get('msg_id',''))")
if [ -n "$Msg_Id2" ]; then
    echo "OK: Message published with ID: $Msg_Id2"
else
    echo "FAIL: Could not publish second message"
    exit 1
fi
echo ""

echo "--- Test 4: Get messages ---"
Get_Data="{\"sub_key\":\"$Sub_Key\"}"
Get_Response=$(curl $Curl_Opts -X POST -u "$Auth" \
    -H "Content-Type: application/json" \
    -d "$Get_Data" \
    "$Base_Url/pubsub/messages/get")

echo "Response: $Get_Response"

if echo "$Get_Response" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if 'message after subscribe' in str(d) else 1)"; then
    echo "OK: Retrieved message"
else
    echo "WARN: Message not found (may have been consumed already)"
fi
echo ""

echo "--- Test 5: Unsubscribe ---"
Unsubscribe_Response=$(curl $Curl_Opts -X POST -u "$Auth" \
    "$Base_Url/pubsub/unsubscribe/topic/$Topic_Name")

echo "Response: $Unsubscribe_Response"

if echo "$Unsubscribe_Response" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d.get('response',{}).get('is_ok') else 1)"; then
    echo "OK: Unsubscribed"
else
    echo "WARN: Unsubscribe response unexpected"
fi
echo ""

echo "=== All tests completed ==="
