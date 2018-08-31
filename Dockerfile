FROM ubuntu:18.04

ADD requirements.txt setup.py package/

RUN apt-get update && \
    apt-get install -y --no-install-suggests --no-install-recommends ca-certificates git \
        python3 python3-dev python3-distutils python3-numpy cython3 libxml2 libxml2-dev \
        libsnappy1v5 libsnappy-dev make gcc g++ curl openjdk-8-jre && \
    apt-get clean && \
    curl https://bootstrap.pypa.io/get-pip.py | python3 && \
    pip3 install --no-cache-dir -r package/requirements.txt && \
    apt-get remove -y python3-dev libxml2-dev libsnappy-dev make gcc curl && \
    apt-get autoremove -y

ADD vecino package/vecino
RUN pip3 install -e ./package
RUN vecino ./package || true

ENTRYPOINT ["vecino"]
