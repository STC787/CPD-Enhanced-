from odoo import api, models, fields, _
from odoo.exceptions import UserError


class InheritSurvey(models.Model):
    _inherit = 'survey.survey'

    date_from = fields.Datetime(string='Date From')
    date_to = fields.Datetime(string='Date To')
    faculty_id = fields.Many2one('op.faculty')
    state = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ], string='State', compute='compute_state', store=True, tracking=True)
    training_course_id = fields.Many2one('registrar.partner.training.table', string='Training Course')

    @api.depends('date_from', 'date_to')
    def compute_state(self):
        now = fields.Datetime.now()
        for record in self:
            if record.date_to and record.date_to <= now:
                record.state = 'inactive'
            elif record.date_from and record.date_from > now:
                record.state = 'inactive'
            elif record.date_from or record.date_to:
                record.state = 'active'
            else:
                record.state = False

    def _is_deadline_expired(self):
        self.ensure_one()
        return bool(self.date_to and self.date_to <= fields.Datetime.now())

    def _is_not_yet_open(self):
        self.ensure_one()
        return bool(self.date_from and self.date_from > fields.Datetime.now())

    def _check_answer_creation(self, *args, **kwargs):
        # Block new answers outside the survey's [date_from, date_to] window, on
        # top of whatever core validation already runs (attempts left, closed/archived, ...).
        if self._is_not_yet_open():
            raise UserError(_('This survey is not open yet.'))
        if self._is_deadline_expired():
            raise UserError(_('This survey has expired and no longer accepts answers.'))
        return super(InheritSurvey, self)._check_answer_creation(*args, **kwargs)

    def get_start_url(self):
        self.ensure_one()
        # Route fresh invite/share links through our name-registration gate first;
        # resuming an existing answer (answer_token in the querystring) still goes
        # straight to core's /survey/start/ via the controller, see survey_registration.py.
        return '/survey/register/%s' % self.access_token

    def _cron_expire_surveys(self):
        """Archive surveys whose end date has passed so the standard survey
        'closed' page is shown to anyone trying to open or resume the link."""
        expired = self.search([
            ('date_to', '!=', False),
            ('date_to', '<=', fields.Datetime.now()),
            ('active', '=', True),
        ])
        if expired:
            expired.compute_state()
            expired.write({'active': False})

    @api.model_create_multi
    def create(self, vals_list):
        surveys = super(InheritSurvey, self).create(vals_list)
        for survey_sudo in surveys.filtered(lambda survey: survey.certification_give_badge).sudo():
            survey_sudo._create_certification_badge_trigger()

        Registration = self.env['training.registration'].sudo()
        Student = self.env['op.student'].sudo()

        students = Student.search([])

        for student in students:
            registration = Registration.search([
                ('student_namee', '=', student.id),
                ('training_course_id', '=', surveys.training_course_id.id),
                ('course_status', '=', 'completed'),
            ])

            if registration:
                student.write({
                    'quiz_ids': [(0, 0, {
                        'exam_id': surveys.id,
                        'training_course_id': surveys.training_course_id.id,
                    })]
                })

        return surveys
