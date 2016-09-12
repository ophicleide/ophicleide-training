FROM radanalyticsio/openshift-spark

USER root

ADD . /opt/ophicleide

RUN yum install -y centos-release-scl epel-release gcc \
    && yum-config-manager --enable rhel-server-rhscl-7-rpms \
    && yum install -y rh-python35  \
    && scl enable rh-python35 "pip install -r /opt/ophicleide/requirements.txt"

CMD cd /opt/ophicleide && scl enable rh-python35 ./run.sh