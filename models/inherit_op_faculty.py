from odoo import api, models, fields, _
from odoo.http import request
from odoo.exceptions import UserError, ValidationError
import json
from werkzeug.security import generate_password_hash


class InheritMasrtechFaculty(models.Model):
    _inherit = 'op.faculty'

    staff_faculty = fields.Many2one('masrtech.faculty')
    university = fields.Many2one('masrtech.universities', string='University')
    faculty = fields.Many2one('masrtech.faculty', string='College')
    department = fields.One2many('op.department', 'staff', string='Department')
    project = fields.Many2one('masrtech.project')
    project_recommendation = fields.Many2one('masrtech.project.recommendation')
    title_dr = fields.Selection([
        ('doctor', 'Doctor'),
        ('assistant', 'Assistant'),
    ], string='Type')
    specialization = fields.Char()
    document_ids = fields.Many2many(
        'ir.attachment',
        string='All Documents'
    )
    count_job_opportunity_recommendation = fields.Integer(compute='_compute_job_opportunity_count',
                                                          string='Training Recommendations')
    count_project_recommendation = fields.Integer(compute='_compute_project_count', string='Projects Recommendations')
    count_problem_recommendation = fields.Integer(compute='_compute_problem_count', string='Problems Recommendations')
    login_username = fields.Char('Login Username')
    login_password = fields.Char('Login Password')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('login_password'):
                vals['login_password'] = generate_password_hash(vals['login_password'])
        return super(InheritMasrtechFaculty, self).create(vals_list)

    def write(self, vals):
        if vals.get('login_password'):
            vals['login_password'] = generate_password_hash(vals['login_password'])
        return super(InheritMasrtechFaculty, self).write(vals)
    emp_id = fields.Many2one('hr.employee', string='Employee', readonly=True)
    user_id = fields.Many2one('res.users', string='User')

    def go_to_job_opportunity_recommendation(self):
        # self.get_student_id()
        # if self.training == True:
        return {
            'name': 'Job Opportunities Recommendations',
            'domain': [('staff_name', '=', self.id)],
            'view_type': 'form',
            'res_model': 'masrtech.job.opportunity.recommendation.staff',
            'view_id': False,
            'view_mode': 'kanban,form',
            'type': 'ir.actions.act_window',
            # 'res_id': self.related,
        }

    def _compute_job_opportunity_count(self):
        for record in self:
            count = self.env['masrtech.job.opportunity.recommendation.staff'].search_count(
                [('staff_name', '=', record.id)])
            record.count_job_opportunity_recommendation = count

    def go_to_project_recommendation(self):
        # self.get_student_id()
        # if self.training == True:
        return {
            'name': 'Projects Recommendations',
            'domain': [('staff_name', '=', self.id)],
            'view_type': 'form',
            'res_model': 'masrtech.project.recommendation.staff',
            'view_id': False,
            'view_mode': 'kanban,form',
            'type': 'ir.actions.act_window',
            # 'res_id': self.related,
        }

    def _compute_project_count(self):
        for record in self:
            count = self.env['masrtech.project.recommendation.staff'].search_count([('staff_name', '=', record.id)])
            record.count_project_recommendation = count

    def go_to_problem_recommendation(self):
        # self.get_student_id()
        # if self.training == True:
        return {
            'name': 'Problems Recommendations',
            'domain': [('staff_name', '=', self.id)],
            'view_type': 'form',
            'res_model': 'masrtech.problem.recommendation',
            'view_id': False,
            'view_mode': 'kanban,form',
            'type': 'ir.actions.act_window',
            # 'res_id': self.related,
        }

    def _compute_problem_count(self):
        for record in self:
            count = self.env['masrtech.problem.recommendation'].search_count([('staff_name', '=', record.id)])
            record.count_problem_recommendation = count


class InheritMasrtechCourse(models.Model):
    _inherit = 'op.course'

    course_faculty = fields.Many2one('masrtech.faculty')

    code = fields.Char(string='Course Code', readonly=True, copy=False, default='New')
    seq = fields.Char(string='Course Code', readonly=True, copy=False, default='New')
    duration_weeks = fields.Integer(string='Duration (Weeks)')
    days_per_week = fields.Integer(string='Days per Week')
    target_audience = fields.Char(string='Target Audience', help='Who is this course for?')
    university_name_ar = fields.Char(string="الجامعه")
    name_ar = fields.Char(string="البرنامج")
    approval_ready = fields.Boolean(
        string='Ready for Approval',
        compute='_compute_approval_ready',
        store=False,
        help='Indicates if course meets all requirements for approval'
    )

    def show_zoom_meeting(self):
        return {
            'type': 'ir.actions.act_url',
            'url': 'https://zoom.us/join',
            'target': 'new',
        }

    def show_mindray(self):
        return {
            'type': 'ir.actions.act_url',
            'url': 'https://www.mindray.com/en',
            'target': 'new',
        }

    # def show_m,(self):
    #     return {
    #         'type': 'ir.actions.act_url',
    #         'url': 'https://zoom.us/join',
    #         'target': 'new',
    #     }

    @api.depends('name', 'description', 'dr_name', 'start_date', 'end_date',
                 'total_hours', 'objective_1', 'objective_2', 'objective_3',
                 'location', 'format', 'university', 'faculty', 'dr_email')
    def _compute_approval_ready(self):
        """Compute if course is ready for approval"""
        for course in self:
            can_approve, missing_fields = course.check_approval_requirements()
            course.approval_ready = can_approve

    def check_approval_requirements(self):
        """
        Check if course meets all requirements for approval
        Returns tuple (can_approve: bool, missing_fields: list)
        """
        missing_fields = []

        # Basic course information
        if not self.name:
            missing_fields.append('Course Title')
        if not self.description:
            missing_fields.append('Description')

        # Doctor information
        if not self.dr_name:
            missing_fields.append('Doctor Name')
        if not self.dr_email:
            missing_fields.append('Doctor Email')
        if not self.department:
            missing_fields.append('Department')

        # Course schedule
        if not self.start_date:
            missing_fields.append('Start Date')
        if not self.end_date:
            missing_fields.append('End Date')
        if not self.total_hours or self.total_hours <= 0:
            missing_fields.append('Total Hours')

        # Objectives (at least one should be filled)
        if not self.objective_1 and not self.objective_2 and not self.objective_3:
            missing_fields.append('At least one Objective')

        # Logistics
        if not self.location:
            missing_fields.append('Location')
        if not self.format:
            missing_fields.append('Format')

        # Accreditation
        if not self.university:
            missing_fields.append('University')
        if not self.faculty:
            missing_fields.append('Faculty/College')

        return len(missing_fields) == 0, missing_fields

    def action_approve_course(self):
        """
        Approve course after validating required fields
        Only users with viewer=True can approve courses
        """
        # Check if current user has viewer rights
        current_user = self.env.user

        for course in self:
            # Check if course is ready for approval
            can_approve, missing_fields = course.check_approval_requirements()

            if not can_approve:
                error_message = _(
                    'Cannot approve course "%s". The following required fields are missing:\n\n%s\n\n'
                    'Please complete all required fields before approval.'
                ) % (course.name or course.code, '\n'.join(['• ' + field for field in missing_fields]))

                raise ValidationError(error_message)

            # Additional business logic validations
            if course.start_date and course.end_date and course.start_date > course.end_date:
                raise ValidationError(_('Start date cannot be later than end date for course "%s".') % course.name)

            if course.credit_hours and course.credit_hours < 0:
                raise ValidationError(_('Credit hours cannot be negative for course "%s".') % course.name)

            # All validations passed, approve the course
            course.write({
                'state': 'publish'
            })

            # Log the approval
            course.message_post(
                body=_('Course approved and published by %s') % current_user.name,
                message_type='notification',
                subtype_xmlid='mail.mt_note'
            )

        # Show success message
        if len(self) == 1:
            message = _('Course "%s" has been successfully approved and published.') % self.name
        else:
            message = _('%d courses have been successfully approved and published.') % len(self)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': message,
                'type': 'success',
                'sticky': False,
            }
        }

    def action_view_course_details(self):
        """Open detailed view of the course in read-only mode"""
        self.ensure_one()
        return {
            'name': _('Course Details'),
            'type': 'ir.actions.act_window',
            'res_model': 'op.course',
            'res_id': self.id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current',
            'flags': {
                'mode': 'readonly',
            },
            'context': {
                'create': False,
                'edit': False,
                'delete': False,
            }
        }

    def action_reject_course(self):
        """Reject course and return to draft"""
        for course in self:
            if course.state == 'publish':
                course.write({'state': 'draft'})
                course.message_post(
                    body=_('Course rejected and returned to draft by %s') % self.env.user.name,
                    message_type='notification',
                    subtype_xmlid='mail.mt_note'
                )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Course Rejected'),
                'message': _('Course has been returned to draft status.'),
                'type': 'warning',
                'sticky': False,
            }
        }

    create_uid = fields.Many2one('res.users', string='Created by', default=lambda self: self.env.user)
    team_leader_name = fields.Char(
        string='Team Leader',
        compute='_get_team_leader',
        store=False
    )
    is_leader = fields.Boolean(defult='False')
    ###########Dr info###############################
    dr_name = fields.Many2one('op.faculty', string='Full Name')
    title_dr = fields.Selection([
        ('doctor', 'Doctor'),
        ('assistant', 'Assistant'),
    ], string='Role')
    dr_email = fields.Char(string='Email')
    dr_phone = fields.Char(string='Phone')
    department = fields.Many2one('op.department', string='Department')
    ###########course info###############################
    name = fields.Char(string="Course Title")
    doctor_name = fields.Char(string="doctor name", compute='compute_doctor_name')
    description = fields.Text(string='Short Description')
    target_audience_en = fields.Many2many(
        'target.model',
        'course_target_audience_en_rel',
        'course_id',
        'target_id',
        string='Target Audience'
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('publish', 'Published'),
    ], string='Status', default='draft')

    @api.depends('create_uid')
    def compute_doctor_name(self):
        for record in self:
            user = self.env.user
            record.doctor_name = user.name

    start_date = fields.Date(string='Course Start Date')
    end_date = fields.Date(string='Course End Date')
    total_hours = fields.Integer(string='Total Hours')
    date_period_display = fields.Char(string='Date Period Display', compute='_compute_date_period_display', store=True)
    #########################objective################
    objective_1 = fields.Char(string='Objective 1')
    objective_2 = fields.Char(string='Objective 2')
    objective_3 = fields.Char(string='Objective 3')
    outcome = fields.Text(string='OutCome')
    benefits = fields.Text(string='Benefits')
    reference = fields.Text(string='REFERENCE')
    training_tools = fields.Text(string='Training Tools')
    ######################Curriculum################
    subject_ids = fields.Many2many('op.subject', string='Curriculum')
    ######################Logistics################
    location = fields.Char(string='Location')
    format = fields.Selection([
        ('in-person', 'In Person'), ('online', 'Online'),
        ('hybrid', 'Hybrid')], string='Format')
    pre_req = fields.Many2many('pre.requirement.model', 'pre_req_rel', string='Pre Requirement')
    ##########Accreditation####################
    university = fields.Many2one('masrtech.universities', string='University')
    faculty = fields.Many2one('masrtech.faculty', string='College')
    credit_hours = fields.Float(string='Number of Credits')
    supporting_docs = fields.Text(string='Supporting Documentation')
    #######################Clinical cases##################
    time = fields.Char(string='duration')
    flyer_image = fields.Binary(
        string='Flyer Image',
        help='Upload the course flyer image (JPG, PNG, GIF)'
    )

    #######################################################333
    def _get_team_leader(self):
        for record in self:
            team_leader = self.env.context.get('team_leader_name', False)
            record.team_leader_name = team_leader
            if record.team_leader_name:
                record.is_leader = True

    def open_my_courses(self):
        user = self.env.user
        is_admin = user.has_group('base.group_system')
        doctor_name = user.name
        user_type = user.x_user_rolee

        team_leader = False

        domain = []
        if not is_admin:
            domain = [('create_uid', '=', user.id)]

        tree_view_id = self.env.ref('openeducat_core.view_op_course_tree').id
        form_view_id = self.env.ref('openeducat_core.view_op_course_form').id
        if user_type == 'doctor':
            title = _('Dr. {} Courses').format(doctor_name)
            is_leader = True,
        elif user_type == 'assistant':
            assistant = self.env['assistant.model'].search([('user_id', '=', user.id)], limit=1)
            if assistant and assistant.staff_dr:
                team_leader = assistant.sudo().staff_dr.name if assistant.staff_dr else False
                print(team_leader, 'team_leader')
                title = _('Assistant Dr. {}').format(doctor_name)
            else:
                title = _('Assistant Dr. {}').format(doctor_name)
        else:
            title = _('{} Courses').format(doctor_name)

        action = {
            'name': title,
            'res_model': 'op.course',
            'type': 'ir.actions.act_window',
            'view_mode': 'kanban,tree,form',
            'domain': domain,
            'context': {
                'create': True,
                'team_leader_name': team_leader,
                'doctor_name': doctor_name
            },
            'target': 'current'
        }

        return action

    target_audience_ar = fields.Many2many(
        'target.model',
        'course_target_audience_ar_rel',
        'course_id',
        'target_id',
        string='الفئة المستهدفة'
    )

    description_ar = fields.Text(string="وصف الدورة")
    pre_req_ar = fields.Many2many('pre.requirement.model', 'pre_req_ar_rel', string='المتطلبات الاساسيه')

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

    @api.onchange('university')
    def _onchange_university(self):
        if self.university:
            self.university_name_ar = self.university.university_name_ar

    @api.model
    def create(self, vals):
        if vals.get('code', 'New') == 'New':
            department_id = vals.get('department')
            sequence_code = 'op.course.code.default'
            if department_id:
                department = self.env['op.department'].browse(department_id)

                if department.name:
                    dept_name = department.name.lower()
                    if dept_name == 'health care':
                        sequence_code = 'op.course.code.medical'
                        print(f"Using MEDICAL sequence: {sequence_code}")
                    elif dept_name == 'industry':
                        sequence_code = 'op.course.code.industry'
                        print(f"Using INDUSTRY sequence: {sequence_code}")
                    else:
                        sequence_code = 'op.course.code.default'
                        print(f"Using DEFAULT sequence: {sequence_code}")
                else:
                    sequence_code = 'op.course.code.default'
                    print(f"No department name - using DEFAULT sequence")
            else:
                sequence_code = 'op.course.code.default'
                print(f"No department ID - using DEFAULT sequence")

            vals['code'] = self.env['ir.sequence'].next_by_code(sequence_code) or 'New'

        course = super(InheritMasrtechCourse, self).create(vals)

        if vals.get('sub_department'):
            try:
                sub_dept = self.env['sub.department.model'].browse(vals['sub_department'])
                if sub_dept.exists():
                    sub_dept.sudo().write({
                        'course_ids': [(4, course.id)]
                    })
                    print(f"Successfully added course {course.id} to sub_department {sub_dept.id}")
            except Exception as e:
                print(f"Error adding course to sub_department: {e}")
                try:
                    sub_dept = self.env['sub.department.model'].browse(vals['sub_department'])
                    if sub_dept.exists():
                        current_courses = sub_dept.course_ids.ids
                        if course.id not in current_courses:
                            current_courses.append(course.id)
                            sub_dept.sudo().course_ids = [(6, 0, current_courses)]
                            print(f"Alternative method: Successfully added course {course.id}")
                except Exception as e2:
                    print(f"Alternative method also failed: {e2}")

        return course

    def write(self, vals):
        result = super(InheritMasrtechCourse, self).write(vals)

        if 'sub_department' in vals:
            for record in self:
                old_sub_departments = self.env['sub.department.model'].search([
                    ('course_ids', 'in', [record.id]),
                    ('id', '!=', vals.get('sub_department', False))
                ])
                for old_sub_dept in old_sub_departments:
                    old_sub_dept.course_ids = [(3, record.id)]

                if record.sub_department:
                    if record.id not in record.sub_department.course_ids.ids:
                        record.sub_department.course_ids = [(4, record.id)]

        return result

    department_domain = fields.Char(compute='domain_service_id')

    @api.onchange('department')
    def domain_service_id(self):
        for rec in self:
            if rec.department:
                departments = self.env['sub.department.model'].search([
                    ('department', '=', rec.department.id),
                ])
                if departments:
                    rec.department_domain = json.dumps([('id', 'in', departments.ids)])
                else:
                    rec.department_domain = json.dumps([('id', 'in', [])])
            else:
                rec.department_domain = json.dumps([('id', 'in', [])])

    def unlink(self):
        for record in self:
            if record.sub_department:
                record.sub_department.course_ids = [(3, record.id)]

        return super(InheritMasrtechCourse, self).unlink()

    sub_department = fields.Many2one('sub.department.model', string='Sub Department')

    @api.onchange('sub_department')
    def _onchange_sub_department(self):
        if self.sub_department and self.id:
            if self.id not in self.sub_department.course_ids.ids:
                self.sub_department.course_ids = [(4, self.id)]


class InheritMasrtechDepartment(models.Model):
    _inherit = 'op.department'

    university = fields.Many2one('masrtech.universities', string='University')
    department_faculty = fields.Many2one('masrtech.faculty', string='College')
    staff = fields.Many2one('op.faculty')
    training = fields.Many2one('masrtech.training')
    job_opportunity = fields.Many2one('masrtech.job.opportunity')
    project = fields.Many2one('masrtech.project')
    problem = fields.Many2one('masrtech.problem')
    description = fields.Text(string='Description')
    sub_department = fields.Many2many('sub.department.model', string='Sub Department')

    # department_faculty = fields.Many2one('masrtech.faculty')
    def action_masrtech_department_staff(self):
        return {
            'name': 'Students',
            'domain': [('university', '=', self.university.id), ('faculty', '=', self.department_faculty.id),
                       ('department', '=', self.id)],
            'view_type': 'form',
            'res_model': 'op.faculty',
            'view_mode': 'kanban,tree,form',
            'type': 'ir.actions.act_window',
        }


class InheritMasrtechSubject(models.Model):
    _inherit = 'op.subject'

    subject_faculty = fields.Many2one('masrtech.faculty')
    university = fields.Many2one('masrtech.universities', string='University')
    faculty = fields.Many2one('masrtech.faculty', string='College')
    department = fields.Many2one('op.department', string='Department')
    name_ar = fields.Char(string='الاسم')
    duration_weeks = fields.Integer(string='Duration (Weeks)')
    description = fields.Text(string='Description')
    description_ar = fields.Text(string='المحتوي')


class InheritMasrtechBatch(models.Model):
    _inherit = 'op.batch'

    batch_faculty = fields.Many2one('masrtech.faculty')
    university = fields.Many2one('masrtech.universities', string='University')
    faculty = fields.Many2one('masrtech.faculty', string='College')
    department = fields.Many2one('op.department', string='Department')


class InheritMasrtechClassroom(models.Model):
    _inherit = 'op.classroom'

    classroom_faculty = fields.Many2one('masrtech.faculty')


class InheritMasrtechActivityType(models.Model):
    _inherit = 'op.activity.type'

    activity_type_faculty = fields.Many2one('masrtech.faculty')


class ResUsers(models.Model):
    _inherit = 'res.users'

    x_user_rolee = fields.Selection([
        ('doctor', 'Doctor'),
        ('assistant', 'Assistant'),
    ], string='Type')

    # x_login_count = fields.Integer(string='Login Count', default=0)
    # x_is_scientific_committee = fields.Boolean(
    #     string='Scientific Committee',
    #     store=False
    # )
