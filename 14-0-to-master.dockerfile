FROM ubuntu:jammy

ENV LANG C.UTF-8
ENV TERM xterm-256color
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y \
    && apt-get upgrade -y \
    # Install required package to add an apt repository key
    && apt-get install -y --no-install-recommends ca-certificates gnupg2 wget \
    # Add the Odoo nightly repository key
    && wget -qO - https://nightly.odoo.com/odoo.key | apt-key add - \
    # Add the Odoo nightly repository
    && echo 'deb http://nightly.odoo.com/deb/jammy ./' > /etc/apt/sources.list.d/odoo.list \
    # Fetch Google Chrome (for web tour tests)
    && wget -qO chrome.deb \
    https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_101.0.4951.64-1_amd64.deb \
    # Continue install after fetching debs
    && apt-get update -y \
    && apt-get install -y --no-install-recommends \
    # Install python dependencies for Odoo
    python3-aiosmtpd python3-asn1crypto python3-babel python3-dateutil python3-dbfread python3-decorator python3-dev \
    python3-docopt python3-docutils python3-feedparser python3-fonttools python3-geoip2 python3-gevent \
    python3-html2text python3-jinja2 python3-jwt python3-libsass python3-lxml python3-mako python3-markdown \
    python3-matplotlib python3-mock python3-num2words python3-ofxparse python3-openid python3-openssl python3-passlib \
    python3-pdfminer python3-phonenumbers python3-pil python3-pip python3-polib python3-psutil python3-psycogreen \
    python3-psycopg2 python3-pydot python3-pyldap python3-pyparsing python3-pypdf2 python3-qrcode python3-reportlab \
    python3-requests python3-rjsmin python3-setproctitle python3-simplejson python3-slugify python3-stdnum \
    python3-suds python3-tz python3-unittest2 python3-vobject python3-websocket python3-werkzeug python3-xlrd \
    python3-xlsxwriter python3-xlwt python3-xmlsec python3-yaml python3-zeep \
    # Set python3 by default
    python-is-python3 \
    # Install lessc
    node-less \
    # Install wkhtmltopf
    wkhtmltox \
    # Install fonts
    fonts-freefont-ttf fonts-khmeros-core fonts-noto-cjk fonts-ocr-b fonts-vlgothic gsfonts \
    # Install Google Chrome
    ./chrome.deb \
    # Install debugging tools
    ipython3 python3-pudb \
    # Install iptables to restrict network
    iptables \
    # Install PIP depdendencies for Odoo
    && pip install --no-cache-dir ebaysdk firebase-admin==2.17.0 pdf417gen \
    # Cleanup
    && rm -rf ./chrome.deb /var/lib/apt/lists/* /tmp/* /var/tmp/*
