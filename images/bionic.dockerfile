FROM ubuntu:bionic

ENV LANG C.UTF-8
ENV TERM xterm-256color
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y \
    && apt-get upgrade -y \
    # Install required package to add an apt repository key
    && apt-get install -y --no-install-recommends ca-certificates gnupg2 wget \
    # Add the Odoo nightly repository key
    && wget -q -O - https://nightly.odoo.com/odoo.key | gpg --dearmor > /usr/share/keyrings/odoo-nightly.gpg \
    # Add the Odoo nightly repository
    && echo 'deb [signed-by=/usr/share/keyrings/odoo-nightly.gpg] http://nightly.odoo.com/deb/bionic ./' \
    > /etc/apt/sources.list.d/odoo-nightly.list \
    # Fetch Google Chrome (for web tour tests)
    && wget -q --show-progres --progress=bar:force:noscroll -O chrome.deb \
    https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_114.0.5735.133-1_amd64.deb \
    # Continue install after fetching debs
    && apt-get update -y \
    && apt-get install -y --no-install-recommends \
    # Install python2 dependencies for Odoo
    python-dev python-babel python-dateutil python-decorator python-docopt python-docutils python-feedparser \
    python-gdata python-geoip2 python-gevent python-html2text python-jinja2 python-ldap python-libxslt1 python-lxml \
    python-mako python-markdown python-matplotlib python-mock python-ofxparse python-openid python-passlib \
    python-phonenumbers python-psutil python-psycogreen python-psycopg2 python-pychart \
    python-pydot python-pyldap python-pyparsing python-pypdf2 python-reportlab python-requests python-setproctitle \
    python-setuptools python-simplejson python-slugify python-sphinx-patchqueue python-tz python-unittest2 \
    python-vatnumber python-vobject python-webdav python-werkzeug python-xlrd python-xlsxwriter python-xlwt \
    python-yaml python-zsi \
    # Install python3 dependencies for Odoo
    python3-babel python3-dateutil python3-dbfread python3-decorator python3-dev python3-docopt python3-docutils \
    python3-feedparser python3-fonttools python3-geoip2 python3-gevent python3-html2text python3-jinja2 \
    python3-libsass python3-lxml python3-mako python3-markdown python3-matplotlib python3-mock python3-ofxparse \
    python3-openid python3-openssl python3-passlib python3-phonenumbers python3-pil python3-polib \
    python3-psutil python3-psycopg2 python3-pydot python3-pyldap python3-pyparsing python3-pypdf2 python3-reportlab \
    python3-requests python3-setproctitle python3-simplejson python3-slugify python3-tz python3-unittest2 \
    python3-vatnumber python3-vobject python3-websocket python3-werkzeug python3-xlrd python3-xlsxwriter python3-yaml \
    # Install pip, to install python dependencies not packaged by Ubuntu
    python-pip python3-pip \
    # Install lessc
    node-less \
    # Install npm, to install node dependencies not packaged by Ubuntu
    npm \
    # Install wkhtmltopf
    wkhtmltox \
    # Install fonts
    fonts-freefont-ttf fonts-khmeros-core fonts-noto-cjk fonts-ocr-b fonts-vlgothic \
    # Install Google Chrome
    ./chrome.deb \
    # Install debugging tools
    less ipython python-pudb ipython3 python3-pudb \
    # Install iptables to restrict network
    iptables \
    # Install PIP2 depdendencies for Odoo
    && pip install --no-cache-dir ebaysdk==2.1.4 pyPdf==1.13 Pillow==3.4.1 suds-jurko==0.6 \
    # Install PIP2 debug tools
    debugpy \
    # Upgrade PIP3 and setuptools
    && pip3 install --no-cache-dir --upgrade pip "setuptools<58" \
    # Install PIP3 depdendencies for Odoo
    && pip3 install --no-cache-dir \
    ebaysdk==2.1.5 firebase-admin==2.17.0 num2words==0.5.10 suds-jurko==0.6 xlwt==1.3.* zeep==3.2.0 \
    # Install PIP3 debug tools
    debugpy \
    # Install node dependencies for Odoo
    && npm install -g rtlcss@2.4.0 \
    # Cleanup
    && rm -rf ./chrome.deb /var/lib/apt/lists/* /tmp/* /var/tmp/*
