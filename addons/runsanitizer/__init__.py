# -*- coding: utf-8 -*-
import logging
import os

_logger = logging.getLogger(__name__)

try:
    from odoo.addons.base.maintenance.migrations import util
    from odoo.modules.module import get_modules
except ImportError:
    from openerp.addons.base.maintenance.migrations import util
    from openerp.modules.module import get_modules

try:
    from odoo.addons.base.models.assetsbundle import AssetsBundle
except ImportError:
    try:
        from openerp.addons.base.ir.ir_qweb import AssetsBundle
    except ImportError:
        from openerp.addons.web.controllers import main

STANDARD_MODULES = get_modules()


def convert_custom_models_and_fields(cr):
    """
    Convert custom models and fields to manual
    """
    env = util.env(cr)
    with util.custom_module_field_as_manual(env, rollback=False):
        pass


def _post_init_hook(cr, registry):
    convert_custom_models_and_fields(cr)


def is_standard_asset(url, filename):
    """
    Indicates if the asset identified by (url, filename) is a standard one or not
    """

    # check the url refers to a custom module
    if url:
        url_parts = url.split("/", 2)
        if len(url_parts) > 1:
            return url_parts[1] in STANDARD_MODULES

    # check that the filename exists
    if filename:
        return os.path.exists(filename)

    return True


def clean_assets(bundle):
    """
    Filter custom assets from bundle
    """
    # temporary debug traces to see which stylesheets/javascripts will be skipped
    for x in [a for a in bundle.stylesheets + bundle.javascripts if not is_standard_asset(a.url, a._filename)]:
        _logger.info(
            "SKIP :: url:%s filename:%s",
            x.url if x.url else "none",
            x._filename if x._filename else "none",
        )

    # filter the bundle
    bundle.stylesheets = [a for a in bundle.stylesheets if is_standard_asset(a.url, a._filename)]
    bundle.javascripts = [a for a in bundle.javascripts if is_standard_asset(a.url, a._filename)]


# monkey-patch assets provider to filter out custom ones
if util.version_gte("8.0"):
    old_init = AssetsBundle.__init__

    def new_init(self, *k, **kw):
        old_init(self, *k, **kw)
        clean_assets(self)

    AssetsBundle.__init__ = new_init
else:
    old_manifest_glob = main.manifest_glob

    def new_manifest_glob(req, extension, addons=None, db=None):
        assets = old_manifest_glob(req, extension, addons, db)

        if extension in ("js", "css"):
            # temporary debug traces to see which stylesheets/javascripts will be skipped
            for filename, url in [(fs, url) for fs, url in assets if not is_standard_asset(url, fs)]:
                _logger.info(
                    "SKIP :: url:%s filename:%s",
                    url if url else "none",
                    filename if filename else "none",
                )
            assets = [x for x in assets if is_standard_asset(url=x[1], filename=x[0])]

        return assets

    main.manifest_glob = new_manifest_glob
