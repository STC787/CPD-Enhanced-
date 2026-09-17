from odoo import api, models, fields


class MasrtechFactoryRegistration(models.Model):
    _name = 'masrtech.factory.registration'

    name = fields.Char(string="name")
    industry = fields.Many2one('masrtech.industry', string='Industry')
    industry_health = fields.Many2one('masrtech.industry.health', string='Industry')
    type = fields.Selection([
        ('health', 'صحة'),
        ('industry', 'صناعة')], default='health', string="Type")
    description = fields.Text(string='Description')
    sector = fields.Selection([
        ('manufacturing', 'Manufacturing'),
        ('technology', 'Technology'),
        ('finance', 'Finance'),
        ('healthcare', 'Healthcare'),
        ('retail', 'Retail'),
        ('other', 'Other')],
        string='Sector')
    founded_date = fields.Date(string='Founded Date')
    website = fields.Char(string='Website')
    contact_name = fields.Char(string='Contact Name')
    contact_email = fields.Char(string='Contact Email')
    contact_phone = fields.Char(string='Contact Phone')
    employees = fields.Integer(string='Number of Employees')
    annual_revenue = fields.Float(string='Annual Revenue')
    country = fields.Char(string='Country')
    city = fields.Char(string='City')
    state = fields.Char(string='State')

