FROM python:3-alpine

ARG SEARXCHECKER_GID=1005
ARG SEARXCHECKER_UID=1005

WORKDIR /usr/local/searx-checker/

RUN addgroup -g ${SEARXCHECKER_GID} searxchk && \
    adduser -u ${SEARXCHECKER_UID} -D -h /usr/local/searx-checker -s /bin/sh -G searxchk searxchk

COPY requirements.txt ./

RUN apk -U upgrade \
 && apk add \
    su-exec \
    tini \
 && pip3 install --upgrade pip \
 && pip3 install --no-cache -r requirements.txt \
 && rm -f /var/cache/apk/*

COPY --chown=searxchk:searxchk . /usr/local/searx-checker

ENTRYPOINT [ "/sbin/tini", "--", "/usr/local/searx-checker/docker-entrypoint.sh" ]
