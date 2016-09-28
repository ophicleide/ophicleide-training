#!/bin/sh

curl -i -s -H "Content-type: application/json" -X POST -d '{"name": "'$1'", "callback":  "http://localhost/ignored", "urls": ["'$2'"] }' http://localhost:8080/models

