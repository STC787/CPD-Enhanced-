from odoo import api, models, fields


class InheritProjectTask(models.Model):
    _inherit = 'project.task'

    company_name = fields.Char(string='Company Name')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    sector = fields.Many2one('masrtech.sub', string='Sector')
    project_requirements = fields.Text(string='Project Description / Requirements')

    def action_make_offer(self):
        return {
            'name': 'Make Offer',
            'view_type': 'form',
            'res_model': 'offer.model',
            'view_id': False,
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'context': {
                'default_task_id': self.id,
            },
        }
