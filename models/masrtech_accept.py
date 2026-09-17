from odoo import api, models, fields


class MasrtechStudentAccept(models.Model):
    _name = 'masrtech.student.accept'

    name = fields.Char(string='Name')
    type = fields.Selection([
        ('training', 'Training'),
        ('job', 'Job Opportunity'),
        ('project', 'Project'),
    ],
        string='type')
    company_id = fields.Many2one('masrtech.factory', string='Company')
    student_name = fields.Many2one('op.student', string='Student')
