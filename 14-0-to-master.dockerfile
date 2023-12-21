FROM ubuntu:jammy

ENV LANG C.UTF-8
ENV TERM xterm-256color
ARG DEBIAN_FRONTEND=noninteractive
ARG NODE_ENV=production
ENV NODE_ENV $NODE_ENV

RUN apt-get update -y \
    && apt-get upgrade -y \
    # Install required package to add an apt repository key
    && apt-get install -y --no-install-recommends ca-certificates gnupg2 wget \
    # Add the Odoo nightly repository key
    && wget -q -O - https://nightly.odoo.com/odoo.key | gpg --dearmor > /usr/share/keyrings/odoo-nightly.gpg \
    # Add the Odoo nightly repository
    && echo 'deb [signed-by=/usr/share/keyrings/odoo-nightly.gpg] http://nightly.odoo.com/deb/jammy ./' \
    > /etc/apt/sources.list.d/odoo-nightly.list \
    # Fetch Google Chrome (for web tour tests)
    && wget -q --show-progres --progress=bar:force:noscroll -O chrome.deb \
    https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_114.0.5735.133-1_amd64.deb \
    # Continue install after fetching debs
    && apt-get update -y \
    && apt-get install -y --no-install-recommends \
    # Install python dependencies for Odoo
    pylint python3-aiosmtpd python3-asn1crypto python3-astroid python3-babel python3-dateutil python3-dbfread \
    python3-decorator python3-dev python3-docopt python3-docutils python3-feedparser python3-fonttools python3-geoip2 \
    python3-gevent python3-html2text python3-jinja2 python3-jwt python3-libsass python3-lxml python3-mako \
    python3-markdown python3-matplotlib python3-mock python3-num2words python3-ofxparse python3-openid python3-openssl \
    python3-passlib python3-pdfminer python3-phonenumbers python3-pil python3-polib python3-psutil python3-psycogreen \
    python3-psycopg2 python3-pydot python3-pyldap python3-pyparsing python3-pypdf2 python3-qrcode python3-reportlab \
    python3-requests python3-rjsmin python3-setproctitle python3-simplejson python3-slugify python3-stdnum \
    python3-suds python3-tz python3-unittest2 python3-vobject python3-websocket python3-werkzeug python3-xlrd \
    python3-xlsxwriter python3-xlwt python3-xmlsec python3-yaml python3-zeep \
    # Set python3 by default
    python-is-python3 \
    # Install pip, to install python dependencies not packaged by Ubuntu
    python3-pip \
    # Install lessc
    node-less \
    # Install npm, to install node dependencies not packaged by Ubuntu
    npm \
    # Install wkhtmltopf
    wkhtmltox \
    # Install fonts
    fonts-freefont-ttf fonts-khmeros-core fonts-noto-cjk fonts-ocr-b fonts-vlgothic gsfonts \
    # Install Google Chrome
    ./chrome.deb \
    # Install debugging tools
    less ipython3 python3-pudb \
    # Install iptables to restrict network
    iptables \
    # Install PIP dependencies for Odoo
    && pip install --no-cache-dir ebaysdk firebase-admin==2.17.0 inotify pdf417gen \
    # Install PIP debug tools
    debugpy \
    # Install node dependencies for Odoo
    && npm install -g rtlcss@2.5.0 \
    # Cleanup
    && rm -rf ./chrome.deb /var/lib/apt/lists/* /tmp/* /var/tmp/*
