from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
        help='Default analytic account for this product'
    )
