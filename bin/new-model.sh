#!/bin/sh

RESULT=$(curl -s -H "Content-type: application/json" -X POST -d '{"name": "'$1'", "callback":  "http://localhost/ignored", "urls": ["'$2'"] }' http://localhost:8080/models | grep -E /models/'[a-f0-9-]+' -o | uniq)

echo http://localhost:8080$RESULT
