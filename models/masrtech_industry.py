from odoo import api, models, fields


class MasrtechIndustryType(models.Model):
    _name = 'masrtech.industry.type'

    name = fields.Char(string="name")

    def action_masrtech_industry_type(self):
        if self.name == 'الصحة':
            return {
                'name': 'الصحة',
                'domain': [],
                'view_type': 'form',
                'res_model': 'masrtech.industry.health',
                'view_mode': 'kanban,tree,form',
                'type': 'ir.actions.act_window',
            }
        elif self.name == 'الصناعة':
            return {
                'name': 'الصناعة',
                'domain': [],
                'view_type': 'form',
                'res_model': 'masrtech.industry',
                'view_mode': 'kanban,tree,form',
                'type': 'ir.actions.act_window',
            }


class MasrtechIndustry(models.Model):
    _name = 'masrtech.industry'

    masrtech_factory = fields.One2many('masrtech.factory', 'industry', string="Factories")
    name = fields.Char(string='Name', required=True)

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
    factory_type = fields.Many2one('masrtech.factory.type')

    def send_data_to_type(self):
        source_records = self.env['masrtech.factory.type'].search([])
        for source_record in source_records:
            if source_record.field == True:
                source_record.type = 'industry'
                source_record.name = self.name
                source_record.industry = self.id
            else:
                source_record.type = 'industry'
                source_record.industry = self.id

    def action_masrtech_factory(self):
        self.send_data_to_type()

        return {
            'name': self.name,
            'domain': [],
            'view_type': 'form',
            'res_model': 'masrtech.factory.type',
            'view_mode': 'kanban,tree,form',
            'type': 'ir.actions.act_window',
        }


class MasrtechIndustryHealth(models.Model):
    _name = 'masrtech.industry.health'

    masrtech_factory = fields.One2many('masrtech.factory', 'industry_health', string="Factories")
    name = fields.Char(string='Name', required=True)
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
    factory_type = fields.Many2one('masrtech.factory.type')

    def send_data_to_health_type(self):
        source_records = self.env['masrtech.factory.type'].search([])
        for source_record in source_records:
            if source_record.field == True:
                source_record.type = 'health'
                source_record.name = self.name
                source_record.industry_health = self.id
            else:
                source_record.type = 'health'
                source_record.industry_health = self.id

    def action_masrtech_factory_type_health(self):
        self.send_data_to_health_type()

        return {
            'name': self.name,
            'domain': [],
            'view_type': 'form',
            'res_model': 'masrtech.factory.type',
            'view_mode': 'kanban,tree,form',
            'type': 'ir.actions.act_window',
        }


class MasrtechTypeFactory(models.Model):
    _name = 'masrtech.factory.type'

    name = fields.Char(string="name")
    industry = fields.Many2one('masrtech.industry', string='Industry')
    industry_health = fields.Many2one('masrtech.industry.health', string='Industry')
    type = fields.Selection([
        ('health', 'صحة'),
        ('industry', 'صناعة')], default='health', string="Type")
    field = fields.Boolean(string="the field")

    def action_masrtech_factory(self):
        if self.name == 'Factories':
            if self.type == 'health':

                return {
                    'name': 'Factories',
                    'domain': [('type', '=', 'health'), ('industry_health', '=', self.industry_health.id)],
                    'view_type': 'form',
                    'res_model': 'masrtech.factory',
                    'view_mode': 'kanban,tree,form',
                    'type': 'ir.actions.act_window',
                }

            elif self.type == 'industry':
                return {
                    'name': 'Factories',
                    'domain': [('type', '=', 'industry'), ('industry', '=', self.industry.id)],
                    'view_type': 'form',
                    'res_model': 'masrtech.factory',
                    'view_mode': 'kanban,tree,form',
                    'type': 'ir.actions.act_window',
                }
        else:
            if self.type == 'health':
                return {
                    'name': self.name,
                    'domain': [],
                    'view_type': 'form',
                    'res_model': 'masrtech.industry.health',
                    'view_mode': 'form',
                    'type': 'ir.actions.act_window',
                    'res_id': self.industry_health.id,
                }
            elif self.type == 'industry':
                return {
                    'name': self.name,
                    'domain': [],
                    'view_type': 'form',
                    'res_model': 'masrtech.industry',
                    'view_mode': 'form',
                    'type': 'ir.actions.act_window',
                    'res_id': self.industry.id,
                }


class MasrtechFactory(models.Model):
    _name = 'masrtech.factory'

    name = fields.Char(string="name")
    industry = fields.Many2one('masrtech.industry', string='Industry')
    type_sub = fields.Many2one('masrtech.sub', string='type')
    type_sub_name = fields.Char(related='type_sub.name')
    industry_health = fields.Many2one('masrtech.industry.health', string='Industry')
    type = fields.Selection([
        ('health', 'صحة'),
        ('industry', 'صناعة'), ('nothing', 'nothing')], default='nothing', string="Type")
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

    def send_data_to_type_recommendation(self):
        source_records = self.env['masrtech.type.job.opportunity'].search([])
        for source_record in source_records:
            source_record.check_rec = 'pre'
            source_record.company_id = self.id

    def send_data_to_type(self):
        source_records = self.env['masrtech.type.job.opportunity'].search([])
        for source_record in source_records:
            source_record.check_rec = 'source'
            source_record.company_id = self.id

    def send_data_to_type_project_recommendation(self):
        source_records = self.env['masrtech.project.type'].search([])
        for source_record in source_records:
            source_record.check_rec = 'pre'
            source_record.company_id = self.id

    def send_data_to_type_project(self):
        source_records = self.env['masrtech.project.type'].search([])
        for source_record in source_records:
            source_record.check_rec = 'source'
            source_record.company_id = self.id

    #
    def go_to_type_training_register(self):
        source_records = self.env['masrtech.gotraining.type'].search([])
        for source_record in source_records:
            # source_record.check_rec = 'pre'
            source_record.company_id = self.id

    def create_training(self):
        return {
            'name': 'Training',
            'domain': [],
            'view_type': 'form',
            'res_model': 'masrtech.training',
            'view_id': False,
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'context': {'default_company_id': self.id},

        }

    # def go_to_training_recommendation(self):
    #     return {
    #         'name': 'Training Recommendations',
    #         'domain': [('company_id', '=', self.id)],
    #         'view_type': 'form',
    #         'res_model': 'masrtech.training.recommendation',
    #         'view_id': False,
    #         'view_mode': 'tree,form',
    #         'type': 'ir.actions.act_window',
    #                        'context': {'default_company_id': self.company_id.id},
    #     }

    def go_to_training_recommendation(self):
        self.go_to_type_training_register()
        return {
            'name': 'Training',
            # 'domain': [('company_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'masrtech.gotraining.type',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'type': 'ir.actions.act_window',
            # 'context': {'default_company_id': self.id},
        }

    def create_type_job_opportunity(self):
        return {
            'name': 'Job Opportunity',
            'domain': [],
            'context': {'default_check_student': False, 'default_company_id': self.id},
            'view_type': 'form',
            'res_model': 'masrtech.job.opportunity',
            'view_id': False,
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
        }

    def go_to_job_opportunity_recommendation(self):
        return {
            'name': 'Job Opportunity',
            'domain': [('company_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'masrtech.job.opportunity.recommendation.staff',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            'context': {
                'group_by': 'name',
            },
        }

        # self.send_data_to_type_recommendation()
        # return {
        #     'name': 'Job Opportunity',
        #     'domain': [],
        #     'view_type': 'form',
        #     'res_model': 'masrtech.type.job.opportunity',
        #     'view_id': False,
        #     'view_mode': 'kanban,tree,form',
        #     'type': 'ir.actions.act_window',
        #     # 'context': {'default_check_student': True},
        #
        # }

    def create_project_type(self):
        return {
            'name': 'project',
            'domain': [],
            'context': {'default_check_student': False, 'default_company_id': self.id},
            'view_type': 'form',
            'res_model': 'masrtech.project',
            'view_id': False,
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
        }

    def go_to_project_type_recommendation(self):
        return {
            'name': 'Projects',
            'domain': [('company_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'masrtech.project.recommendation.staff',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            'context': {
                'group_by': 'name',
            },
        }

    def create_problem(self):
        return {
            'name': 'problem',
            'domain': [],
            'view_type': 'form',
            'res_model': 'masrtech.problem',
            'view_id': False,
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'context': {'default_company_id': self.id},

        }

    def go_to_problem_recommendation(self):
        return {
            'name': 'Problems Recommendations',
            'domain': [],
            'view_type': 'form',
            'res_model': 'masrtech.problem.recommendation',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            'context': {
                'group_by': 'name',
            },
        }

    def recruitment(self):
        return {
            'name': 'Recruitment',
            'domain': [],
            'view_type': 'form',
            'res_model': 'hr.job',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'type': 'ir.actions.act_window',

        }
