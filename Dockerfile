FROM radanalyticsio/openshift-spark

USER root

ADD . /opt/ophicleide

WORKDIR /opt/ophicleide

RUN yum install -y python-pip \
 && pip install setuptools==36.2.5 \
 && pip install -r requirements.txt \
 && pip wheel -r wheel-requirements.txt -w . \
 && mv pymongo*.whl pymongo.zip

USER 185

CMD ./run.sh
