from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from werkzeug.security import generate_password_hash, check_password_hash


class TrainingApplication(models.Model):
    _name = 'cocacola.model'
    _rec_name = 'name'

    student_namee = fields.Many2one('op.student', string='Student Name')
    email = fields.Char(string='Email')
    password = fields.Char(string='password', invisible=True)
    name = fields.Char(string='name')
    phone = fields.Char(string='Phone')
    national_id = fields.Char(string='National ID')
    university_id = fields.Many2one('masrtech.universities', string='University')
    university = fields.Char(string='University', default='Borg El Arab Technological University - جامعة برج العرب التكنولوجية')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], 'Gender')
    age = fields.Integer(string='Age')
    registration_status = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
    ], string='Status', default='draft')
    attachment = fields.Binary(string='Attachment')

    def _check_password(self, plain_password):
        """Verify a plaintext password against the stored hash."""
        if not self.password:
            return False
        return check_password_hash(self.password, plain_password or '')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('password'):
                vals['password'] = generate_password_hash(vals['password'])
        return super(TrainingApplication, self).create(vals_list)

    def write(self, vals):
        if vals.get('password'):
            vals['password'] = generate_password_hash(vals['password'])
        return super(TrainingApplication, self).write(vals)

    def action_confirm(self):
        for record in self:
            if not record.attachment:
                raise UserError('Please upload an attachment before confirming.')
            record.registration_status = 'confirmed'

        return True