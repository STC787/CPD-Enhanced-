# Add this to your existing models file
from odoo import models, fields, api


class StudentCertification(models.Model):
    _name = 'student.certification'
    _description = 'Student Certification Management'
    _rec_name = 'student_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    student_id = fields.Many2one('op.student', string='Student', tracking=True)
    student_ids = fields.Many2many('op.student', string='Students', )
    name = fields.Char(string='Certificate Name')
    certification_type = fields.Char(string='Certification Type', required=True, tracking=True)
    state = fields.Selection([
        ('active', 'Active'),
        ('expired', 'Expired')
    ], string='State', default='active', tracking=True)

    # Additional useful fields
    description = fields.Text(string='Description')
    issue_date = fields.Date(string='Issue Date', default=fields.Date.context_today)
    expiry_date = fields.Date(string='Date')
    certificate_number = fields.Char(string='Certificate Number', readonly=True)
    course_id = fields.Many2one('op.course', string='Course')
    grade = fields.Selection([
        ('a+', 'A+'),
        ('a', 'A'),
        ('b+', 'B+'),
        ('b', 'B'),
        ('c+', 'C+'),
        ('c', 'C'),
        ('pass', 'Pass'),
        ('fail', 'Fail')
    ], string='Grade')
    score = fields.Float(string='Score (%)', digits=(5, 2))

    def name_get(self):
        """Custom display name for the record"""
        result = []
        for record in self:
            name = f"{record.student_id.name} - {record.certification_type}"
            result.append((record.id, name))
        return result
