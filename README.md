# ophicleide-training
model training component for Ophicleide 

# Testing
Ophicleide uses tox for testing. A dockerfile *dockerfile-ci* is provided that configures all required dependencies and runs the tests.

To use this dockerfile execute `docker build -t ophicleide-training-ci . -f Dockerfile-ci`

To run the tests without docker simply run `tox` 
