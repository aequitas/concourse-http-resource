FROM python:3-alpine as test

# This Dockerfile abuses the multistage build to run a test suite before
# building the actual (lean) docker image.

# install requirements
ADD requirements*.txt setup.cfg ./
RUN apk add --no-cache --virtual .pynacl_deps build-base python3-dev libffi-dev
RUN pip install --no-cache-dir -r requirements.txt -r requirements_dev.txt

# install assets
ADD assets/ /opt/resource/
ADD test/ /opt/resource-tests/

RUN pylama /opt/resource /opt/resource-tests/
RUN py.test -l --tb=short -vv -r fE /opt/resource-tests

# 'clean' all test requirements from the image to have a nice small download
FROM python:3-alpine

# install requirements
ADD requirements*.txt setup.cfg ./
RUN pip install --no-cache-dir -r requirements.txt

# install assets
ADD assets/ /opt/resource/
ADD test/ /opt/resource-tests/
