# Mostly copied from https://www.github.com/Wonderfall/docker-searx

FROM alpine:3.10

RUN apk -U upgrade \
 && apk add -t build-dependencies \
    build-base \
    python3-dev \
    py3-setuptools \
    libffi-dev \
    libxslt-dev \
    libxml2-dev \
    openssl-dev \
    tar \
    ca-certificates \
    git \
 && apk add \
    su-exec \
    python3 \
    libxml2 \
    libxslt \
    openssl

RUN mkdir /usr/local/searx && cd /usr/local \
 && git clone -b master --single-branch https://github.com/asciimoo/searx.git\
 && cd searx\
 && pip3 install --upgrade setuptools \
 && pip3 install --no-cache -r requirements.txt \
 && sed -i "s/127.0.0.1/0.0.0.0/g" searx/settings.yml \
 && SEARX_GIT_VERSION=$(git describe --match "v[0-9]*\.[0-9]*\.[0-9]*" HEAD 2>/dev/null | awk -F'-' '{OFS="-"; $1=substr($1, 2); $3=substr($3, 2); print}') \
 && echo "VERSION_STRING = '$SEARX_GIT_VERSION'" >> searx/version.py \
 && apk del build-dependencies \
 && rm -f /var/cache/apk/*

EXPOSE 8888

ENTRYPOINT ["python3", "/usr/local/searx/searx/webapp.py"]
