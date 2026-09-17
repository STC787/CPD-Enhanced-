from odoo import models, fields, api
from odoo.tools import html_escape
from urllib.parse import urlparse


class IframeEdx(models.Model):
    _name = 'iframe.edx'

    name = fields.Char(string="Website URL")
    iframe_code = fields.Html(string="Iframe Preview", sanitize=True, sanitize_tags=True,
                              sanitize_attributes=True, compute="_compute_iframe_code")

    @api.onchange('name')
    def _compute_iframe_code(self):
        for rec in self:
            if rec.name:
                url = str(rec.name).strip()
                parsed = urlparse(url)
                if parsed.scheme in ('javascript', 'vbscript', 'data') or not parsed.scheme:
                    rec.iframe_code = ''
                    return
                # Only http(s) sources are permitted; escape to prevent attribute injection
                rec.iframe_code = f"""
                                                <iframe 
                                                    title="Viewer" 
                                                    width="600" 
                                                    height="373.5" 
                                                    src="{html_escape(url)}" 
                                                    frameborder="0" 
                                                    allowFullScreen="true"
                                                    class="embed-responsive-item">
                                                </iframe>
                                            """
            else:
                rec.iframe_code = ""
