from odoo import api, models, fields


class JobOpportunityRecommendationStaff(models.Model):
    _name = 'masrtech.job.opportunity.recommendation.staff'

    name = fields.Char(string='Job Title')
    staff_name = fields.Many2one('op.faculty', string='Staff')
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


class ProjectRecommendationStaff(models.Model):
    _name = 'masrtech.project.recommendation.staff'

    name = fields.Char(string='Project Title', required=True)
    description = fields.Text(string='Project Description')
    staff_name = fields.Many2one('op.faculty', string='Staff')
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


class ProblemRecommendationStaff(models.Model):
    _name = 'masrtech.problem.recommendation'

    name = fields.Char(string='Problem Title', required=True)
    staff_name = fields.Many2one('op.faculty', string='Staff')
    description = fields.Text(string='Description')
    date = fields.Date(string='Date')
    email = fields.Char(string='Email')
    company_id = fields.Many2one('masrtech.factory', string='Company')
    location = fields.Char(string='Location')
    deadline = fields.Date(string='Deadline')
    status = fields.Selection([
        ('new', 'New'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed')
    ], string='Status', default='new')

    challenges = fields.Text(string='Challenges')
    materials_needed = fields.Text(string='Materials Needed')
