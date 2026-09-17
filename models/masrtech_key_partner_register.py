from odoo import api, models, fields, _
from odoo.exceptions import AccessError
from datetime import datetime,date,timedelta
from odoo.exceptions import UserError, ValidationError
from cryptography.fernet import Fernet
import random
import qrcode
import base64
from io import BytesIO


class MasrtechRegisterPartner(models.Model):
    _name = 'masrtech.register.partner'

    name = fields.Char(string='Company Name', required=True)
    company_address = fields.Char(string='Company Address', required=True)
    responsible_person = fields.Char(string='Responsible Person', required=True)
    job_title = fields.Char(string='Job Title')
    phone_number = fields.Char(string='Phone Number', required=True)
    email = fields.Char(string='Email', required=True)
    info = fields.Boolean(string='ركن تعريفي للشركة')
    workshop = fields.Boolean(string='تقديم ورشة عمل تفاعلية')
    interviews = fields.Boolean(string='تنظيم جلسات مقابلة شخصية')
    other = fields.Boolean(string='أنشطة أخرى')

    other_notes = fields.Text(String="Other activities")
    parking_space = fields.Selection([
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large')
    ], string='Parking Space')
    is_course = fields.Boolean(default=False)
    is_training = fields.Boolean(default=False)
    representatives = fields.Integer(string='Limit No of students')
    additional_equipment = fields.Text(string='Additional Equipment')
    training_opportunities = fields.Text(string='Training Opportunities')
    job_opportunities = fields.Text(string='Job Opportunities')
    type_sub = fields.Many2one('masrtech.sub', string='type')

    training_table = fields.One2many('registrar.partner.training.table', 'relation_id')
    opportunity_table = fields.One2many('registrar.partner.opportunity.table', 'relation_id',
                                        string='Training Relationship')
    reg_student_list = fields.One2many('training.registration', 'partner_id',
                                       string='Registration List')
    company_details_name = fields.Text(string='Company details')
    image = fields.Binary(string='Image')
    total_registered_students = fields.Integer('Total Registered', compute='_compute_student_counts', store=True)
    remaining_spots = fields.Integer('Remaining Students', compute='_compute_student_counts', store=True)
    course_product_id = fields.Many2one(
        'product.template',
        string='Course Product',
        domain=[('type', '=', 'service')]
    )
    university_ids = fields.Many2many(
        'masrtech.universities',
        string='Universities',
        help='If set, only students from these universities can see and register for this '
             'course/training. Leave empty to allow students from all universities.'
    )

    @api.depends('reg_student_list.registration_status', 'training_table.registered_count', 'training_table.capacity',
                 'training_table.weekly_schedule_ids.registered_count')
    def _compute_student_counts(self):
        for record in self:
            total_registered = 0
            total_capacity = 0

            for training in record.training_table:
                if training.is_weekly_breakdown and training.weekly_schedule_ids:
                    for week in training.weekly_schedule_ids:
                        confirmed_in_week = len(week.student_registrations.filtered(
                            lambda r: r.registration_status in ['confirmed']
                        ))
                        total_registered += confirmed_in_week
                else:
                    total_registered += training.registered_count or 0

                total_capacity += training.capacity or 0

            record.total_registered_students = total_registered
            record.remaining_spots = total_capacity - total_registered


class TrainingTableCategory(models.Model):
    _name = 'registrar.partner.training.table.category'
    _rec_name = 'training_name'
    training_name = fields.Char(string='Course Title')
    type = fields.Char(string='Course Title')


class TrainingTable(models.Model):
    _name = 'registrar.partner.training.table'
    _rec_name = 'training'

    training_title = fields.Char(string='Course Title')
    training = fields.Many2one('registrar.partner.training.table.category')
    duration = fields.Char(string='Duration')
    location = fields.Char(string='Location')
    code = fields.Char(string='Code')
    capacity = fields.Integer(string='Limit No of students')
    relation_id = fields.Many2one('masrtech.register.partner')
    cost = fields.Float(string='Price', compute='_compute_cost', store=True)
    is_weekly_breakdown = fields.Boolean(string='Enable Weekly Breakdown', default=False)
    total_weeks = fields.Integer(string='Total Weeks', default=1)
    students_per_week = fields.Integer(string='Students Per Week')
    training_start_date = fields.Date(string='Training Start Date')

    weekly_schedule_ids = fields.One2many('training.weekly.schedule', 'training_id', string='Weekly Schedule')

    training_registrations = fields.One2many('training.registration', 'training_course_id',
                                             string='Course Registrations')

    registered_count = fields.Integer(
        string='Total Registered Students',
        compute='_compute_course_stats',
        store=True)
    remaining_capacity = fields.Integer(
        string='Remaining Total Capacity',
        compute='_compute_course_stats',
        store=True)

    level_ids = fields.Many2many('level.year', string='Year Level')

    @api.depends('relation_id.course_product_id')
    def _compute_cost(self):
        for rec in self:
            if rec.relation_id and rec.relation_id.course_product_id:
                rec.cost = rec.relation_id.course_product_id.list_price
            else:
                rec.cost = 0.0

    @api.depends('capacity', 'weekly_schedule_ids.registered_count')
    def _compute_course_stats(self):
        for record in self:
            if record.id:
                if record.is_weekly_breakdown and record.weekly_schedule_ids:
                    total_registered = sum(record.weekly_schedule_ids.mapped('registered_count'))
                    record.registered_count = total_registered
                    record.remaining_capacity = (record.capacity or 0) - total_registered
                else:
                    registered = self.env['training.registration'].search_count([
                        ('training_course_id', '=', record.id),
                        ('registration_status', 'in', ['confirmed'])
                    ])
                    record.registered_count = registered
                    record.remaining_capacity = (record.capacity or 0) - registered
            else:
                record.registered_count = 0
                record.remaining_capacity = record.capacity or 0

    def get_next_available_week(self):
        available_weeks = self.weekly_schedule_ids.filtered(
            lambda w: w.is_week_available()
        ).sorted('week_number')

        return available_weeks[0] if available_weeks else False

    def get_current_active_week(self):
        for week in self.weekly_schedule_ids.sorted('week_number'):
            if week.is_week_available():
                return week
        return False

    # @api.onchange('is_weekly_breakdown', 'total_weeks', 'students_per_week', 'training_start_date')
    # def _onchange_weekly_breakdown(self):
    #     if self.is_weekly_breakdown and self.total_weeks and self.students_per_week and self.training_start_date:
    #         self._generate_weekly_schedule()
    #
    # def _generate_weekly_schedule(self):
    #     self.weekly_schedule_ids = [(5, 0, 0)]
    #
    #     if not self.training_start_date:
    #         return
    #
    #     schedule_lines = []
    #     start_date = self.training_start_date
    #
    #     for week in range(1, self.total_weeks + 1):
    #         week_start = start_date + timedelta(weeks=week - 1)
    #         week_end = week_start + timedelta(days=6)
    #
    #         schedule_lines.append((0, 0, {
    #             'week_number': week,
    #             'week_start_date': week_start,
    #             'week_end_date': week_end,
    #             'max_students': self.students_per_week,
    #             'registered_count': 0,
    #             'remaining_spots': self.students_per_week,
    #         }))
    #
    #     self.weekly_schedule_ids = schedule_lines

    # def generate_weekly_schedule_action(self):
    #     self._generate_weekly_schedule()
    #     return {
    #         'type': 'ir.actions.client',
    #         'tag': 'display_notification',
    #         'params': {
    #             'title': _('Success'),
    #             'message': _('Weekly schedule generated successfully!'),
    #             'type': 'success'
    #         }
    #     }


class TrainingWeeklySchedule(models.Model):
    _name = 'training.weekly.schedule'
    _description = 'Training Weekly Schedule'
    _rec_name = 'display_name'
    _order = 'week_number'

    training_id = fields.Many2one('registrar.partner.training.table', string='Training Course', required=True,
                                  ondelete='cascade')
    week_number = fields.Integer(string='Week Number', required=True)
    week_start_date = fields.Date(string='Week Start Date', required=True)
    week_end_date = fields.Date(string='Week End Date', required=True)
    max_students = fields.Integer(string='Max Students This Week', required=True)
    registered_count = fields.Integer(string='Registered Students', compute='_compute_registered_count', store=True)
    remaining_spots = fields.Integer(string='Remaining Spots', compute='_compute_remaining_spots', store=True)

    is_full = fields.Boolean(string='Week Full', compute='_compute_week_status', store=True)
    is_active = fields.Boolean(string='Currently Active', compute='_compute_week_status', store=True)

    student_registrations = fields.One2many('training.registration', 'weekly_schedule_id', string='Week Registrations')

    company_id = fields.Many2one('masrtech.register.partner', string='Company Name',
                                 related='training_id.relation_id', store=True, readonly=True)

    display_name = fields.Char(string='Display Name', compute='_compute_display_name', store=True)
    template_id = fields.Many2one('ir.ui.view', string='Template')
    template_xml_id = fields.Char(string='Template XML ID', related='template_id.key')
    template_encrypted_key = fields.Char(string='Template Encrypted Key')
    link = fields.Char()

    @api.depends('training_id', 'week_number', 'week_start_date', 'week_end_date', 'company_id')
    def _compute_display_name(self):
        for record in self:
            if record.training_id and record.week_number and record.company_id:
                training_name = record.training_id.training.training_name or record.training_id.training_title or 'Training'
                record.display_name = f"{record.company_id.name} - {training_name} - Week {record.week_number} ({record.week_start_date} to {record.week_end_date})"
            elif record.training_id and record.week_number:
                training_name = record.training_id.training.training_name or record.training_id.training_title or 'Training'
                record.display_name = f"{training_name} - Week {record.week_number} ({record.week_start_date} to {record.week_end_date})"
            else:
                record.display_name = f"Week {record.week_number or 0}"

    @api.depends('student_registrations', 'student_registrations.registration_status')
    def _compute_registered_count(self):
        for record in self:
            if record.student_registrations:
                confirmed_registrations = record.student_registrations.filtered(
                    lambda r: r.registration_status in ['confirmed']
                )
                record.registered_count = len(confirmed_registrations)
            else:
                record.registered_count = 0

    @api.depends('max_students', 'registered_count')
    def _compute_remaining_spots(self):
        for record in self:
            record.remaining_spots = (record.max_students or 0) - (record.registered_count or 0)

    @api.depends('max_students', 'registered_count')
    def _compute_week_status(self):
        for record in self:
            record.is_full = record.remaining_spots <= 0

            record.is_active = False
            if record.training_id and record.training_id.is_weekly_breakdown:
                weeks_before = record.training_id.weekly_schedule_ids.filtered(
                    lambda w: w.week_number < record.week_number and w.remaining_spots > 0
                )
                record.is_active = (not weeks_before and record.remaining_spots > 0)

    def action_create_discussion_channel(self):

        if not self.student_registrations:
            raise UserError(_('No registered students found for this week.'))

        channel_name = f"{self.display_name}"

        confirmed_registrations = self.student_registrations.filtered(
            lambda r: r.registration_status == 'confirmed'
        )
        partner_ids = []
        for registration in confirmed_registrations:
            if registration.student_id:
                partner_ids.append(registration.student_namee.id)

        channel_vals = {
            'name': channel_name,
            'channel_type': 'channel',
            'student_idss': [(6, 0, partner_ids)],
            'group_public_id': False,
        }
        channel = self.env['discuss.channel'].create(channel_vals)
        self.discussion_channel_id = channel.id
        self.invitation_url = channel.invitation_url
        self.create_qweb_template()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success!'),
                'message': _('Discussion channel "%s" created successfully with %d students.') % (
                    channel_name, len(partner_ids) - 1),
                'sticky': False,
                'type': 'success'
            }
        }

    discussion_channel_id = fields.Many2one('discuss.channel', 'Discussion Channel')
    invitation_url = fields.Char('Invitation URL')

    def get_session(self):
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': f'https://borg-arab.com{self.invitation_url}'
        }

    def create_qweb_template(self, preview=''):
        for rec in self:
            random_int = random.randint(1, 100000)
            display_name = f"{rec.company_id.name}_Week{rec.week_number}({rec.week_start_date}_{rec.week_end_date})_{random_int}"
            channel_id = rec.discussion_channel_id.id if rec.discussion_channel_id else ''

            key = 'nexus_nms.' + str(display_name).lower().replace(" ", "_") + preview
            arch = ""
            arch += '<t t-name="' + key + '">'
            arch += """
                      <head>
            <meta charset="UTF-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
            <title>NEXUS - Meeting Invitation</title>
            <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css"
                  rel="stylesheet"/>
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
                  rel="stylesheet"/>
            <style>
                :root {
                --primary-gradient: linear-gradient(135deg, #29abe2 0%, #24557b 100%);
                --card-gradient: linear-gradient(135deg, #3b82f6, #1d4ed8);
                --orange-gradient: linear-gradient(135deg, #f97316, #ea580c);
                --yellow-gradient: linear-gradient(135deg, #f59e0b, #d97706);
                --blue-gradient: linear-gradient(135deg, #3b82f6, #1d4ed8);
                }

                * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                }

                body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: var(--primary-gradient);
                min-height: 100vh;
                overflow-x: hidden;
                position: relative;
                }
                .main-container {
                min-height: 100vh;
                position: relative;
                z-index: 2;
                }

                .invitation-card {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(20px);
                border-radius: 24px;
                box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.3);
                position: relative;
                overflow: hidden;
                animation: slideInUp 1s ease-out;
                max-width: 700px;
                margin: 0 auto;
                }

                @keyframes slideInUp {
                from {
                opacity: 0;
                transform: translateY(60px);
                }
                to {
                opacity: 1;
                transform: translateY(0);
                }
                }

                /* Shimmer effect */
                .invitation-card::before {
                content: '';
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.1), transparent);
                transform: rotate(45deg);
                animation: shimmer 4s ease-in-out infinite;
                pointer-events: none;
                }

                @keyframes shimmer {
                0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
                50% { transform: translateX(100%) translateY(100%) rotate(45deg); }
                100% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
                }

                .invitation-title {
                color: #1f2937;
                font-weight: 600;
                font-size: 1.8rem;
                position: relative;
                z-index: 1;
                animation: titleSlide 1s ease-out 0.6s both;
                }

                @keyframes titleSlide {
                from {
                opacity: 0;
                transform: translateX(-30px);
                }
                to {
                opacity: 1;
                transform: translateX(0);
                }
                }

                .form-section {
                position: relative;
                z-index: 1;
                animation: formFadeIn 1s ease-out 0.9s both;
                }

                @keyframes formFadeIn {
                from {
                opacity: 0;
                transform: translateY(40px);
                }
                to {
                opacity: 1;
                transform: translateY(0);
                }
                }

                .form-label {
                color: #4b5563;
                font-weight: 500;
                font-size: 1.1rem;
                }

                .form-control {
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                padding: 1rem 1.25rem;
                font-size: 1.1rem;
                background: rgba(255, 255, 255, 0.9);
                transition: all 0.3s ease;
                animation: inputReady 0.5s ease-out 1.2s both;
                }

                @keyframes inputReady {
                from {
                transform: scale(0.95);
                opacity: 0;
                }
                to {
                transform: scale(1);
                opacity: 1;
                }
                }

                .form-control:focus {
                border-color: #3b82f6;
                box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.15);
                transform: translateY(-2px);
                background: rgba(255, 255, 255, 1);
                }

                /* FIXED: Changed from .btn-join to .join-btn to match HTML */
                .join-btn {
                background: var(--card-gradient);
                border: none;
                border-radius: 12px;
                padding: 1.1rem 2.5rem;
                font-size: 1.2rem;
                font-weight: 600;
                color: white;
                position: relative;
                overflow: hidden;
                transition: all 0.4s ease;
                animation: buttonEntrance 0.8s ease-out 1.5s both;
                }

                @keyframes buttonEntrance {
                from {
                transform: translateY(20px) scale(0.9);
                opacity: 0;
                }
                to {
                transform: translateY(0) scale(1);
                opacity: 1;
                }
                }

                .join-btn::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
                transition: left 0.6s ease;
                }

                .join-btn:hover {
                transform: translateY(-4px);
                box-shadow: 0 15px 35px rgba(59, 130, 246, 0.4);
                filter: brightness(1.1);
                }

                .join-btn:hover::before {
                left: 100%;
                }

                .join-btn:active {
                transform: translateY(-2px);
                }

                .btn-icon {
                transition: transform 0.3s ease;
                margin-left: 8px;
                }

                .join-btn:hover .btn-icon {
                transform: translateX(5px);
                }


                /* Responsive adjustments */
                @media (max-width: 768px) {
                .logo-text {
                font-size: 2.5rem;
                letter-spacing: -2px;
                }

                .invitation-title {
                font-size: 1.5rem;
                }

                .logo-block {
                width: 28px;
                height: 28px;
                }
                }

                @media (max-width: 576px) {
                .invitation-card {
                margin: 1rem;
                border-radius: 20px;
                }

                .logo-text {
                font-size: 2rem;
                }

                .invitation-title {
                font-size: 1.3rem;
                }
                }
            </style>
        </head>
        <body class="bg-particles">
            <div class="container-fluid main-container d-flex align-items-center justify-content-center">
                <div class="row w-100 justify-content-center">
                    <div class="col-12 col-md-8 col-lg-6 col-xl-5">
                        <div class="invitation-card p-5">
                            <!-- Logo Section -->
                            <div class="text-center">
                                <img src="/nexus_nms/static/src/images/nexus-sq.png" class="w-75"/>
                            </div>

                            <!-- Invitation Text -->
                            <h1 class="invitation-title text-center mb-0 p-3 p-md-5">
                                You've been invited to a meeting!
                            </h1>

                            <!-- Form Section - FIXED: Added method and name attributes -->
                            <form method="get" action="">
                                <div class="mb-4">
                                    <label for="studentId" class="form-label">Student ID</label>
                                    <input type="text" 
                                           id="student-id" 
                                           name="student_id"
                                           placeholder="Enter your Student ID" 
                                           class="form-control"/>
                                    <input type="hidden" id="channel-id" name="channel_id" value="{channel_id}"/>
                                </div>

                                <div class="text-center">
                                    <button type="submit" class="join-btn">
                                        Join Us
                                        <i class="fas fa-arrow-right btn-icon"></i>
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>

            <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/js/bootstrap.bundle.min.js"></script>
            <script>
                    <![CDATA[
                    document.addEventListener('DOMContentLoaded', function() {{
                        const form = document.querySelector('form');
                        const joinBtn = document.querySelector('.join-btn');
                        const studentIdInput = document.getElementById('student-id');
                        const channelIdInput = document.getElementById('channel-id');
                        
                        // FIXED: Proper form submission handler
                        form.addEventListener('submit', function(e) {{
                            e.preventDefault();
                            
                            const studentId = studentIdInput.value.trim();
                            const channelId = channelIdInput.value;
                            
                            if (!studentId) {{
                                alert('Please enter your Student ID');
                                return;
                            }}
                            
                            // FIXED: Proper URL building
                            const url = new URL(window.location.href);
                            url.searchParams.set('student_id', studentId);
                            if (channelId) {{
                                url.searchParams.set('channel_id', channelId);
                            }}
                            
                            window.location.href = url.toString();
                        }});
                        
                        // Handle Enter key press - FIXED: Variable name
                        studentIdInput.addEventListener('keypress', function(e) {{
                            if (e.key === 'Enter') {{
                                e.preventDefault();
                                form.dispatchEvent(new Event('submit'));
                            }}
                        }});
                    }});
                    ]]>
                </script>
            </body></t>
                       """
            existing_template = self.env['ir.ui.view'].search([('key', '=', key)], limit=1)
            if existing_template:
                existing_template.write({
                    'arch': arch,
                    'name': rec.template_name
                })
                rec.template_id = existing_template.id
            else:
                temp = self.env['ir.ui.view'].create({
                    'name': display_name,
                    'type': 'qweb',
                    'key': key,
                    'xml_id': key,
                    'arch': arch
                })

                rec.template_id = temp.id

            icp = self.env['ir.config_parameter'].sudo()
            secret_key = icp.get_param('nexus_nms.template_encryption_key', '')
            if not secret_key:
                secret_key = Fernet.generate_key().decode()
                icp.set_param('nexus_nms.template_encryption_key', secret_key)
            key = secret_key.encode()
            f = Fernet(key)
            rec.template_encrypted_key = f.encrypt(rec.template_xml_id.encode())
            rec.link = f'https://borg-arab.com/template/{rec.template_encrypted_key}'

    def is_week_full(self):
        return self.remaining_spots <= 0

    def is_week_available(self):
        return self.remaining_spots > 0

    # @api.constrains('registered_count', 'max_students')
    # def _check_max_students(self):
    #     for record in self:
    #         if record.registered_count > record.max_students:
    #             raise ValidationError(
    #                 _('Week %s has exceeded maximum students limit (%s/%s)') %
    #                 (record.week_number, record.registered_count, record.max_students)
    #             )

    def action_view_registrations(self):
        return {
            'name': f'{self.company_id.name} - Week {self.week_number} - Registered Students',
            'type': 'ir.actions.act_window',
            'res_model': 'training.registration',
            'view_mode': 'tree,form',
            'domain': [('weekly_schedule_id', '=', self.id)],
            'context': {
                'default_weekly_schedule_id': self.id,
                'default_training_course_id': self.training_id.id,
                'default_partner_id': self.company_id.id,
            },
        }

    @api.model
    def get_company_weeks(self, company_id, training_id=None):
        domain = [('company_id', '=', company_id)]
        if training_id:
            domain.append(('training_id', '=', training_id))
        return self.search(domain)

    @api.model
    def get_available_company_weeks(self, company_id, training_id=None):
        domain = [
            ('company_id', '=', company_id),
            ('remaining_spots', '>', 0)
        ]
        if training_id:
            domain.append(('training_id', '=', training_id))
        return self.search(domain)

    @api.model
    def check_student_access(self, invitation_url, student_id):
        """Simple validation for student access"""

        training = self.search([('invitation_url', '=', invitation_url)], limit=1)
        if not training:
            return False

        # Check if student is registered
        registration = self.env['training.registration'].search([
            ('student_id', '=', student_id),
            ('training_schedule_id', '=', training.id),
            ('registration_status', '=', 'confirmed')
        ], limit=1)

        return bool(registration)


class JopOpportunity(models.Model):
    _name = 'registrar.partner.opportunity.table'

    jop_title = fields.Char(string='JOP TITLE')
    experience = fields.Char(string='Experience')
    location = fields.Char(string='Location')
    qualification = fields.Char(string='Qualification')
    extra_skills = fields.Char(string='Extra Skills')
    relation_id = fields.Many2one('masrtech.register.partner')


class TrainingRegistration(models.Model):
    _name = 'training.registration'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    _description = 'Training Registration'
    _rec_name = 'student_namee'

    student_namee = fields.Many2one('op.student', string='Student Name')
    email = fields.Char(string='Email Address')
    vat = fields.Char(string='National ID')
    phone = fields.Char(string='Phone Number')
    weekly_schedule_id = fields.Many2one('training.weekly.schedule', string='Assigned Week')

    university_id = fields.Many2one('masrtech.universities', string='University')
    faculty_id = fields.Many2one('masrtech.faculty', string='Faculty')
    student_id = fields.Char(string='Faculty ID')
    year_level = fields.Selection([
        ('one', 'First Year'),
        ('two', 'Second Year'),
        ('three', 'Third Year'),
        ('fourth', 'Four Year'),
    ], string='Year Level')
    gpa = fields.Float(string='GPA')
    department_id = fields.Many2one('op.department', string='Program')
    attachment = fields.Binary(string='Attachment')
    training_course_id = fields.Many2one('registrar.partner.training.table', string='Training Course')
    partner_id = fields.Many2one('masrtech.register.partner', string='Training Partner')
    invoice_id = fields.Many2one('account.move', string='Invoice')

    payment_method = fields.Selection([
        ('fawry', 'Pay With Fawry'),
        ('paymob', 'Pay With Paymob'),
    ], string='Payment Method')

    payment_way=fields.Many2one('payment.way',string='Payment Way')

    registration_status = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
    ], string='Status', default='draft')
    course_status = fields.Selection([
        ('upcoming', 'Up Coming'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ], string='Status', default='upcoming', tracking=True)
    is_course = fields.Boolean(default=False)
    student_name_en = fields.Char(
        string='Full Name (English)',
        tracking=True,
    )

    def _update_status_based_on_dates(self):
        """Update registration status based on training dates"""
        for record in self:
            if not record.training_start_date or not record.training_end_date:
                continue

            today = date.today()
            if record.course_status == 'confirmed':
                if today < record.training_start_date:
                    record.course_status = 'upcoming'
                elif record.training_start_date <= today <= record.training_end_date:
                    record.course_status = 'in_progress'
                elif today > record.training_end_date:
                    record.course_status = 'completed'
            elif record.course_status == 'upcoming':
                if record.training_start_date <= today <= record.training_end_date:
                    record.course_status = 'in_progress'
                elif today > record.training_end_date:
                    record.course_status = 'completed'
            elif record.course_status == 'in_progress':
                if today > record.training_end_date:
                    record.course_status = 'completed'

    @api.model
    def _cron_update_training_status(self):
        """Cron job to automatically update training status based on dates"""
        registrations = self.search([
            ('course_status', 'in', ['draft', 'upcoming', 'in_progress','completed']),
            ('training_start_date', '!=', False),
            ('training_end_date', '!=', False),
        ])

        for registration in registrations:
            registration._update_status_based_on_dates()

    training_start_date = fields.Date(string='Training Start Date', compute='_compute_training_dates', store=True)
    training_end_date = fields.Date(string='Training End Date', compute='_compute_training_dates', store=True)

    @api.depends('weekly_schedule_id', 'training_course_id')
    def _compute_training_dates(self):
        for record in self:
            if record.weekly_schedule_id:
                record.training_start_date = record.weekly_schedule_id.week_start_date
                record.training_end_date = record.weekly_schedule_id.week_end_date
            else:
                record.training_start_date = False
                record.training_end_date = False
    def _post_invoice_from_confirmation(self):
        for record in self:
            desired_name = record._get_student_display_name()
            invoice = record.invoice_id or record.create_draft_invoice()
            if invoice and desired_name and invoice.partner_id and not invoice.partner_id.is_company and invoice.partner_id.name != desired_name:
                invoice.partner_id.sudo().write({'name': desired_name})
            if invoice and invoice.state == 'draft':
                invoice.sudo().action_post()
            if invoice and invoice.amount_total == 0 and invoice.payment_state != 'paid':
                invoice.sudo()._compute_amount()
                invoice.sudo()._compute_payment_state()

    def action_confirm_registration(self):
        for record in self:
            if record.weekly_schedule_id:
                current_week = record.weekly_schedule_id

                if current_week.remaining_spots < 1:
                    next_week = record.env['training.weekly.schedule'].search([
                        ('training_id', '=', current_week.training_id.id),
                        ('week_number', '>', current_week.week_number),
                        ('remaining_spots', '>', 0)
                    ], order='week_number', limit=1)

                    if next_week:
                        record.weekly_schedule_id = next_week
                        record.registration_status = 'confirmed'
                        record._generate_qr_code()
                        record.add_course_to_student()
                        record._post_invoice_from_confirmation()

                        return {
                            'type': 'ir.actions.client',
                            'tag': 'display_notification',
                            'params': {
                                'title': 'Registration Confirmed with Transfer',
                                'message': f'Week {current_week.week_number} was full. Student transferred to Week {next_week.week_number}',
                                'type': 'warning',
                                'sticky': True,
                            }
                        }
                    else:
                        raise ValidationError('Week is full and no next available week found!')
                else:
                    record.registration_status = 'confirmed'
                    record._generate_qr_code()
                    record.add_course_to_student()
                    record._post_invoice_from_confirmation()


            else:
                record.registration_status = 'confirmed'
                record._generate_qr_code()
                record.add_course_to_student()
                record._post_invoice_from_confirmation()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Registration Confirmed',
                'message': 'Student registration confirmed successfully',
                'type': 'success',
            }
        }

    def cron_add_courses_to_students(self):
        registrations = self.search([
            ('registration_status', '=', 'confirmed'),
            ('partner_id', '!=', False)
        ])

        for record in registrations:
            if record.student_namee and record.partner_id.is_course :
                student = self.env['op.student'].search([
                    ('id', '=', record.student_namee.id)
                ], limit=1)

                if student and record.partner_id.id not in student.courses_id.ids:
                    student.write({
                        'courses_id': [(4, record.partner_id.id)]
                    })

    def add_course_to_student(self):
        for record in self:
            if record.student_namee and record.partner_id.is_course :
                student = self.env['op.student'].search([
                    ('id', '=', record.student_namee.id)
                ], limit=1)

                if student and record.partner_id.id not in student.courses_id.ids:
                    student.write({
                        'courses_id': [(4, record.partner_id.id)]
                    })

    def _get_student_display_name(self):
        self.ensure_one()
        if self.student_namee and self.student_namee.name:
            return self.student_namee.name
        student = False
        if self.student_id:
            student = self.env['op.student'].sudo().search([('student_id', '=', self.student_id)], limit=1)
            if not student:
                student = self.env['op.student'].sudo().search([('faculty_id', '=', self.student_id)], limit=1)
        if not student and self.email:
            student = self.env['op.student'].sudo().search([('email', '=', self.email)], limit=1)
        if not student and self.phone:
            student = self.env['op.student'].sudo().search([('mobile', '=', self.phone)], limit=1)
        if student and student.name:
            if not self.student_namee:
                self.student_namee = student.id
            return student.name
        return False

    def _get_invoice_partner(self):
        self.ensure_one()
        desired_name = self._get_student_display_name()
        partner = False
        if self.email:
            partner = self.env['res.partner'].sudo().search([('email', '=', self.email)], limit=1)
        if not partner and self.phone:
            partner = self.env['res.partner'].sudo().search([('phone', '=', self.phone)], limit=1)
        if not partner and desired_name:
            partner = self.env['res.partner'].sudo().search([
                ('name', '=', desired_name)
            ], limit=1)
        if partner and desired_name and not partner.is_company and partner.name != desired_name:
            partner.sudo().write({'name': desired_name})
        if not partner:
            partner = self.env['res.partner'].sudo().create({
                'name': desired_name or 'Training Student',
                'email': self.email or False,
                'phone': self.phone or False,
            })
        return partner

    def _get_invoice_product(self):
        self.ensure_one()
        if self.partner_id and self.partner_id.course_product_id:
            return self.partner_id.course_product_id.product_variant_id
        return False

    def _get_income_account(self):
        self.ensure_one()
        product = self._get_invoice_product()
        if product:
            return product.property_account_income_id or product.categ_id.property_account_income_categ_id
        return self.env['account.account'].search([
            ('account_type', '=', 'income'),
            ('company_id', '=', self.env.company.id)
        ], limit=1)

    def _get_invoice_number(self):
        self.ensure_one()
        sequence = self.env['ir.sequence'].sudo().search([
            ('code', '=', 'training.registration.invoice'),
            ('company_id', 'in', [self.env.company.id, False]),
        ], limit=1)
        if not sequence:
            sequence = self.env['ir.sequence'].sudo().create({
                'name': 'Training Registration Invoice',
                'code': 'training.registration.invoice',
                'prefix': 'TRI/%(year)s/',
                'padding': 5,
                'company_id': self.env.company.id,
            })
        return sequence.next_by_id()

    def create_draft_invoice(self):
        self.ensure_one()
        if self.invoice_id:
            return self.invoice_id
        partner = self._get_invoice_partner()
        product = self._get_invoice_product()
        price_unit = self.training_course_id.cost or (product and product.lst_price) or 0.0
        invoice_date = self.registration_date.date() if self.registration_date else fields.Date.context_today(self)
        student_display = self._get_student_display_name() or 'Student'
        email_display = self.email or ''
        university_display = self.university_id.name if self.university_id else ''
        training_display = ''
        if self.training_course_id:
            training_display = self.training_course_id.training_title or (self.training_course_id.training and self.training_course_id.training.training_name) or ''
        if not training_display and self.partner_id:
            training_display = self.partner_id.name or ''
        line_name_parts = [
            f"Student: {student_display}",
            f"Email: {email_display}",
            f"Training: {training_display}",
            f"University: {university_display}",
        ]
        line_name = " | ".join([part for part in line_name_parts if part.split(": ")[1]])
        line_vals = {
            'name': line_name or (self.training_course_id.training_title or self.partner_id.name or 'Training Registration'),
            'quantity': 1.0,
            'price_unit': price_unit,
        }
        if product:
            line_vals['product_id'] = product.id
        else:
            account = self._get_income_account()
            if account:
                line_vals['account_id'] = account.id
        move_vals = {
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'invoice_origin': self.training_course_id.training_title or self.partner_id.name or 'Training Registration',
            'invoice_date': invoice_date,
            'invoice_date_due': invoice_date,
            'name': self._get_invoice_number(),
            'invoice_line_ids': [(0, 0, line_vals)],
        }
        move = self.env['account.move'].sudo().create(move_vals)
        self.invoice_id = move.id
        return move

    registration_date = fields.Datetime(string='Registration Date', default=fields.Datetime.now)

    @api.onchange('training_course_id')
    def _onchange_training_course(self):
        if self.training_course_id and self.training_course_id.is_weekly_breakdown:
            available_week = self.training_course_id.get_current_active_week()

            if available_week:
                self.weekly_schedule_id = available_week
            else:
                self.weekly_schedule_id = False
                return {
                    'warning': {
                        'title': _('No Available Spots'),
                        'message': _('All weeks are fully booked for this training course.')
                    }
                }
        else:
            self.weekly_schedule_id = False

    @api.onchange('weekly_schedule_id')
    def _onchange_assigned_week(self):
        if self.weekly_schedule_id:
            if self.weekly_schedule_id.training_id:
                self.training_course_id = self.weekly_schedule_id.training_id

                if self.training_course_id.relation_id:
                    self.partner_id = self.training_course_id.relation_id
        else:
            self.training_course_id = False
            self.partner_id = False

    def unassign_weeks(self):
        active_ids = self._context.get('active_id')
        active_ids_ref = self.env['training.registration'].browse(active_ids)
        for re in active_ids_ref:
            re.weekly_schedule_id = False
    qr_code_image = fields.Binary(string='QR Code', readonly=True)
    qr_code_filename = fields.Char(string='QR Code Filename', readonly=True)
    qr_code_url = fields.Char(string='QR Code URL', readonly=True)

    def action_generate_qr_for_old_confirmed_records(self):
        old_confirmed_without_qr = self.search([
            ('registration_status', '=', 'confirmed'),
            ('student_id', '!=', False),
            '|',
            ('qr_code_image', '=', False),
            ('qr_code_image', '=', None)
        ])

        if not old_confirmed_without_qr:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'No Records Found',
                    'message': 'No old confirmed records without QR codes found',
                    'type': 'info',
                }
            }

        success_count = 0
        for record in old_confirmed_without_qr:
            try:
                record._generate_qr_code()
                success_count += 1
            except:
                pass  # Continue with other records

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'QR Generation Complete',
                'message': f'Generated QR codes for {success_count} old confirmed records',
                'type': 'success',
                'sticky': True,
            }
        }

    def action_download_qr_code(self):
        if not self.qr_code_image:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'No QR Code',
                    'message': 'This record does not have a QR code. Generate one first.',
                    'type': 'warning',
                }
            }

        attachment = self.env['ir.attachment'].create({
            'name': self.qr_code_filename or f'qr_code_{self.student_id or self.id}.png',
            'type': 'binary',
            'datas': self.qr_code_image,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'image/png',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
    def _generate_qr_code(self):
        for record in self:
            if not record.student_id:
                continue

            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', 'https://borg-arab.com')
            qr_url = f"{base_url}/training_pagee?student_id={record.student_id}"

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=12,
                border=4,
            )
            qr.add_data(qr_url)
            qr.make(fit=True)

            qr_img = qr.make_image(fill_color="black", back_color="white")

            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            qr_code_data = buffer.getvalue()
            buffer.close()

            qr_code_b64 = base64.b64encode(qr_code_data)

            record.write({
                'qr_code_image': qr_code_b64,
                'qr_code_filename': f'qr_code_{record.student_id}_{record.id}.png',
                'qr_code_url': qr_url,
            })
    def assign_weeks(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Assign Week',
            'res_model': 'assign.week.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_registrations': [
                    (6, 0, self.env['training.registration'].browse(self._context.get('active_ids')).ids)],
            },
        }

    @api.model
    def create(self, vals):
        result = super().create(vals)

        if result.training_course_id and result.training_course_id.is_weekly_breakdown and not result.weekly_schedule_id:
            available_week = result.training_course_id.get_current_active_week()

            if available_week:
                result.weekly_schedule_id = available_week

        if result.training_course_id:
            result.training_course_id._compute_course_stats()
        if result.weekly_schedule_id:
            result.weekly_schedule_id._compute_registered_count()
            result.weekly_schedule_id._compute_remaining_spots()
            result.weekly_schedule_id._compute_week_status()
        if result.partner_id:
            result.partner_id._compute_student_counts()

        return result

    def write(self, vals):
        old_courses = self.mapped('training_course_id')
        old_weeks = self.mapped('weekly_schedule_id')
        old_partners = self.mapped('partner_id')

        result = super().write(vals)

        new_courses = self.mapped('training_course_id')
        new_weeks = self.mapped('weekly_schedule_id')
        new_partners = self.mapped('partner_id')

        all_courses = set(old_courses + new_courses)
        all_weeks = set(old_weeks + new_weeks)
        all_partners = set(old_partners + new_partners)

        for course in all_courses:
            if course:
                course._compute_course_stats()

        for week in all_weeks:
            if week:
                week._compute_registered_count()
                week._compute_remaining_spots()
                week._compute_week_status()

        for partner in all_partners:
            if partner:
                partner._compute_student_counts()
        if 'student_id' in vals and self.registration_status == 'confirmed':
            for record in self:
                if record.student_id:
                    record._generate_qr_code()

        return result

    def unlink(self):
        affected_courses = self.mapped('training_course_id')
        affected_weeks = self.mapped('weekly_schedule_id')
        affected_partners = self.mapped('partner_id')

        result = super().unlink()

        for course in affected_courses:
            if course.exists():
                course._compute_course_stats()
        for week in affected_weeks:
            if week.exists():
                week._compute_registered_count()
                week._compute_remaining_spots()
                week._compute_week_status()
        for partner in affected_partners:
            if partner.exists():
                partner._compute_student_counts()

        return result


class WorklistModel(models.Model):
    _name = 'worklist.model'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)

    def get_pacs_data(self):
        return True


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        res = super().action_post()
        registrations = self.env['training.registration'].sudo().search([
            ('invoice_id', 'in', self.ids)
        ])
        if registrations:
            registrations.write({'registration_status': 'confirmed'})
            registrations._generate_qr_code()
            registrations.add_course_to_student()
        return res


class Level(models.Model):
    _name = 'level.year'
    _rec_name = 'name'

    name = fields.Char(string='Level year', required=True)


class InheritDiscussChannel(models.Model):
    _inherit = 'discuss.channel'
    student_ids = fields.Many2many('op.student', 'student_id_ref')
    student_idss = fields.One2many('op.student', 'student_id_reff')


class AssignWeekly(models.TransientModel):
    _name = 'assign.week.wizard'

    weekly_schedule_id = fields.Many2one('training.weekly.schedule', string='Assigned Week', required=True)
    registrations = fields.Many2many('training.registration', string='Registrations')

    def confirm(self):
        for rec in self:
            todo = rec.registrations
            week = rec.weekly_schedule_id
            if week and week.max_students and (week.registered_count + len(todo)) > week.max_students:
                raise ValidationError(_(
                    'Cannot assign %s registrations to Week %s: only %s spot(s) remaining.'
                ) % (len(todo), week.week_number, week.remaining_spots))
            for re in todo:
                re.weekly_schedule_id = week.id
