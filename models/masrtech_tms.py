from odoo import api, models, fields


class MasrtechTraining(models.Model):
    _name = 'masrtech.training'

    name = fields.Char(string='Name')
    description = fields.Text(string='Description')
    company_id = fields.Many2one('masrtech.factory', string='Company')
    date_start = fields.Date(string='Start Date')
    date_end = fields.Date(string='End Date')
    location = fields.Char(string='Location')
    duration_hours = fields.Float(string='Duration (Hours)')
    seats_available = fields.Integer(string='Seats Available')
    registration_deadline = fields.Date(string='Registration Deadline')
    # materials = fields.Char(string='Training Materials')
    masrtech_department = fields.One2many('op.department', 'training', string='Interested Departments')

    def send_to_students(self):
        records = self.env['op.student'].search([])
        list = []
        for rec in records:
            for dep in self.masrtech_department:
                if (rec.department.id == dep.id):
                    training_recommendation = self.env['masrtech.training.recommendation'].create({
                        'name': self.name,
                        'student_name': rec.id,
                        'description': self.description,
                        'company_id': self.company_id.id,
                        'duration': self.duration_hours,
                        'date_start': self.date_start,
                        'date_end': self.date_end,
                        'location': self.location,
                        # 'materials': self.materials,
                        'seats_available': self.seats_available,
                        'registration_deadline': self.registration_deadline,
                    })


class MasrtechTypeGoTraining(models.Model):
    _name = 'masrtech.gotraining.type'

    name = fields.Char(string='name')
    # check_rec = fields.Selection([
    #     ('source', 'Source'),
    #     ('pre', 'Pre')])
    company_id = fields.Many2one('masrtech.factory', string='Company')

    def go_to_Registers_recommendation(self):
        if self.name == 'Registers':
            return {
                'name': 'Registers',
                'domain': [('company_id', '=', self.company_id.id)],
                'view_type': 'form',
                'res_model': 'masrtech.training.registration',
                'view_id': False,
                'view_mode': 'tree,form',
                'type': 'ir.actions.act_window',
                'context': {
                    'group_by': 'training_name',
                },

            }

        elif self.name == 'Recommendations':
            return {
                'name': 'Training Recommendations',
                'domain': [('company_id', '=', self.company_id.id)],
                'view_type': 'form',
                'res_model': 'masrtech.training.recommendation',
                'view_id': False,
                'view_mode': 'tree,form',
                'type': 'ir.actions.act_window',
                'context': {
                    'group_by': 'name',
                },
            }


class MasrtechCourse(models.Model):
    _name = 'masrtech.course'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    duration = fields.Integer(string='Duration (in weeks)')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    capacity = fields.Integer(string='Capacity')
    materials = fields.Text(string='Course Materials')

    # students_count = fields.Integer(compute='_compute_students_count', string='Students Count', store=True)

    # @api.depends('student_ids')
    # def _compute_students_count(self):
    #     for course in self:
    #         course.students_count = len(course.student_ids)


class MasrtechJobOpportunity(models.Model):
    _name = 'masrtech.job.opportunity'
    _description = 'Job Opportunity'

    name = fields.Char(string='Job Title')
    description = fields.Text(string='Job Description')
    requirements = fields.Text(string='Requirements')
    location = fields.Char(string='Location')
    salary = fields.Float(string='Salary')
    deadline = fields.Date(string='Application Deadline')
    company_id = fields.Many2one('masrtech.factory', string='Company')
    masrtech_department = fields.One2many('op.department', 'job_opportunity', string='Interested Departments')
    job_type = fields.Selection([('full_time', 'Full Time'), ('part_time', 'Part Time'), ('contract', 'Contract')],
                                string='Job Type')
    experience_required = fields.Integer(string='Years of Experience Required')
    education_level = fields.Selection([('high_school', 'High School'), ('bachelor', 'Bachelor'),
                                        ('master', 'Master'), ('phd', 'PhD')], string='Education Level')
    skills_required = fields.Many2many('hr.skill', string='Skills Required')
    email = fields.Char(string='Email')
    check_student = fields.Boolean()

    def send_to_students(self):
        records = self.env['op.student'].search([])
        list = []
        for rec in records:
            for dep in self.masrtech_department:
                if (rec.department.id == dep.id):
                    recommendation = self.env['masrtech.job.opportunity.recommendation'].create({
                        'name': self.name,
                        'student_name': rec.id,
                        'description': self.description,
                        'company_id': self.company_id.id,
                        'email': self.email,
                        'requirements': self.requirements,
                        'location': self.location,
                        'salary': self.salary,
                        'deadline': self.deadline,
                        'job_type': self.job_type,
                        'experience_required': self.experience_required,
                        'education_level': self.education_level,
                        'skills_required': self.skills_required.ids,
                    })

    def send_to_staff(self):
        records = self.env['op.faculty'].search([])
        list = []
        for rec in records:
            for dep in self.masrtech_department:
                for fac in rec.department:
                    if (fac.id == dep.id):
                        recommendation = self.env['masrtech.job.opportunity.recommendation.staff'].create({
                            'name': self.name,
                            'staff_name': rec.id,
                            'description': self.description,
                            'company_id': self.company_id.id,
                            'email': self.email,
                            'requirements': self.requirements,
                            'location': self.location,
                            'salary': self.salary,
                            'deadline': self.deadline,
                            'job_type': self.job_type,
                            'experience_required': self.experience_required,
                            'education_level': self.education_level,
                            'skills_required': self.skills_required.ids,
                        })


class TypeJobOpportunity(models.Model):
    _name = 'masrtech.type.job.opportunity'
    name = fields.Char(string='Name')
    check_rec = fields.Selection([
        ('source', 'Source'),
        ('pre', 'Pre')])
    company_id = fields.Many2one('masrtech.factory', string='Company')

    def create_job_opportunity(self):
        if self.check_rec == 'source':
            if self.name == 'Students':
                return {
                    'name': 'Job Opportunity',
                    'domain': [],
                    'context': {'default_check_student': True, 'default_company_id': self.company_id.id},
                    'view_type': 'form',
                    'res_model': 'masrtech.job.opportunity',
                    'view_id': False,
                    'view_mode': 'form',
                    'type': 'ir.actions.act_window',

                }
            elif self.name == 'Staff':
                return {
                    'name': 'Job Opportunity',
                    'domain': [],
                    'context': {'default_check_student': False, 'default_company_id': self.company_id.id},
                    'view_type': 'form',
                    'res_model': 'masrtech.job.opportunity',
                    'view_id': False,
                    'view_mode': 'form',
                    'type': 'ir.actions.act_window',
                }
        elif self.check_rec == 'pre':
            if self.name == 'Students':
                return {
                    'name': 'Job Opportunity',
                    'domain': [('company_id', '=', self.company_id.id)],
                    'view_type': 'form',
                    'res_model': 'masrtech.job.opportunity.recommendation',
                    'view_id': False,
                    'view_mode': 'tree,form',
                    'type': 'ir.actions.act_window',
                    'context': {
                        'group_by': 'name',
                    },
                }
            elif self.name == 'Staff':
                return {
                    'name': 'Job Opportunity',
                    'domain': [('company_id', '=', self.company_id.id)],
                    'view_type': 'form',
                    'res_model': 'masrtech.job.opportunity.recommendation.staff',
                    'view_id': False,
                    'view_mode': 'tree,form',
                    'type': 'ir.actions.act_window',
                    'context': {
                        'group_by': 'name',
                    },
                }


class MasrtechProject(models.Model):
    _name = 'masrtech.project'

    name = fields.Char(string='Project Title', required=True)
    description = fields.Text(string='Project Description')
    company_id = fields.Many2one('masrtech.factory', string='Company')

    supervisor_id = fields.Many2one('op.faculty', string='Supervisor')
    masrtech_department = fields.One2many('op.department', 'project', string='Interested Departments')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    students = fields.One2many('op.student', 'project', string='Students')
    achievements = fields.Text(string='Achievements')
    challenges = fields.Text(string='Challenges')
    materials_needed = fields.Text(string='Materials Needed')
    email = fields.Char(string='Email')
    deadline = fields.Date(string='Application Deadline')

    check_student = fields.Boolean()

    def send_to_students(self):
        records = self.env['op.student'].search([])
        list = []
        for rec in records:
            for dep in self.masrtech_department:
                if (rec.department.id == dep.id):
                    recommendation = self.env['masrtech.project.recommendation'].create({
                        'name': self.name,
                        'student_name': rec.id,
                        'description': self.description,
                        'supervisor_id': self.supervisor_id.id,
                        'email': self.email,
                        'start_date': self.start_date,
                        'end_date': self.end_date,
                        'deadline': self.deadline,
                        'achievements': self.achievements,
                        'challenges': self.challenges,
                        'materials_needed': self.materials_needed,
                    })

    def send_to_staff(self):
        records = self.env['op.faculty'].search([])
        list = []
        for rec in records:
            for dep in self.masrtech_department:
                for fac in rec.department:
                    if (fac.id == dep.id):
                        recommendation = self.env['masrtech.project.recommendation.staff'].create({
                            'name': self.name,
                            'staff_name': rec.id,
                            'description': self.description,
                            'email': self.email,
                            'start_date': self.start_date,
                            'end_date': self.end_date,
                            'deadline': self.deadline,
                            'achievements': self.achievements,
                            'challenges': self.challenges,
                            'materials_needed': self.materials_needed,
                        })


class MasrtechProjectType(models.Model):
    _name = 'masrtech.project.type'

    name = fields.Char(string='Name')
    check_rec = fields.Selection([
        ('source', 'Source'),
        ('pre', 'Pre')])
    company_id = fields.Many2one('masrtech.factory', string='Company')

    def create_project(self):
        if self.check_rec == 'source':
            if self.name == 'Students':
                return {
                    'name': 'Project',
                    'domain': [],
                    'context': {'default_check_student': True, 'default_company_id': self.company_id.id},
                    'view_type': 'form',
                    'res_model': 'masrtech.project',
                    'view_id': False,
                    'view_mode': 'form',
                    'type': 'ir.actions.act_window',
                }
            elif self.name == 'Staff':
                return {
                    'name': 'project',
                    'domain': [],
                    'context': {'default_check_student': False, 'default_company_id': self.company_id.id},
                    'view_type': 'form',
                    'res_model': 'masrtech.project',
                    'view_id': False,
                    'view_mode': 'form',
                    'type': 'ir.actions.act_window',
                }
        elif self.check_rec == 'pre':
            if self.name == 'Students':
                return {
                    'name': 'Projects',
                    'domain': [('company_id', '=', self.company_id.id)],
                    'view_type': 'form',
                    'res_model': 'masrtech.project.recommendation',
                    'view_id': False,
                    'view_mode': 'tree,form',
                    'type': 'ir.actions.act_window',
                    'context': {
                        'group_by': 'name',
                    },
                }
            elif self.name == 'Staff':
                return {
                    'name': 'Projects',
                    'domain': [('company_id', '=', self.company_id.id)],
                    'view_type': 'form',
                    'res_model': 'masrtech.project.recommendation.staff',
                    'view_id': False,
                    'view_mode': 'tree,form',
                    'type': 'ir.actions.act_window',
                    'context': {
                        'group_by': 'name',
                    },
                }


class MasrtechProblems(models.Model):
    _name = 'masrtech.problem'

    name = fields.Char(string='Problem Title', required=True)
    description = fields.Text(string='Description')
    date = fields.Date(string='Date')
    # recommended_staff_ids = fields.Many2many('op.faculty', string='Recommended Staff')
    email = fields.Char(string='Email')
    company_id = fields.Many2one('masrtech.factory', string='Company')
    masrtech_department = fields.One2many('op.department', 'problem', string='Interested Departments')
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

    def send_to_staff(self):
        records = self.env['op.faculty'].search([])
        list = []
        for rec in records:
            for dep in self.masrtech_department:
                for fac in rec.department:
                    if (fac.id == dep.id):
                        recommendation = self.env['masrtech.problem.recommendation'].create({
                            'name': self.name,
                            'staff_name': rec.id,
                            'description': self.description,
                            'email': self.email,
                            'date': self.date,
                            'company_id': self.company_id.id,
                            'deadline': self.deadline,
                            'location': self.location,
                            'status': self.status,
                            'challenges': self.challenges,
                            'materials_needed': self.materials_needed,
                        })
