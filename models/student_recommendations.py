from odoo import api, models, fields


class TrainingRecommendation(models.Model):
    _name = 'masrtech.training.recommendation'

    name = fields.Char(string='name')
    student_name = fields.Many2one('op.student', string='Student')
    company_id = fields.Many2one('masrtech.factory', string='Company')

    description = fields.Text(string='Description')
    duration = fields.Integer(string='Duration (in weeks)')
    date_start = fields.Date(string='Start Date')
    date_end = fields.Date(string='End Date')
    location = fields.Char(string='Location')
    materials = fields.Char(string='Training Materials')
    duration_hours = fields.Float(string='Duration (Hours)')
    seats_available = fields.Integer(string='Seats Available')
    registration_deadline = fields.Date(string='Registration Deadline')

    def get_training_registration(self):
        return {
            'name': 'Training',
            'domain': [],
            'view_type': 'form',
            'res_model': 'masrtech.training.registration',
            'view_id': False,
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'context': {'default_student_name': self.student_name.id, 'default_company_id': self.company_id.id,
                        'default_training_name': self.name},

        }
    # student_name = fields.One2many('op.student', 'training_recommendation', string='Student')


class JobOpportunityRecommendation(models.Model):
    _name = 'masrtech.job.opportunity.recommendation'

    name = fields.Char(string='Job Title')
    student_name = fields.Many2one('op.student', string='Student')

    description = fields.Text(string='Job Description')
    requirements = fields.Text(string='Requirements')
    location = fields.Char(string='Location')
    salary = fields.Float(string='Salary')
    deadline = fields.Date(string='Application Deadline')
    company_id = fields.Many2one('masrtech.factory', string='Company')
    masrtech_department = fields.One2many('op.department', 'training', string='Interested Departments')
    job_type = fields.Selection([('full_time', 'Full Time'), ('part_time', 'Part Time'), ('contract', 'Contract')],
                                string='Job Type')
    experience_required = fields.Integer(string='Years of Experience Required')
    education_level = fields.Selection([('high_school', 'High School'), ('bachelor', 'Bachelor'),
                                        ('master', 'Master'), ('phd', 'PhD')], string='Education Level')
    skills_required = fields.Many2many('hr.skill', string='Skills Required')
    email = fields.Char(string='Email')


class ProjectRecommendation(models.Model):
    _name = 'masrtech.project.recommendation'

    name = fields.Char(string='Project Title', required=True)
    description = fields.Text(string='Project Description')
    supervisor_id = fields.Many2one('op.faculty', string='Supervisor')
    company_id = fields.Many2one('masrtech.factory', string='Company')

    # masrtech_department = fields.One2many('op.department', 'project', string='Interested Departments')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    student_name = fields.Many2one('op.student', string='Students')
    achievements = fields.Text(string='Achievements')
    challenges = fields.Text(string='Challenges')
    materials_needed = fields.Text(string='Materials Needed')
    email = fields.Char(string='Email')
    deadline = fields.Date(string='Application Deadline')
