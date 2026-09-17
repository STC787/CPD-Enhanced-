from odoo import api, models, fields


class OfferModel(models.Model):
    _name = 'offer.model'

    name = fields.Char(string="name")
    description = fields.Text(string="Description")
    state = fields.Selection([('In Progress', 'In Progress'), ('Approved', 'Approved')], string='State')
    task_id = fields.Many2one('offer.model', string='Task')
    email = fields.Char(string='Email Partner')

    def action_send_offer(self):
        pass
