# -*- coding: utf-8 -*-
{
    "name": "runsanitizer",
    "summary": "Clean a client database to be able to run it in a docker container.",
    "description": "See summary.",
    "version": "0.1",
    "author": "Odoo",
    "category": "Internal",
    "website": "http://www.odoo.com",
    "depends": ["base"],
    "installable": True,
    "auto_install": False,
    "application": False,
    "post_init_hook": "_post_init_hook",
}
