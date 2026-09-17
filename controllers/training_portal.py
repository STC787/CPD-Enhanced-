# -*- coding: utf-8 -*-
import json
from odoo import http, _
from odoo.http import request
from odoo.exceptions import ValidationError
import re


class TrainingPortalController(http.Controller):

    # ── Main form ─────────────────────────────────────────────────────────────

    @http.route('/training/register', type='http', auth='public', website=True, csrf=False)
    def training_form(self, **kw):
        companies    = request.env['masrtech.register.partner'].sudo().search([('is_training', '=', True)])
        levels       = request.env['level.year'].sudo().search([])
        universities = request.env['masrtech.universities'].sudo().search([])
        return request.render('nexus_nms.training_portal_registration_form', {
            'error':         {},
            'error_message': [],
            'form_data':     {},
            'companies':     companies,
            'levels':        levels,
            'universities':  universities,
        })

    # ── AJAX: training companies filtered by student's university ────────────
    # If a company has university_ids set, it is only shown to students from
    # one of those universities. If university_ids is empty, the company is
    # visible to students from any university.

    @http.route('/training/ajax/companies', type='http', auth='public', website=True, csrf=False)
    def ajax_get_companies(self, university_id=None, **kw):
        domain = [('is_training', '=', True)]
        try:
            uid = int(university_id) if university_id else 0
        except (ValueError, TypeError):
            uid = 0

        companies = request.env['masrtech.register.partner'].sudo().search(domain)
        if uid:
            companies = companies.filtered(
                lambda c: not c.university_ids or uid in c.university_ids.ids
            )
        else:
            companies = companies.filtered(lambda c: not c.university_ids)

        result = [{'id': c.id, 'name': c.name} for c in companies]
        return request.make_response(
            json.dumps(result),
            headers=[('Content-Type', 'application/json')],
        )

    # ── AJAX: programs filtered by company + level ────────────────────────────

    @http.route('/training/ajax/programs', type='http', auth='public', website=True, csrf=False)
    def ajax_get_programs(self, company_id=None, level_id=None, **kw):
        result = []
        try:
            cid = int(company_id) if company_id else 0
            lid = int(level_id)   if level_id   else 0
        except (ValueError, TypeError):
            cid = lid = 0

        if cid:
            domain = [('relation_id', '=', cid)]
            programs = request.env['registrar.partner.training.table'].sudo().search(domain)
            # Filter by level in Python to avoid ORM Many2many domain issues
            if lid:
                programs = programs.filtered(lambda p: lid in p.level_ids.ids)
            for p in programs:
                display = p.training_title or (p.training.training_name if p.training else '') or p.code or str(p.id)
                result.append({
                    'id':   p.id,
                    'name': display,
                    'code': p.code or '',
                    'level_ids': [
                        {'id': l.id, 'name': l.name}
                        for l in p.level_ids
                    ],
                })
        return request.make_response(
            json.dumps(result),
            headers=[('Content-Type', 'application/json')],
        )

    # ── AJAX: student lookup by faculty_id ───────────────────────────────────

    @http.route('/training/ajax/student', type='http', auth='public', website=True, csrf=False)
    def ajax_get_student(self, university_id=None, **kw):
        result = {}
        if university_id:
            student = request.env['op.student'].sudo().search([
                ('faculty_id', '=', university_id.strip()),
            ], limit=1)
            if student:
                level_map = {
                    'one':   '1st',
                    'two':   '2nd',
                    'three': '3rd',
                    'four':  '4th',
                }
                level_name = level_map.get(student.level or '', '')
                level_rec = request.env['level.year'].sudo().search([
                    ('name', '=', level_name)
                ], limit=1)
                result = {
                    'found':          True,
                    'name':           student.name or '',
                    'national_id':    student.vat or '',
                    'phone':          student.mobile or '',
                    'university_id':  student.university.id if student.university else '',
                    'level_id':       str(level_rec.id) if level_rec else '',
                }
            else:
                result = {'found': False}
        return request.make_response(
            json.dumps(result),
            headers=[('Content-Type', 'application/json')],
        )

    # ── AJAX: weeks + live capacity for a program ─────────────────────────────

    @http.route('/training/ajax/weeks', type='http', auth='public', website=True, csrf=False)
    def ajax_get_weeks(self, program_id=None, **kw):
        result = []
        if program_id:
            try:
                pid = int(program_id)
            except (ValueError, TypeError):
                pid = 0
            if pid:
                weeks = request.env['training.weekly.schedule'].sudo().search([
                    ('training_id', '=', pid),
                ], order='week_number asc')
                for w in weeks:
                    result.append({
                        'id':     w.id,
                        'number': w.week_number,
                        'start':  str(w.week_start_date) if w.week_start_date else '',
                        'end':    str(w.week_end_date)   if w.week_end_date   else '',
                        'max':    w.max_students,
                        'taken':  w.registered_count,
                        'left':   w.remaining_spots,
                        'full':   w.is_full,
                        'pct':    int((w.registered_count / w.max_students) * 100) if w.max_students else 0,
                    })
        return request.make_response(
            json.dumps(result),
            headers=[('Content-Type', 'application/json')],
        )

    # ── Submit ────────────────────────────────────────────────────────────────

    @http.route('/training/register/submit', type='http', auth='public', website=True, methods=['POST'], csrf=False)
    def training_submit(self, **post):
        error         = {}
        error_message = []

        required_fields = [
            'student_name', 'student_name_en', 'university_name', 'university_group',
            'university_id', 'national_id', 'phone_whatsapp',
            'training_company_id', 'training_program_id', 'training_week_id',
        ]
        for field in required_fields:
            if not post.get(field, '').strip():
                error[field] = 'missing'

        # English name validation — only English letters and spaces, minimum 3 words
        if not error:
            name_en = post.get('student_name_en', '').strip()
            import re as _re
            if not _re.match(r'^[A-Za-z ]+$', name_en):
                error['student_name_en'] = 'invalid'
                error_message.append(_('Full Name (English) must contain English letters only.'))
            elif len(name_en.split()) < 3:
                error['student_name_en'] = 'invalid'
                error_message.append(_('Full Name (English) must contain at least 3 names.'))

        # Backend check — university ID must exist in op.student
        if not error:
            uid_check = post.get('university_id', '').strip()
            student_check = request.env['op.student'].sudo().search([
                ('faculty_id', '=', uid_check)
            ], limit=1)
            if not student_check:
                error['university_id'] = 'not_found'
                error_message.append(_('This University ID is not registered in our system. Registration is not allowed.'))

        if not error:
            if not re.match(r'^\d{14}$', post.get('national_id', '')):
                error['national_id'] = 'invalid'
                error_message.append(_('National ID must be exactly 14 digits.'))

        # Pre-check week capacity
        if not error:
            week_id = post.get('training_week_id', '')
            if week_id:
                try:
                    wid  = int(week_id)
                    week = request.env['training.weekly.schedule'].sudo().browse(wid)
                    if week.exists() and week.is_full:
                        error['training_week_id'] = 'full'
                        error_message.append(_(
                            'The selected training week is fully booked (%d/%d seats). '
                            'Please choose a different week.'
                        ) % (week.max_students, week.max_students))
                except (ValueError, TypeError):
                    pass

        if error and not error_message:
            error_message.append(_('Please fill in all required fields.'))

        if error:
            companies    = request.env['masrtech.register.partner'].sudo().search([('is_training', '=', True)])
            levels       = request.env['level.year'].sudo().search([])
            universities = request.env['masrtech.universities'].sudo().search([])
            return request.render('nexus_nms.training_portal_registration_form', {
                'error':         error,
                'error_message': error_message,
                'form_data':     post,
                'companies':     companies,
                'levels':        levels,
                'universities':  universities,
            })

        try:
            # Support both auto-filled and manual entry
            student_name = (post.get('student_name') or post.get('student_name_manual') or '').strip()
            student_name_en = post.get('student_name_en', '').strip()
            national_id   = post['national_id'].strip()
            phone         = (post.get('phone_whatsapp') or post.get('phone_whatsapp_manual') or '').strip()
            university_id = post['university_id'].strip()
            level_id_raw  = post.get('university_group') or post.get('university_group_manual') or ''
            level_id      = int(level_id_raw) if level_id_raw else 0
            univ_rec_id_raw = post.get('university_name') or post.get('university_name_manual') or ''
            company_id      = int(post['training_company_id'])
            program_id      = int(post['training_program_id'])
            week_id         = int(post['training_week_id'])

            env = request.env

            # ── Split name ──
            name_parts = student_name.split(' ', 1)
            first_name = name_parts[0]
            last_name  = name_parts[1] if len(name_parts) > 1 else ''

            # ── Resolve selected masrtech.universities record ──
            university_rec = env['masrtech.universities'].sudo().browse(
                int(univ_rec_id_raw) if str(univ_rec_id_raw).isdigit() else 0
            )
            if not university_rec.exists():
                university_rec = env['masrtech.universities'].sudo()

            # ── A company restricted to specific universities rejects others ──
            company = env['masrtech.register.partner'].sudo().browse(company_id)
            if company.exists() and company.university_ids and (
                not university_rec or university_rec.id not in company.university_ids.ids
            ):
                raise ValidationError(_('This training company is not available for your university.'))

            # ── Map level.year id → year_level selection on training.registration ──
            level_rec = env['level.year'].sudo().browse(level_id)
            level_name_map = {
                '1st':   'one',
                '2nd':   'two',
                '3rd':   'three',
                '4th':   'fourth',
                'first':  'one',
                'second': 'two',
                'third':  'three',
                'fourth': 'fourth',
            }
            year_level_val = level_name_map.get(
                level_rec.name.lower() if level_rec else '', 'one')

            # ── Find or create op.student by national ID ──
            existing_student = env['op.student'].sudo().search([
                ('vat', '=', national_id),
            ], limit=1)

            if existing_student:
                student = existing_student
            else:
                student_vals = {
                    'first_name': first_name,
                    'last_name':  last_name,
                    'name':       student_name,
                    'mobile':     phone,
                    'vat':        national_id,
                    'student_id': university_id,
                    'gender':     'm',
                }
                if university_rec:
                    student_vals['university'] = university_rec.id

                student = env['op.student'].sudo().create(student_vals)

            # ── Create training.registration (confirmed directly) ──
            env['training.registration'].sudo().create({
                'student_namee':       student.id,
                'vat':                 national_id,
                'phone':               phone,
                'student_id':          university_id,
                'weekly_schedule_id':  week_id,
                'training_course_id':  program_id,
                'partner_id':          company_id,
                'university_id':       university_rec.id if university_rec else False,
                'year_level':          year_level_val,
                'student_name_en':     student_name_en,
                'registration_status': 'draft',
            })

        except (ValidationError, ValueError, TypeError) as e:
            companies    = request.env['masrtech.register.partner'].sudo().search([('is_training', '=', True)])
            levels       = request.env['level.year'].sudo().search([])
            universities = request.env['masrtech.universities'].sudo().search([])
            error_message.append(str(e))
            return request.render('nexus_nms.training_portal_registration_form', {
                'error':         error,
                'error_message': error_message,
                'form_data':     post,
                'companies':     companies,
                'levels':        levels,
                'universities':  universities,
            })

        return request.render('nexus_nms.training_portal_registration_success', {
            'student_name': post['student_name'].strip(),
        })