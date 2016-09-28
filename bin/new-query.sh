#!/bin/sh

curl -i -s -H "Content-type: application/json" -X POST -d '{"model": "'$1'", "word": "'$2'" }' http://localhost:8080/queries
