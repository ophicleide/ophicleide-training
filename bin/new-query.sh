#!/bin/sh

RESULT=$(curl -s -H "Content-type: application/json" -X POST -d '{"model": "'$1'", "word": "'$2'" }' http://localhost:8080/queries | grep -E /queries/'[a-f0-9-]+' -o | uniq)

curl http://localhost:8080$RESULT
