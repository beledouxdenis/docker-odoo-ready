FROM debian:bookworm

ENV DEBIAN_FRONTEND=noninteractive LANG=C.UTF-8 NODE_ENV=production TERM=xterm-256color

RUN apt-get update -y \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
    # Install python dependencies for Odoo
    pylint python3-aiosmtpd python3-asn1crypto python3-astroid python3-babel python3-cbor2 python3-dateutil \
    python3-dbfread python3-decorator python3-dev python3-docopt python3-docutils python3-feedparser python3-fonttools \
    python3-freezegun python3-geoip2 python3-gevent python3-html2text python3-jinja2 python3-jwt python3-libsass \
    python3-lxml python3-mako python3-markdown python3-matplotlib python3-mock python3-num2words python3-ofxparse \
    python3-openid python3-openpyxl python3-openssl python3-passlib python3-pdfminer python3-phonenumbers python3-pil \
    python3-polib python3-psutil python3-psycogreen python3-psycopg2 python3-pydot python3-pyldap python3-pyparsing \
    python3-pypdf2 python3-qrcode python3-renderpm python3-reportlab python3-requests python3-rjsmin \
    python3-setproctitle python3-simplejson python3-slugify python3-stdnum python3-suds python3-tz python3-unittest2 \
    python3-vobject python3-websocket python3-werkzeug python3-xlrd python3-xlsxwriter python3-xlwt python3-xmlsec \
    python3-zeep \
    # Set python3 by default
    python-is-python3 \
    # Install pip and venv, to install python dependencies not packaged by Ubuntu
    python3-pip python3-venv \
    # Install lessc
    node-less \
    # Install npm, to install node dependencies not packaged by Ubuntu
    npm \
    # Install wkhtmltopf
    wkhtmltopdf \
    # Install fonts
    fonts-freefont-ttf fonts-noto-cjk fonts-ocr-b fonts-vlgothic gsfonts \
    # Install Chromium for web tours
    chromium \
    # Install debugging tools
    less vim \
    # Install iptables to restrict network
    iptables \
    # Create a virtual env for PIP dependencies and activate it
    && python -m venv /venv --system-site-packages && . /venv/bin/activate \
    # Upgrade PIP
    && pip install --upgrade pip \
    # Install PIP dependencies for Odoo
    && pip install --no-cache-dir ebaysdk firebase-admin==2.17.0 inotify pdf417gen \
    # Install PIP debug tools
    debugpy ipython pudb \
    # Install node dependencies for Odoo
    && npm install -g rtlcss@2.5.0 \
    # Cleanup
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

    # Activate the virtual env by default, to run Odoo using the virtual env
    ENV PATH="/venv/bin:$PATH"
