from odoo import models, fields, api
from odoo.exceptions import UserError


class SimpleDashboard(models.Model):
    _name = 'simple.dashboard'
    _description = 'Simple Dashboard'

    title = fields.Char('Title')
    description = fields.Text('Description')

    target_model = fields.Char('Target Model')
    select_title = fields.Selection(
        [('Register New', 'Register New'), ('Course', 'Course'), ('Expert', 'Expert'), ('Review Certs', 'Review Certs')
         ])

    def action_view_records(self):
        self.ensure_one()

        if self.select_title == 'Register New':
            return {
                'name': 'Students',
                'type': 'ir.actions.act_window',
                'res_model': 'op.student',
                'view_mode': 'kanban,tree,form',
                'target': 'current',
            }
        elif self.select_title == 'Course':
            return {
                'name': 'Courses',
                'type': 'ir.actions.act_window',
                'res_model': 'op.course',
                'view_mode': 'kanban,tree,form',
                'target': 'current',
            }
        elif self.select_title == 'Expert':
            return {
                'name': 'Experts',
                'type': 'ir.actions.act_window',
                'res_model': 'op.faculty',
                'view_mode': 'kanban,tree,form',
                'target': 'current',
            }
        elif self.select_title == 'Review Certs':
            return {
                'name': 'Certification',
                'type': 'ir.actions.act_window',
                'res_model': 'student.certification',
                'view_mode': 'kanban,tree,form',
                'target': 'current',
            }
        else:
            return {
            'name': 'General INP',

                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Info',
                    'message': f'No specific action configured for {self.title}',
                    'type': 'info',
                }
            }
