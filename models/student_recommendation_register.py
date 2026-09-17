from odoo import api, models, fields


class MasrtechTraingRegister(models.Model):
    _name = 'masrtech.training.registration'
    _rec_name = 'student_name'

    student_name = fields.Many2one('op.student', string='Student')
    student_id = fields.Char(string='Student ID', related='student_name.student_id', readonly=False)
    gender = fields.Selection([
        ('m', 'Male'),
        ('f', 'Female'),
    ], 'Gender', default='m', related='student_name.gender', readonly=False)
    birth_date = fields.Date(string='Birth Date', related='student_name.birth_date', readonly=False)
    email = fields.Char(string='Email', related='student_name.email', readonly=False)
    mobile = fields.Char(string='Mobile', related='student_name.mobile', readonly=False)
    university = fields.Many2one('masrtech.universities', string='University', related='student_name.university',
                                 readonly=False)
    faculty = fields.Many2one('masrtech.faculty', string='College', related='student_name.faculty', readonly=False)
    department = fields.Many2one('op.department', string='Department', related='student_name.department',
                                 readonly=False)
    semester = fields.Integer(string='Current Semester', related='student_name.semester', readonly=False)
    gpa = fields.Float(string='GPA', related='student_name.gpa', readonly=False)
    clubs = fields.Text(string='Clubs', related='student_name.clubs', readonly=False)
    graduation_date = fields.Date(string='Graduation Date', related='student_name.graduation_date', readonly=False)
    certificates = fields.One2many('masrtech.certificate', 'training_registration', string='Certificates')
    company_id = fields.Many2one('masrtech.factory', string='Company')
    training_name = fields.Char(string='Training Name')
    check_company = fields.Boolean()

    def create_accept_student(self):
        return {
            'name': 'Training',
            'domain': [],
            'view_type': 'form',
            'res_model': 'masrtech.student.accept',
            'view_id': False,
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'context': {'default_company_id': self.company_id.id, 'default_student_name': self.student_name.id,
                        'default_name': self.training_name, 'default_type': 'training'},

        }


class MasrtechCertificates(models.Model):
    _name = 'masrtech.certificate'

    name = fields.Char(string='name')
    description = fields.Char(string='Description')
    attachment = fields.Binary(string='Attachment')
    training_registration = fields.Many2one('masrtech.training.registration')
