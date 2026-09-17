from odoo import api, models, fields


class MasrtechRegistration(models.Model):
    _name = 'masrtech.registration'

    name = fields.Char(string='Name', required=True)
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    country = fields.Char(string="Country")
    city = fields.Char(string="City")
    address = fields.Text(string='Address')
    type = fields.Selection([
        ('supplier', 'Supplier'),
        ('distributor', 'Distributor'),
        ('service_provider', 'Service Provider'),
        ('other', 'Other')],
        string='Type')

    web_link = fields.Char(string="website")
    contact_person = fields.Char(string='Contact Person')
    notes = fields.Html(string='Notes')
    # tags = fields.Many2many('partner.tag', string='Tags')
    financial_info = fields.Text(string='Financial Information')
    date_registered = fields.Date(string='Date Registered')
    active = fields.Boolean(string='Active')
    image = fields.Binary(string='Image', attachment=True)


class Masrtechint(models.Model):
    _name = 'masrtech.int'

    name = fields.Char(string='Name', required=True)


class MasrtechSub(models.Model):
    _name = 'masrtech.sub'

    name = fields.Char(string='Name', required=True)

    def go_to_factories(self):
        return {
            'name': self.name,
            'domain': [('type_sub.id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'masrtech.factory',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'type': 'ir.actions.act_window',
        }
