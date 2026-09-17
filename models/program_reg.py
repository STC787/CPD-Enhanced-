from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
import secrets

_logger = logging.getLogger(__name__)


def _safe_account_password(raw):
    if raw and not raw.startswith(('pbkdf2:', 'pbkdf2-sha256', 'scrypt:', 'sha256$')):
        return raw
    return secrets.token_urlsafe(24)


class TrainingApplication(models.Model):
    _name = 'program.reg'
    _rec_name = 'full_name'
    document_ids = fields.Many2many(
        'ir.attachment',
        string='All Documents'
    )
    full_name = fields.Char(string='Full Name', required=True, )
    email_address = fields.Char(string='Email Address', )
    phone_number = fields.Char(string='Phone Number', required=True, help='Enter your phone number')
    why_interested = fields.Text(string='Why are you interested?')
    education_year = fields.Selection([
        ('1st_year', '1st Year'),
        ('2nd_year', '2nd Year'),
        ('3rd_year', '3rd Year'),
        ('4th_year', '4th Year'),
        ('graduate', 'Graduate'),
        ('postgraduate', 'Post Graduate'),
    ], string='Education Year')
    seat_number = fields.Char(string='Assigned Seat Number')
    application_date = fields.Date(string='Application Date', default=fields.Datetime.now, readonly=True)
    course_id = fields.Many2one('op.course', string='Course')
    university = fields.Many2one('masrtech.universities', string='University')
    national_id = fields.Char('National ID')
    work_phone = fields.Char('Work Phone')
    home_phone = fields.Char('Home Phone')
    educational_status = fields.Selection([
        ('student', 'Student'),
        ('graduate', 'Graduate'),
        ('postgraduate', 'Postgraduate')
    ])
    organization = fields.Char('Organization')
    position = fields.Char('Position')
    experience_years = fields.Integer('Years of Experience')
    special_requirements = fields.Text('Special Requirements')


class TargetModel(models.Model):
    _name = 'target.model'
    _rec_name = 'name'

    name = fields.Char(string='Target Audience')
    name_ar = fields.Char(string='الفئة المستهدفة')


class PreRequirementModel(models.Model):
    _name = 'pre.requirement.model'
    _rec_name = 'name'

    name = fields.Char(string='Pre Requirement')
    name_ar = fields.Char(string='الطلبات المسبقه')


class OpFaculty(models.Model):
    _inherit = 'op.faculty'
    user_id = fields.Many2one('res.users', string='User')

    @api.model
    def create(self, vals):
        record = super(OpFaculty, self).create(vals)

        record.create_employee()

        return record

    def create_employee(self):
        for record in self:
            existing_user = None
            if record.email:
                existing_user = self.env['res.users'].sudo().search([
                    ('email', '=', record.email)
                ], limit=1)

            if not existing_user and record.login_username:
                existing_user = self.env['res.users'].sudo().search([
                    ('login', '=', record.login_username)
                ], limit=1)

            existing_employee = None
            if record.email:
                existing_employee = self.env['hr.employee'].search([
                    ('work_email', '=', record.email)
                ], limit=1)

            if existing_employee:
                record.emp_id = existing_employee.id

                if existing_employee.user_id:
                    record.user_id = existing_employee.user_id.id
                    record.user_id.groups_id = [(4, self.env.ref('openeducat_core.group_op_faculty').id)]
                    if record.title_dr:
                        existing_employee.user_id.write({
                            'x_user_rolee': record.title_dr
                        })
                elif existing_user:
                    existing_employee.user_id = existing_user.id
                    record.user_id = existing_user.id
                    record.user_id.groups_id =[(4, self.env.ref('openeducat_core.group_op_faculty').id)]

                    if record.title_dr:
                        existing_user.write({
                            'x_user_rolee': record.title_dr})

            else:
                if existing_user:
                    user_id = existing_user
                    if record.title_dr:
                        user_id.write({
                            'x_user_rolee': record.title_dr
                        })
                else:
                    existing_partner = None
                    if record.email:
                        existing_partner = self.env['res.partner'].sudo().search([
                            ('email', '=', record.email)
                        ], limit=1)

                    user_vals = {
                        'name': record.name,
                        'login': record.login_username or record.email,
                        'email': record.email,
                        'password': _safe_account_password(record.login_password),
                        'x_user_rolee': record.title_dr,
                    }

                    if existing_partner:
                        user_vals['partner_id'] = existing_partner.id

                    user_id = self.env['res.users'].sudo().create(user_vals)
                    user_id.groups_id = [(4, self.env.ref('openeducat_core.group_op_faculty').id)]


                employee_vals = {
                    'name': record.name,
                    'work_email': record.email,
                    'work_phone': record.phone,
                    'gender': record.gender,
                    'birthday': record.birth_date,
                    'user_id': user_id.id,
                }

                emp_id = self.env['hr.employee'].create(employee_vals)
                record.emp_id = emp_id.id
                record.user_id = user_id.id

class SubDepartmentModel(models.Model):
    _name = 'sub.department.model'
    _rec_name = 'name'
    name = fields.Char(string='Name')
    course_ids=fields.Many2many('op.course',string='Courses')
    department = fields.Many2one('op.department',string='Parent Department')

class AssistantModel(models.Model):
    _name = 'assistant.model'
    _rec_name = 'name'

    first_name = fields.Char(string='First Name')
    name = fields.Char(string='Name')
    middle_name = fields.Char(string='Middle Name')
    last_name = fields.Char(string='Last Name')
    birth_date = fields.Date(string='Birth Date')
    course_id = fields.Many2many('op.course', string='Course')
    staff = fields.Many2many('op.faculty', string='Team leader Dr')
    staff_dr = fields.Many2one('op.faculty', string='Team leader Dr')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], 'Gender')
    title_dr = fields.Selection([
        ('doctor', 'Doctor'),
        ('assistant', 'Assistant'),
    ], string='Type')
    university = fields.Many2one('masrtech.universities', string='University')
    faculty = fields.Many2one('masrtech.faculty', string='College')
    login_username = fields.Char('Login Username')
    login_password = fields.Char('Login Password')
    emp_id = fields.Many2one('hr.employee', string='Employee', readonly=True)
    user_id = fields.Many2one('res.users', string='User')
    document_ids = fields.Many2many(
        'ir.attachment',
        string='All Documents'
    )

    @api.model
    def create(self, vals):
        record = super(AssistantModel, self).create(vals)

        record.create_employee()

        return record

    def create_employee(self):
        for record in self:
            existing_employee = self.env['hr.employee'].search([
                ('work_email', '=', record.email)
            ], limit=1)

            if existing_employee:
                record.emp_id = existing_employee.id
                record.user_id = existing_employee.user_id.id if existing_employee.user_id else False
                record.user_id.groups_id = [(4, self.env.ref('openeducat_core.group_op_faculty').id)]
                record.user_id.write({
                    'x_user_rolee': record.title_dr
                })
            else:
                user_vals = {
                    'name': record.name,
                    'login': record.login_username or record.email,
                    'email': record.email,
                    'password': _safe_account_password(record.login_password),
                    'x_user_rolee': record.title_dr,
                }
                user_id = self.env['res.users'].sudo().create(user_vals)
                user_id.groups_id = [(4, self.env.ref('openeducat_core.group_op_faculty').id)]

                employee_vals = {
                    'name': record.name,
                    'work_email': record.email,
                    'work_phone': record.phone,
                    'gender': record.gender,
                    'birthday': record.birth_date,
                    'user_id': user_id.id,
                }

                emp_id = self.env['hr.employee'].create(employee_vals)
                record.emp_id = emp_id.id
                record.user_id = user_id.id


class ReviewerModel(models.Model):
    _name = 'reviewer.model'
    _rec_name = 'name'

    name = fields.Char(string='Reviewer Name')
    title_dr = fields.Selection([
        ('scientific', 'Scientific Reviewer'),
    ], string='Committee Role')
    review_date = fields.Date(
        string='Review Date',
        default=fields.Date.today
    )
    email = fields.Char(string='Email Address')
    university = fields.Many2one('masrtech.universities', string='University')

    phone = fields.Char(string='Phone')

    course_id = fields.Many2one('op.course', string='Course Title')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], 'Gender')
    role = fields.Selection([
        ('reviewer', 'Reviewer'),
        ('chair', 'Chair')
    ], 'Role in Committee')
    credentials = fields.Selection([
        ('md', 'MD'),
        ('phd', 'PhD')
    ], 'Professional Credentials')
    course_code = fields.Char(
        string='Course Code',
        help='Unique course identifier'
    )
    lead_instructor = fields.Char(
        string='Lead Instructor',
    )

    # SCIENTIFIC MERIT SECTION
    scientific_rationale = fields.Text(
        string='Scientific Rationale',
        help='Provide detailed scientific justification for the course content'
    )

    alignment_with_standards = fields.Text(
        string='Alignment with Standards',
        help='Describe how the course meets current professional standards'
    )
    ethical = fields.Text(
        string='Ethical Considerations',
    )
    # QUALITY ASSURANCE SECTION
    pedagogical_approach = fields.Text(
        string='Pedagogical Approach',
        help='Detail the teaching methodology and educational materials used'
    )

    assessment_methods = fields.Text(
        string='Assessment Methods',
        help='Describe how learners will be evaluated and feedback provided'
    )

    accreditation_compliance = fields.Text(
        string='Accreditation Compliance',
        help='Verify that the course meets required accreditation standards'
    )
    format = fields.Selection([
        ('in-person', 'In Person'), ('online', 'Online'),
        ('hybrid', 'Hybrid')], string='Format')
    target_audience_en = fields.Many2many(
        'target.model',
        string='Target Audience'
    )
    objective_1 = fields.Char(string='Objective 1')
    objective_2 = fields.Char(string='Objective 2')
    objective_3 = fields.Char(string='Objective 3')
    description = fields.Text(string='Course Description')
    pre_req = fields.Many2many('pre.requirement.model', string='Pre Requisites')
    start_date = fields.Date(string='Course Start Date')
    end_date = fields.Date(string='Course End Date')
    total_hours = fields.Integer(string='Total Hours')
    date_period_display = fields.Char(string='Date Period Display', compute='_compute_date_period_display', store=True)
    # Scientific Merit Section Fields

    key_references = fields.Text(
        string='Key References',
        help='Provide the primary scientific references that support the course content',
    )

    recent_research = fields.Text(
        string='Recent Research',
        help='Summarize the most recent studies, guidelines, or research that inform the course content',
    )

    # SCIENTIFIC REVIEW SUBSECTION

    scientific_validity = fields.Text(
        string='Scientific Validity',
        help='Assess the scientific accuracy, validity, and reliability of the course material',
    )

    innovative_aspects = fields.Text(
        string='Innovative Aspects',
        help='Identify and describe any novel, cutting-edge, or advanced scientific concepts presented in the course'
    )

    # ETHICAL CONSIDERATIONS SUBSECTION

    ethical_compliance = fields.Text(
        string='Ethical Compliance',
        help='Assess compliance with ethical standards and note any ethical considerations or issues',

    )

    conflict_of_interest = fields.Text(
        string='Conflict of Interest',
        help='Disclose any potential conflicts of interest related to the course content, instructors, or reviewers'
    )
    ############    q#########

    accreditation_standards = fields.Text(
        string='Accreditation',
        help='List the relevant accreditations or quality standards that the course meets',

    )

    quality_control_procedures = fields.Text(
        string='Quality Control',
        help='Describe the quality control procedures implemented for course content and delivery',

    )

    feedback_mechanisms = fields.Text(
        string='Feedback Mechanisms',
        help='Explain how participant feedback is collected and used for course improvement',

    )

    revision_process = fields.Text(
        string='Revision Process',
        help='Outline the systematic process for regular course updates and revisions',

    )

    supporting_documents = fields.Text(
        string='Supporting Documents',
        help='List or provide links to quality assurance documentation and supporting materials'
    )
    ################33
    eligibility_criteria = fields.Text(
        string='Eligibility Criteria',
        help='Define who is eligible to receive certification from this course',

    )

    certification_assessment = fields.Text(
        string='Assessment Methods',
        help='Explain the methods used to assess participants for certification',

    )

    certification_validity = fields.Text(
        string='Certification Validity',
        help='State how long the certification remains valid',

    )

    renewal_process = fields.Text(
        string='Renewal Process',
        help='Describe the process and requirements for certification renewal'
    )

    certification_documentation = fields.Text(
        string='Documentation',
        help='List or provide links to certification-related documentation and evidence'
    )
    summary_recommendation = fields.Text(
        string='Summary Recommendation',
        help='Provide your overall recommendation for this course',

    )

    conditions_or_suggestions = fields.Text(
        string='Conditions or Suggestions',
        help='List specific conditions that must be met for approval or suggestions for improvement'
    )

    # Rationale
    rationale_header = fields.Char(
        string='Rationale'
    )
    final_comments = fields.Text(
        string='Final Comments (Optional)',
        help='Any additional final comments for the committee or course provider'
    )


    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('request_changes', 'Changes Requested')
    ], string='Review Status', default='draft', tracking=True)


    def action_request_changes(self):
        """
        Request changes for the course
        """
        self.write({
            'state': 'request_changes',
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Changes Requested',
                'message': 'Course review status updated to "Changes Requested"',
                'type': 'warning',
                'sticky': False,
            }
        }

    def action_reject(self):
        """
        Reject the course
        """
        self.write({
            'state': 'rejected',
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Course Rejected',
                'message': 'Course review status updated to "Rejected"',
                'type': 'danger',
                'sticky': False,
            }
        }

    def action_approve(self):
        if self.course_id:
            self.write({
                'state': 'approved',
            })

            self.course_id.write({
                'state': 'publish'
            })

            # Add tracking message to the course record
            self.course_id.message_post(
                body=f"Course approved by reviewer: {self.name} on {fields.Date.today()}",
                message_type='notification'
            )

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Course Approved',
                    'message': f'Course "{self.course_id.name}" has been approved and published!',
                    'type': 'success',
                    'sticky': False,
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'message': 'No course is linked to this review record.',
                    'type': 'danger',
                    'sticky': True,
                }
            }

    @api.depends('start_date', 'end_date')
    def _compute_date_period_display(self):
        for record in self:
            if record.start_date and record.end_date:
                start_month = record.start_date.strftime('%B')
                end_month = record.end_date.strftime('%B')
                if start_month == end_month:
                    record.date_period_display = start_month
                else:
                    record.date_period_display = f"{start_month}-{end_month}"
            else:
                record.date_period_display = ''

# class ResUsers(models.Model):
#     _inherit = 'res.users'
#
#     x_login_count_today = fields.Integer(string='Today Login Count', default=0)
#     x_last_login_time = fields.Datetime(string='Last Login Time')
