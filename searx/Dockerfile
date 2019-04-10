# Mostly copied from https://www.github.com/Wonderfall/docker-searx
# /config URL doesn't work with python3 : switch back to python2

FROM alpine:3.9

RUN apk -U upgrade \
 && apk add -t build-dependencies \
    build-base \
    python2-dev \
    libffi-dev \
    libxslt-dev \
    libxml2-dev \
    openssl-dev \
    tar \
    ca-certificates \
    git\
    py2-pip\
 && apk add \
    su-exec \
    python2 \
    libxml2 \
    libxslt \
    openssl \
 && mkdir /usr/local/searx && cd /usr/local \
 && git clone --depth=1 https://github.com/asciimoo/searx.git\
 && cd searx\
 && pip install --upgrade setuptools \
 && pip install --no-cache -r requirements.txt \
 && sed -i "s/127.0.0.1/0.0.0.0/g" searx/settings.yml \
 && echo "VERSION_STRING = VERSION_STRING + '.$(git log --format="%H" -n 1)'" >> searx/version.py \
 && apk del build-dependencies \
 && rm -f /var/cache/apk/*

EXPOSE 8888

ENTRYPOINT ["python", "/usr/local/searx/searx/webapp.py"]
