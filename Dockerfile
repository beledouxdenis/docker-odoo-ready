FROM ubuntu:focal

ENV LANG C.UTF-8
ENV TERM xterm-256color
ENV DEBIAN_FRONTEND=noninteractive

# APT Install
# hadolint ignore=DL3008,DL3013
RUN apt-get update -y && apt-get upgrade -y                                                                         && \
    apt-get install -y --no-install-recommends curl software-properties-common                                      && \
    # Add repository for older python versions
    add-apt-repository ppa:deadsnakes/ppa                                                                           && \
    # Fetch wkhtmltopdf (for report printing)
    curl -o wkhtmltox.deb -sSL                                                                                         \
    https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.focal_amd64.deb          && \
    # Fetch Google Chrome (for web tour tests)
    curl -o chrome.deb -sSL                                                                                            \
    https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_90.0.4430.93-1_amd64.deb && \
    # Continue install after fetching debs
    apt-get update -y && apt-get install -y --no-install-recommends                                                    \
    # Install iptables to restrict network
    iptables                                                                                                           \
    # Install Python
    python2.7-dev python3.6-dev python3.8-dev                                                                          \
    # Install the Python dependencies for the binaries of this repository
    python3-psycopg2                                                                                                   \
    # Install virtualenv, to be able to have multiple environments according to the different versions of Odoo
    # From Python 3.3, the module venv should be used to create a Python virtual environment, using `python -m venv`
    # Before that, virtualenv should be used
    virtualenv python3.6-venv python3.8-venv                                                                           \
    # Install dependencies required for Odoo python dependencies
    build-essential gcc libpq-dev libxml2-dev libxslt1-dev libsasl2-dev libldap2-dev libssl-dev libjpeg8-dev           \
    zlib1g-dev node-less                                                                                               \
    # Install debugging tools
    ipython3 python3-pudb                                                                                              \
    # Install wkhtmltox
    ./wkhtmltox.deb                                                                                                    \
    # Install Google Chrome
    ./chrome.deb                                                                                                    && \
    # Cleanup
    rm -rf ./wkhtmltox.deb ./chrome.deb /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Virtualenv and PIP install for Odoo from 6.1 to Odoo 10.0
RUN                                                                                                                    \
    virtualenv --python=python2.7 /home/odoo/venvs/6.1                                                              && \
    /home/odoo/venvs/6.1/bin/pip install --no-cache-dir --upgrade pip                                               && \
    /home/odoo/venvs/6.1/bin/pip install --no-cache-dir                                                                \
    # Odoo dependencies
    Babel==2.3.4 decorator==4.0.10 docutils==0.12 ebaysdk==2.1.4 feedparser==5.2.1 gdata==2.0.18 gevent==1.1.2         \
    greenlet==0.4.10 jcconv==0.2.3 Jinja2==2.10.1 lxml==3.5.0 Mako==1.0.4 MarkupSafe==0.23 mock==2.0.0 ofxparse==0.16  \
    passlib==1.6.5 phonenumbers==8.8.1 Pillow==3.4.1 psutil==4.3.1 psycogreen==1.0 psycopg2==2.7.7 pydot==1.2.3        \
    pyOpenSSL==17.5.0 pyparsing==2.1.10 pyPdf==1.13 pyserial==3.1.1 Python-Chart==1.39 python-dateutil==2.5.3          \
    python-ldap==2.4.27 python-openid==2.2.5 pytz==2016.7 pyusb==1.0.0 pywebdav==0.9.8 PyYAML==3.12 qrcode==5.3        \
    reportlab==3.3.0 requests==2.20.0 simplejson==3.17.5 six==1.10.0 suds-jurko==0.6 unittest2 vatnumber==1.2          \
    vobject==0.9.3 Werkzeug==0.11.11 wsgiref==0.1.2 xlrd==1.0.0 XlsxWriter==0.9.3 xlwt==1.1.2                          \
    # Upgrade dependencies
    markdown futures                                                                                                   \
    # Debugging tools
    ipython pudb

# Virtualenv and PIP install for Odoo from 10.0 to Odoo 14.0
RUN                                                                                                                    \
    python3.6 -m venv /home/odoo/venvs/11.0                                                                         && \
    /home/odoo/venvs/11.0/bin/pip install --no-cache-dir --upgrade pip                                              && \
    /home/odoo/venvs/11.0/bin/pip install --no-cache-dir --upgrade "setuptools<58"                                  && \
    /home/odoo/venvs/11.0/bin/pip install --no-cache-dir                                                               \
    # Odoo dependencies
    Babel==2.6.0 chardet==3.0.4 dbfread==2.0.7 decorator==4.3.0 docutils==0.14 ebaysdk==2.1.5 feedparser==5.2.1        \
    firebase-admin==5.0.3 freezegun==0.3.12 gevent==1.3.7 greenlet==0.4.15 html2text==2018.1.9 idna==2.6               \
    Jinja2==2.10.1 libsass==0.17.0 lxml==4.3.2 Mako==1.0.7 MarkupSafe==1.1.0 mock==2.0.0 num2words==0.5.6              \
    ofxparse==0.19 passlib==1.7.1 pdfminer==20191125 phonenumbers==8.9.10 Pillow==5.4.1 polib==1.1.0 psutil==5.6.6     \
    psycopg2==2.8.3 pydot==1.4.1 pyOpenSSL==19.0.0 pyparsing==2.2.0 PyPDF2==1.26.0 pyserial==3.4                       \
    python-dateutil==2.7.3 python-ldap==3.1.0 python-stdnum==1.8 pytz==2019.1 pyusb==1.0.2 PyYAML==3.13 qrcode==6.1    \
    reportlab==3.5.13 requests==2.21.0 suds-jurko==0.6 vatnumber==1.2 vobject==0.9.6.1 websocket-client==0.59.0        \
    Werkzeug==0.16.1 xlrd==1.1.0 XlsxWriter==1.1.2 xlwt==1.3.* zeep==3.2.0                                             \
    # Upgrade dependencies
    markdown simplejson==3.17.5                                                                                        \
    # Debugging tools
    ipython==7.13.0 pudb==2019.2 urwid==2.0.1 jedi==0.15.2

# Virtualenv and PIP install for Odoo from 15.0 to Odoo master
RUN                                                                                                                    \
    python3.8 -m venv /home/odoo/venvs/15.0                                                                         && \
    /home/odoo/venvs/15.0/bin/pip install --no-cache-dir --upgrade pip                                              && \
    /home/odoo/venvs/15.0/bin/pip install --no-cache-dir                                                               \
    # Odoo dependencies
    Babel==2.6.0 chardet==3.0.4 dbfread==2.0.7 decorator==4.4.2 docutils==0.16 ebaysdk==2.1.5 feedparser==5.2.1        \
    firebase-admin==5.0.3 freezegun==0.3.15 gevent==20.9.0 greenlet==0.4.17 html2text==2020.1.16 idna==2.8             \
    Jinja2==2.10.1 libsass==0.18.0 lxml==4.6.1 MarkupSafe==1.1.0 num2words==0.5.6 ofxparse==0.19 passlib==1.7.2        \
    pdfminer==20191125 phonenumbers==8.12.46 Pillow==8.1.2 polib==1.1.0 psutil==5.6.6 psycopg2==2.8.6 pydot==1.4.1     \
    pyopenssl==19.0.0 PyPDF2==1.26.0 pyserial==3.4 python-dateutil==2.7.3 python-ldap==3.2.0 python-stdnum==1.13       \
    pytz==2019.3 pyusb==1.0.2 qrcode==6.1 reportlab==3.5.59 requests==2.22.0 vobject==0.9.6.1 websocket-client==0.59.0 \
    Werkzeug==0.16.1 xlrd==1.2.0 XlsxWriter==1.1.2 xlwt==1.3.* zeep==3.4.0                                             \
    # Upgrade dependencies
    markdown simplejson==3.17.5                                                                                        \
    # Debugging tools
    ipython==7.13.0 pudb==2019.2 urwid==2.0.1 jedi==0.15.2
