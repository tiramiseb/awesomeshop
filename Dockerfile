FROM python:2.7-alpine

ADD . /awesomeshop

RUN apk update && \
    apk add --update \
        gcc \
        git \
        libjpeg-turbo \
        jpeg-dev \
        libffi \
        libffi-dev \
        libpng \
        libpng-dev \
        linux-headers \
        musl-dev \
        nodejs \
        openssl-dev \
        python-dev \
        zlib-dev && \
    pip install -r /awesomeshop/requirements.txt && \
    pip install uwsgi && \
    npm install -g bower && \
    cd /awesomeshop && \
    sed -i 's/bower install/bower --allow-root install/' init_webroot.sh && \
    ./init_webroot.sh && \
    apk del gcc \
            git \
            jpeg-dev \
            libffi-dev \
            libpng-dev \
            linux-headers \
            musl-dev \
            nodejs \
            openssl-dev \
            python-dev \
            zlib-dev

VOLUME /awesomeshop/webroot

CMD ["uwsgi", "--socket", ":3031", "--wsgi-file", "/awesomeshop/wsgi.py", "--callable", "app", "--master"]
