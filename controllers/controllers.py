from odoo import http
from odoo.http import request
from odoo import _, api, models
import datetime
from datetime import datetime, timedelta
import json
import logging
import base64
import os
import requests
import traceback
_logger = logging.getLogger(__name__)


class nmsWebsite(http.Controller):
    @http.route('/', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def websiteHome(self, **kw):
        return http.request.render('nexus_nms.Home1', {})

    @http.route('/handsOn', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def handsOn(self, **kw):
        return http.request.render('nexus_nms.handsOnTrainCourse', {})

    @http.route('/doctorRegis', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def doctorRegis(self, **kw):
        # uid = request.session.authenticate('TMS', 'admin', 'REDACTED')
        faculty = request.env['masrtech.faculty'].sudo().search([])

        return http.request.render('nexus_nms.doctor_registration',
                                   {'faculty': faculty})

    @http.route('/blog', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def blog(self, **kw):
        return http.request.render('nexus_nms.blog', {})

    @http.route('/all_Courses', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def allCourses(self, **kw):
        return http.request.render('nexus_nms.all_Courses', {})

    @http.route('/confirm_apply_ar', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def confirm_apply_ar(self, **kw):
        return http.request.render('nexus_nms.confirmation_apply_arabic', {})

    @http.route('/confirm_contact_ar', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def confirm_contact_ar(self, **kw):
        return http.request.render('nexus_nms.contact_us_confirmation_arab', {})

    @http.route('/confirm_contact', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def confirm_contact(self, **kw):
        return http.request.render('nexus_nms.contact_us_confirmation_en', {})

    @http.route('/refund_request_confirm', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def refund_request_confirm_template(self, **kw):
        return http.request.render('nexus_nms.refund_request_confirm_template', {})

    @http.route('/refund_request', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def refund_request_template(self, **kw):
        return http.request.render('nexus_nms.refund_request_template', {})


    @http.route('/registration_for_training', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def registration_for_training(self, **kw):
        universities = request.env['masrtech.universities'].sudo().search([])
        faculty = request.env['masrtech.faculty'].sudo().search([])
        department = request.env['op.department'].sudo().search([])
        payment_ways = request.env['payment.way'].sudo().search([('active', '=', True)], order='sequence, id')

        course_code = kw.get('course_code', '')
        partner_id = kw.get('partner_id', '')
        training_id = kw.get('training_id', '')
        error_message = kw.get('error_message', '')

        selected_partner = False
        selected_training = False

        if partner_id:
            try:
                selected_partner = request.env['masrtech.register.partner'].sudo().browse(int(partner_id))
            except (ValueError, TypeError):
                selected_partner = False

        if training_id:
            try:
                selected_training = request.env['registrar.partner.training.table'].sudo().browse(int(training_id))
            except (ValueError, TypeError):
                selected_training = False

        return http.request.render('nexus_nms.registration_for_training', {
            'universities': universities,
            'faculty': faculty,
            'department': department,
            'payment_ways': payment_ways,
            'course_code': course_code,
            'partner_id': partner_id,
            'training_id': training_id,
            'selected_partner': selected_partner,
            'selected_training': selected_training,
            'error_message': error_message,
        })

    @http.route('/get_student_data', type='http', auth='public', methods=['POST'], csrf=False, website=True)
    def get_student_data(self, **kw):
        import json
        import logging
        _logger = logging.getLogger(__name__)

        student_id = kw.get('student_id', '').strip()

        if not student_id:
            return http.Response(
                json.dumps({'error': 'Student ID is required'}),
                content_type='application/json'
            )

        student = request.env['op.student'].sudo().search([('faculty_id', '=', student_id)], limit=1)

        if not student:
            return http.Response(
                json.dumps({'error': 'Student not found'}),
                content_type='application/json'
            )

        all_universities = request.env['masrtech.universities'].sudo().search([])
        all_faculties = request.env['masrtech.faculty'].sudo().search([])

        university_id = ''
        university_name = ''
        if student.university:
            university_id = student.university.id
            university_name = student.university.name

        faculty_id = ''
        faculty_name = ''
        if student.faculty:
            faculty_id = student.faculty.id
            faculty_name = student.faculty.name

        level = student.level or ''

        data = {
            'success': True,
            'data': {
                'name': student.name or '',
                'email': student.email or '',
                'phone': student.mobile or '',
                'university_id': university_id,
                'university_name': university_name,
                'faculty_id': faculty_id,
                'faculty_name': faculty_name,
                'level': level,
                'available_universities': [{'id': u.id, 'name': u.name} for u in all_universities],
                'available_faculties': [{'id': f.id, 'name': f.name} for f in all_faculties],
            }
        }

        return http.Response(
            json.dumps(data),
            content_type='application/json'
        )

    # @http.route('/get_student_data', type='http', auth='public', methods=['POST'], csrf=False, website=True)
    # def get_student_data(self, **kw):
    #     import json
    #     import logging
    #     _logger = logging.getLogger(__name__)
    #
    #     student_id = kw.get('student_id', '').strip()
    #     national_id = kw.get('national_id', '').strip()
    #
    #     _logger.info(f"=== STUDENT SEARCH DEBUG ===")
    #     _logger.info(f"Student ID: '{student_id}'")
    #     _logger.info(f"National ID: '{national_id}'")
    #
    #     # Check if at least one identifier is provided
    #     if not student_id and not national_id:
    #         return http.Response(
    #             json.dumps({'error': 'Student ID or National ID is required'}),
    #             content_type='application/json'
    #         )
    #
    #     # Search based on which identifier was provided
    #     student = None
    #     search_type = ''
    #
    #     if student_id:
    #         student = request.env['op.student'].sudo().search([('faculty_id', '=', student_id)], limit=1)
    #         search_type = 'student_id (faculty_id)'
    #         _logger.info(f"Searching by student_id: {student_id}")
    #     elif national_id:
    #         student = request.env['op.student'].sudo().search([('vat', '=', national_id)], limit=1)
    #         search_type = 'national_id (vat)'
    #         _logger.info(f"Searching by national_id: {national_id}")
    #
    #     if not student:
    #         error_msg = f'Student not found with {search_type}: {student_id or national_id}'
    #         _logger.warning(error_msg)
    #         return http.Response(
    #             json.dumps({'error': 'Student not found. Please enter your data manually.'}),
    #             content_type='application/json'
    #         )
    #
    #     _logger.info(f"Student found: {student.name} (ID: {student.id})")
    #
    #     # Get all available universities and faculties for debugging
    #     all_universities = request.env['masrtech.universities'].sudo().search([])
    #     _logger.info(f"Available universities in system:")
    #     for uni in all_universities:
    #         _logger.info(f"  - ID: {uni.id}, Name: {uni.name}")
    #
    #     all_faculties = request.env['masrtech.faculty'].sudo().search([])
    #     _logger.info(f"Available faculties in system:")
    #     for fac in all_faculties:
    #         _logger.info(f"  - ID: {fac.id}, Name: {fac.name}")
    #
    #     # Get student's university
    #     university_id = ''
    #     university_name = ''
    #     if student.university:
    #         university_id = student.university.id
    #         university_name = student.university.name
    #         _logger.info(f"Student's University: {university_name} (ID: {university_id})")
    #     else:
    #         _logger.warning("Student has no university assigned!")
    #
    #     # Get student's faculty
    #     faculty_id = ''
    #     faculty_name = ''
    #     if student.faculty:
    #         faculty_id = student.faculty.id
    #         faculty_name = student.faculty.name
    #         _logger.info(f"Student's Faculty: {faculty_name} (ID: {faculty_id})")
    #     else:
    #         _logger.warning("Student has no faculty assigned!")
    #
    #     # Get student's level
    #     level = student.level or ''
    #     _logger.info(f"Student's Level: '{level}'")
    #
    #     # Get student's GPA if available
    #     gpa = 0.0
    #     if hasattr(student, 'gpa') and student.gpa:
    #         gpa = student.gpa
    #         _logger.info(f"Student's GPA: {gpa}")
    #
    #     # Prepare response data
    #     data = {
    #         'success': True,
    #         'data': {
    #             'name': student.name or '',
    #             'email': student.email or '',
    #             'phone': student.mobile or '',
    #             'university_id': university_id,
    #             'university_name': university_name,
    #             'faculty_id': faculty_id,
    #             'faculty_name': faculty_name,
    #             'level': level,
    #             'gpa': gpa,
    #             'student_id': student.faculty_id or '',  # Return the student_id
    #             'national_id': student.vat or '',  # Return the national_id
    #             'available_universities': [{'id': u.id, 'name': u.name} for u in all_universities],
    #             'available_faculties': [{'id': f.id, 'name': f.name} for f in all_faculties],
    #             'debug_info': {
    #                 'student_record_id': student.id,
    #                 'search_type': search_type,
    #                 'has_university': bool(student.university),
    #                 'has_faculty': bool(student.faculty),
    #                 'raw_level': level,
    #                 'has_gpa': bool(gpa)
    #             }
    #         }
    #     }
    #
    #     _logger.info(f"Returning data: {json.dumps(data, indent=2, default=str)}")
    #
    #     return http.Response(
    #         json.dumps(data, default=str),
    #         content_type='application/json'
    #     )

    @http.route('/registration_for_training/submit', type='http', auth='public', methods=['POST', 'GET'], csrf=False,
                website=True)
    def submit_registration(self, **post):
        try:
            status = post.get('status')
            student = None

            if status == 'student' and post.get('student_id'):
                student = request.env['op.student'].sudo().search([
                    ('faculty_id', '=', post.get('student_id'))
                ], limit=1)
            elif status == 'graduated' and post.get('national_id'):
                student = request.env['op.student'].sudo().search([
                    ('vat', '=', post.get('national_id'))
                ], limit=1)

            id_attachment = False
            if 'id_number_attachment' in request.httprequest.files:
                uploaded_file = request.httprequest.files['id_number_attachment']
                if uploaded_file and uploaded_file.filename:
                    import base64
                    file_content = uploaded_file.read()
                    if file_content:
                        id_attachment = base64.b64encode(file_content)

            university_id = int(post.get('university')) if post.get('university') else False
            faculty_id = int(post.get('faculty')) if post.get('faculty') else False
            if not student:
                student_vals = {
                    'name': post.get('name'),
                    'faculty_id': post.get('student_id', ''),
                    'vat': post.get('national_id', ''),
                    'email': post.get('email'),
                    'mobile': post.get('phone'),
                    'university': int(post.get('university')) if post.get('university') else False,
                    'faculty': int(post.get('faculty')) if post.get('faculty') else False,
                }
                student = request.env['op.student'].sudo().create(student_vals)

            if id_attachment:
                student.sudo().write({'id_attachment': id_attachment})

            name_stt = student.name
            name_st = student
            phone = post.get('phone')
            email = student.email
            create_phone = post.get('phone')
            partner_id = post.get('partner_id')
            is_course = False

            if partner_id:
                partner = request.env['masrtech.register.partner'].sudo().browse(int(partner_id))
                if partner.exists():
                    is_course = partner.is_course

            payment_method = post.get('payment_way')
            if payment_method:
                try:
                    payment_method = int(payment_method)
                except (ValueError, TypeError):
                    pass

            registration_vals = {
                'student_namee': name_st.id,
                'email': email,
                'is_course': is_course,
                'phone': post.get('phone'),
                'university_id': university_id,
                'faculty_id': faculty_id,
                'student_id': post.get('student_id', ''),
                'vat': post.get('national_id', ''),
                'year_level': post.get('levels'),
                'payment_way': payment_method,
                'registration_status': 'draft',
            }

            if post.get('partner_id'):
                registration_vals['partner_id'] = int(post.get('partner_id'))

            if post.get('training_id'):
                registration_vals['training_course_id'] = int(post.get('training_id'))

            registration = request.env['training.registration'].sudo().create(registration_vals)

            if student and create_phone:
                student.sudo().write({'mobile': create_phone})

            return http.request.render('nexus_nms.training_registration_confirm', {})

        except Exception as e:
            import traceback
            traceback.print_exc()
            error_url = f'/registration_for_training?partner_id={post.get("partner_id")}&training_id={post.get("training_id")}&course_code={post.get("course_code", "")}&error_message=Registration failed'
            return request.redirect(error_url)
    @http.route('/registration_for_training_success', type='http', auth='public', methods=['GET'], csrf=False,
                website=True)
    def registration_for_training_confirm(self, **kw):
        return http.request.render('nexus_nms.payment_success', {})

    @http.route('/course-details', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def details_program(self, **kw):
        return http.request.render('nexus_nms.programDetails', {})

    @http.route('/payment_details', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def payment_method(self, **kw):
        return http.request.render('nexus_nms.payment_details', {})

    @http.route('/training_page', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def training_page(self, **kw):
        partners = request.env['masrtech.register.partner'].sudo().search([
            ('is_course', '=', False)
        ], order='create_date desc')
        type_field = request.env['masrtech.sub'].sudo().search([])

        current_user = request.env.user
        is_student = False

        training_data = []
        for partner in partners:
            if partner.training_table:
                for training in partner.training_table:
                    total_capacity = training.capacity or 0
                    available_weeks_info = []
                    students_capacity = 0
                    remaining_spots = 0
                    max_students = 0
                    total_registered = 0

                    if training.is_weekly_breakdown and training.weekly_schedule_ids:
                        sorted_weeks = training.weekly_schedule_ids.sorted('week_start_date')
                        first_available = next((w for w in sorted_weeks if w.remaining_spots > 0), None)
                        week = first_available or (sorted_weeks[0] if sorted_weeks else None)

                        if week:
                            available_weeks_info.append({
                                'week_number': week.week_number,
                                'start_date': week.week_start_date.strftime('%Y-%m-%d') if week.week_start_date else '',
                                'end_date': week.week_end_date.strftime('%Y-%m-%d') if week.week_end_date else '',
                                'remaining_spots': week.remaining_spots,
                                'max_students': week.max_students,
                                'registered_count': week.registered_count,
                                'is_active': week.is_active
                            })
                            remaining_spots = week.remaining_spots or 0
                            max_students = week.max_students or 0
                            total_registered = week.registered_count or 0
                            students_capacity = max_students
                    else:
                        total_registered = training.registered_count or 0
                        remaining_spots = training.remaining_capacity or 0
                        students_capacity = total_capacity

                    training_name = training.training.training_name if training.training else "General Training"

                    if remaining_spots <= 0:
                        availability_status = "full"
                    elif remaining_spots <= 5:
                        availability_status = "limited"
                    else:
                        availability_status = "available"

                    price_display = f"{training.cost} EGP" if training.cost else ""

                    levels = []
                    training_level_ids = []
                    if training.level_ids:
                        levels = [{'id': level.id, 'name': level.name} for level in training.level_ids]
                        training_level_ids = [level.id for level in training.level_ids]

                    type_field = None
                    if hasattr(partner, 'type_sub') and partner.type_sub:
                        type_field = partner.type_sub.name
                    else:
                        type_field = "General"

                    training_data.append({
                        'partner': partner,
                        'training': training,
                        'company_name': partner.name,
                        'company_details': partner.company_details_name or f'{partner.name} combines advanced manufacturing processes with strict regulatory compliance to deliver safe and effective products globally.',
                        'image': partner.image,
                        'training_title': partner.name,
                        'duration': training.duration,
                        'code': training.code,
                        'students_capacity': training.capacity,
                        'total_capacity': total_capacity,
                        'registered_count': total_registered,
                        'remaining_spots': remaining_spots,
                        'availability_status': availability_status,
                        'is_full': remaining_spots <= 0,
                        'price_display': price_display,
                        'training_name': training_name,
                        'levels': levels,
                        'training_level_names': [level['name'] for level in levels],
                        'total_no': partner.representatives,
                        'is_weekly_breakdown': training.is_weekly_breakdown,
                        'total_weeks': training.total_weeks if training.is_weekly_breakdown else 0,
                        'students_per_week': max_students,
                        'available_weeks_info': available_weeks_info,
                        'available_weeks_count': len(available_weeks_info),
                        'type': type_field,  # Add the type field for filtering

                    })

        return http.request.render('nexus_nms.training_page', {
            'training_data': training_data,
            'partners': partners,
            'current_user': current_user,
            'is_student': is_student,
            'json': json,
        })

    @http.route('/course_page', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def course_page(self, **kw):
        partners = request.env['masrtech.register.partner'].sudo().search([
            ('is_course', '=', True)
        ])
        type_field = request.env['masrtech.sub'].sudo().search([])

        current_user = request.env.user
        is_student = False

        training_data = []
        for partner in partners:
            if partner.training_table:
                for training in partner.training_table:
                    total_capacity = training.capacity or 0
                    available_weeks_info = []
                    students_capacity = 0
                    remaining_spots = 0
                    max_students = 0
                    total_registered = 0

                    if training.is_weekly_breakdown and training.weekly_schedule_ids:
                        sorted_weeks = training.weekly_schedule_ids.sorted('week_start_date')
                        first_available = next((w for w in sorted_weeks if w.remaining_spots > 0), None)
                        week = first_available or (sorted_weeks[0] if sorted_weeks else None)

                        if week:
                            available_weeks_info.append({
                                'week_number': week.week_number,
                                'start_date': week.week_start_date.strftime('%Y-%m-%d') if week.week_start_date else '',
                                'end_date': week.week_end_date.strftime('%Y-%m-%d') if week.week_end_date else '',
                                'remaining_spots': week.remaining_spots,
                                'max_students': week.max_students,
                                'registered_count': week.registered_count,
                                'is_active': week.is_active
                            })
                            remaining_spots = week.remaining_spots or 0
                            max_students = week.max_students or 0
                            total_registered = week.registered_count or 0
                            students_capacity = max_students
                    else:
                        total_registered = training.registered_count or 0
                        remaining_spots = training.remaining_capacity or 0
                        students_capacity = total_capacity

                    training_name = training.training.training_name if training.training else "General Training"

                    if remaining_spots <= 0:
                        availability_status = "full"
                    elif remaining_spots <= 5:
                        availability_status = "limited"
                    else:
                        availability_status = "available"

                    price_display = f"{training.cost} EGP" if training.cost else ""

                    levels = []
                    training_level_ids = []
                    if training.level_ids:
                        levels = [{'id': level.id, 'name': level.name} for level in training.level_ids]
                        training_level_ids = [level.id for level in training.level_ids]

                    type_field = None
                    if hasattr(partner, 'type_sub') and partner.type_sub:
                        type_field = partner.type_sub.name
                    else:
                        type_field = "General"

                    training_data.append({
                        'partner': partner,
                        'training': training,
                        'company_name': partner.name,
                        'company_details': partner.company_details_name or f'{partner.name} combines advanced manufacturing processes with strict regulatory compliance to deliver safe and effective products globally.',
                        'image': partner.image,
                        'training_title': partner.name,
                        'duration': training.duration,
                        'code': training.code,
                        'students_capacity': training.capacity,
                        'total_capacity': total_capacity,
                        'registered_count': total_registered,
                        'remaining_spots': remaining_spots,
                        'availability_status': availability_status,
                        'is_full': remaining_spots <= 0,
                        'price_display': price_display,
                        'training_name': training_name,
                        'levels': levels,
                        'training_level_names': [level['name'] for level in levels],
                        'total_no': partner.representatives,
                        'is_weekly_breakdown': training.is_weekly_breakdown,
                        'total_weeks': training.total_weeks if training.is_weekly_breakdown else 0,
                        'students_per_week': max_students,
                        'available_weeks_info': available_weeks_info,
                        'available_weeks_count': len(available_weeks_info),
                        'type': type_field,

                    })

        return http.request.render('nexus_nms.course_page', {
            'training_data': training_data,
            'partners': partners,
            'current_user': current_user,
            'is_student': is_student,
            'json': json,
        })

    @http.route('/template/<temp_id>', type='http', auth='public', website=True)
    def tiktok_lead_form(self, temp_id, **kw):
        template = request.env['training.weekly.schedule'].sudo().search([('template_encrypted_key', '=', temp_id)])

        if not template:
            return request.render('nexus_nms.error_template', {'error': 'Template not found'})

        student_id = kw.get('student_id') or request.httprequest.args.get('student_id')
        print('student_id', student_id)
        if student_id:
            channel = template.discussion_channel_id
            print('channel', channel)
            if channel:
                student_found = channel.student_idss.filtered(lambda s: s.faculty_id == student_id)
                print('student_found', student_found)
                if student_found:
                    invitation_url = f'https://borg-arab.com{template.invitation_url}'
                    return request.redirect(invitation_url)
                else:
                    return request.render('nexus_nms.student_not_allowed', {
                        'student_id': student_id,
                        'channel_name': channel.name
                    })
            else:
                return request.render('nexus_nms.error_template', {'error': 'No discussion channel found'})

        return request.render(template.template_xml_id, {
            'channel_id': template.discussion_channel_id.id if template.discussion_channel_id else ''
        })

    @http.route('/discuss/channel', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def invitation_link(self, **kw):
        return http.request.render('nexus_nms.join_meeting_template', {})

    # @http.route('/training_page', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    # def training_page(self, **kw):
    #     partners = request.env['masrtech.register.partner'].sudo().search([])
    #
    #     training_data = []
    #     for partner in partners:
    #         if partner.training_table:
    #             for training in partner.training_table:
    #                 total_registered = training.registered_count or 0
    #                 remaining_spots = training.remaining_capacity or 0
    #                 training_name = training.training_title
    #
    #                 total_capacity = sum(t.capacity or 0 for t in partner.training_table)
    #
    #                 if remaining_spots <= 0:
    #                     availability_status = "full"
    #                 elif remaining_spots <= 5:
    #                     availability_status = "limited"
    #                 else:
    #                     availability_status = "available"
    #
    #                 price_display = ""
    #                 if training.cost:
    #                     price_display = f"{training.cost} EGP"
    #
    #                 levels = []
    #                 if training.level_ids:
    #                     levels = [{'id': level.id, 'name': level.name} for level in training.level_ids]
    #
    #                 training_data.append({
    #                     'partner': partner,
    #                     'training': training,
    #                     'company_name': partner.name,
    #                     'company_details': partner.company_details_name or f'{partner.name} combines advanced manufacturing processes with strict regulatory compliance to deliver safe and effective products globally.',
    #                     'image': partner.image,
    #                     'training_title': partner.name,
    #                     'duration': training.duration,
    #                     'code': training.code,
    #                     'students_capacity': training.capacity,
    #                     'registered_count': total_registered,
    #                     'remaining_spots': remaining_spots,
    #                     'availability_status': availability_status,
    #                     'is_full': remaining_spots <= 0,
    #                     'price_display': price_display,
    #                     'training_name': training_name,
    #                     'levels': levels,
    #                 })
    #
    #     return http.request.render('nexus_nms.training_page', {
    #         'training_data': training_data,
    #         'partners': partners,
    #     })

    @http.route('/submit_application_ar', type='http', auth='public', methods=['GET', 'POST'], csrf=False, website=True)
    def submit_application_ar(self, **kw):
        course_id = kw.get('course_id')
        course = None

        if course_id:
            course = request.env['op.course'].sudo().browse(int(course_id))

        application_data = {
            'full_name': kw.get('full_name'),
            'national_id': kw.get('national_id'),
            'email_address': kw.get('email'),
            'phone_number': kw.get('mobile'),
            'work_phone': kw.get('work_phone'),
            'home_phone': kw.get('home_phone'),
            'educational_status': kw.get('educational_status'),
            'organization': kw.get('organization'),
            'position': kw.get('position'),
            'experience_years': int(kw.get('experience', 0)) if kw.get('experience') else 0,
            'why_interested': kw.get('motivation'),
            'special_requirements': kw.get('requirements'),
        }

        if course:
            application_data.update({
                'course_id': course.id,
            })

        application = request.env['program.reg'].sudo().create(application_data)
        attachment_ids = []

        if request.httprequest.files:
            files = request.httprequest.files.getlist('fileUpload')
            _logger.info(f"Found {len(files)} files")

            for file in files:
                if file and file.filename:
                    file_content = file.read()
                    _logger.info(f"Processing file: {file.filename}")

                    attachment = request.env['ir.attachment'].sudo().create({
                        'name': file.filename,
                        'datas': base64.b64encode(file_content),
                        'res_model': 'program.reg',
                        'res_id': application.id,
                        'mimetype': file.mimetype or 'application/octet-stream',
                        'public': False,
                    })
                    attachment_ids.append(attachment.id)
        else:
            _logger.warning("No files found in the request")

        if attachment_ids:
            _logger.info(f"Linking {len(attachment_ids)} attachments to student")
            application.sudo().write({
                'document_ids': [(6, 0, attachment_ids)]
            })

        return http.request.render('nexus_nms.payment_details', {
            'application': application,
            'course': course,
            'course_id': course_id
        })

    @http.route('/submit_application', type='http', auth='public', methods=['GET', 'POST'], csrf=False, website=True)
    def submit_application(self, **kw):
        course_id = kw.get('course_id')
        course = None
        if course_id:
            course = request.env['op.course'].sudo().browse(int(course_id))

        application_data = {
            'full_name': kw.get('full_name'),
            'national_id': kw.get('national_id'),
            'email_address': kw.get('email'),
            'phone_number': kw.get('mobile'),
            'work_phone': kw.get('work_phone'),
            'home_phone': kw.get('home_phone'),
            'educational_status': kw.get('educational_status'),
            'organization': kw.get('organization'),
            'position': kw.get('position'),
            'experience_years': int(kw.get('experience', 0)) if kw.get('experience') else 0,
            'why_interested': kw.get('motivation'),
            'special_requirements': kw.get('requirements'),
        }

        if course:
            application_data['course_id'] = course.id

        application = request.env['program.reg'].sudo().create(application_data)
        attachment_ids = []

        if request.httprequest.files:
            files = request.httprequest.files.getlist('fileUpload')
            _logger.info(f"Found {len(files)} files")

            for file in files:
                if file and file.filename:
                    file_content = file.read()
                    _logger.info(f"Processing file: {file.filename}")

                    attachment = request.env['ir.attachment'].sudo().create({
                        'name': file.filename,
                        'datas': base64.b64encode(file_content),
                        'res_model': 'program.reg',
                        'res_id': application.id,
                        'mimetype': file.mimetype or 'application/octet-stream',
                        'public': False,
                    })
                    attachment_ids.append(attachment.id)
        else:
            _logger.warning("No files found in the request")

        if attachment_ids:
            _logger.info(f"Linking {len(attachment_ids)} attachments to student")
            application.sudo().write({
                'document_ids': [(6, 0, attachment_ids)]
            })

        return request.render('nexus_nms.payment_details', {
            'application': application,
            'course': course,
        })

    @http.route('/confirmation_apply', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def confirmation_apply(self, **kw):
        return http.request.render('nexus_nms.confirmation_apply', {})

    @http.route('/healthtech-training', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def apply(self, course_id=None, **kw):
        try:
            course = None
            if course_id:
                course = request.env['op.course'].sudo().browse(int(course_id))
                if not course.exists():
                    return request.redirect('/all_programs')

            return request.render('nexus_nms.apply_template', {
                'course': course,
            })

        except Exception as e:
            _logger.error(f"Error loading application form: {str(e)}")
            return request.redirect('/all_programs')

    @http.route('/healthCare_analysis', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def healthCare_analysis(self, **kw):
        return http.request.render('nexus_nms.healthCare_analysis', {})

    @http.route('/hospital_departments', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def healthCare_departments(self, **kw):
        return http.request.render('nexus_nms.hospital_departments_template', {})

    @http.route('/it_system', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def it_system(self, **kw):
        return http.request.render('nexus_nms.it_system', {})

    @http.route('/contact_us', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def contact_us(self, **kw):
        return http.request.render('nexus_nms.contact_us_template', {})

    @http.route('/contact_us_ar', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def contact_us_ar(self, **kw):
        return http.request.render('nexus_nms.contact_us_template_ar', {})

    @http.route('/apply_template_ar', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def apply_template_ar(self, course_id=None, **kw):
        course = None
        if course_id:
            course = request.env['op.course'].sudo().browse(int(course_id))
            if not course.exists():
                return request.redirect('/all_programs')

        return http.request.render('nexus_nms.apply_template_ar', {
            'course': course,
        })

    @http.route('/courseDetails', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def courseDetails(self, **kw):
        return http.request.render('nexus_nms.courseDetails', {})

    @http.route('/studentRegistration', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def studentRegis(self, **kw):
        # uid = request.session.authenticate('TMS', 'admin', 'REDACTED')
        universities = request.env['masrtech.universities'].sudo().search([])
        faculty = request.env['masrtech.faculty'].sudo().search([])
        department = request.env['op.department'].sudo().search([])

        error_message = kw.get('error_message', '')

        return http.request.render('nexus_nms.student_registration', {
            'universities': universities,
            'faculty': faculty,
            'department': department,
            'error_message': error_message,
        })

    @http.route('/studentRegisConfirm', type='http', auth='public', methods=['GET', 'POST'], csrf=False, website=True)
    def studentRegisConfirm(self, **kw):
        try:
            user = request.env.user
            faculty_id = kw.get('faculty_id')

            existing_student = request.env['op.student'].sudo().search([
                ('faculty_id', '=', faculty_id)
            ], limit=1)

            if existing_student:
                error_message = f"طالب برقم جامعي {faculty_id} موجود بالفعل في النظام"
                return request.redirect(f'/studentRegistration?error_message={error_message}')

            existing_user = request.env['res.users'].sudo().search([
                ('login', '=', kw.get('username'))
            ], limit=1)

            if existing_user:
                error_message = f"اسم المستخدم {kw.get('username')} موجود بالفعل"
                return request.redirect(f'/studentRegistration?error_message={error_message}')

            portal_group = request.env.ref('base.group_portal')

            portal_user = request.env['res.users'].sudo().create({
                'name': kw.get('portal_name'),
                'login': kw.get('username'),
                'email': kw.get('email'),
                'password': kw.get('password'),
                'active': True,
                'share': True,
                'groups_id': [(6, 0, [portal_group.id])],
            })

            university = request.env['masrtech.universities'].sudo().search([], limit=1)

            create_op_student = request.env['op.student'].sudo().create({
                'name': kw.get('name'),
                'student_id': kw.get('student_id'),
                'faculty_id': faculty_id,
                'mobile': kw.get('phone'),
                'email': kw.get('email'),
                'university': university.id if university else False,
                'faculty': kw.get('faculty'),
                'department': kw.get('department'),
                'level': kw.get('levels'),
                'soft_skills': kw.get('soft_skill'),
                'trainings': kw.get('training'),
                'academic_track': kw.get('academic_track'),
                'user_id': portal_user.id,

            })

            print('kw.get("fileUpload")', kw.get('fileUpload'))
            attachment_ids = []

            if request.httprequest.files:
                files = request.httprequest.files.getlist('fileUpload')
                _logger.info(f"Found {len(files)} files")

                for file in files:
                    if file and file.filename:
                        file_content = file.read()
                        _logger.info(f"Processing file: {file.filename}")

                        attachment = request.env['ir.attachment'].sudo().create({
                            'name': file.filename,
                            'datas': base64.b64encode(file_content),
                            'res_model': 'op.student',
                            'res_id': create_op_student.id,
                            'mimetype': file.mimetype or 'application/octet-stream',
                            'public': False,
                        })
                        attachment_ids.append(attachment.id)
            else:
                _logger.warning("No files found in the request")

            if attachment_ids:
                _logger.info(f"Linking {len(attachment_ids)} attachments to student")
                create_op_student.sudo().write({
                    'document_ids': [(6, 0, attachment_ids)]
                })

            values = {
                'username': kw.get('username'),
            }
            return http.request.render('nexus_nms.student_registration_confirm', values)

        except Exception as e:
            _logger.error(f"Error during student registration: {str(e)}")
            error_message = "حدث خطأ أثناء التسجيل. يرجى المحاولة مرة أخرى"
            return request.redirect(f'/studentRegistration?error_message={error_message}')

    @http.route('/doctorRegisConfirm', type='http', auth='public', methods=['GET', 'POST'], csrf=False, website=True)
    def doctorRegisConfirm(self, **kw):

        first_name = kw.get('first_name')
        middle_name = kw.get('middle_name')
        last_name = kw.get('last_name')
        name = f"{first_name} {middle_name} {last_name}".replace('  ', ' ').strip()

        date_of_birth = kw.get('date_of_birth')
        formatted_date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d') if date_of_birth else False

        title = kw.get('title')
        username = kw.get('username')
        password = kw.get('password')

        common_data = {
            'name': name,
            'first_name': first_name,
            'middle_name': middle_name,
            'last_name': last_name,
            'birth_date': formatted_date_of_birth,
            'gender': kw.get('gender'),
            'phone': kw.get('phone'),
            'email': kw.get('email'),
            'title_dr': title,
            'university': kw.get('university'),
            'faculty': kw.get('faculty'),
            'login_username': username,
            'login_password': password,
        }

        created_record = None
        record_type = None

        if title == 'doctor':
            created_record = request.env['op.faculty'].sudo().create(common_data)
            attachment_ids = []

            if request.httprequest.files:
                files = request.httprequest.files.getlist('fileUpload')
                _logger.info(f"Found {len(files)} files")

                for file in files:
                    if file and file.filename:
                        file_content = file.read()
                        _logger.info(f"Processing file: {file.filename}")

                        attachment = request.env['ir.attachment'].sudo().create({
                            'name': file.filename,
                            'datas': base64.b64encode(file_content),
                            'res_model': 'op.faculty',
                            'res_id': created_record.id,
                            'mimetype': file.mimetype or 'application/octet-stream',
                            'public': False,
                        })
                        attachment_ids.append(attachment.id)
            else:
                _logger.warning("No files found in the request")

            if attachment_ids:
                _logger.info(f"Linking {len(attachment_ids)} attachments to student")
                created_record.sudo().write({
                    'document_ids': [(6, 0, attachment_ids)]
                })
            record_type = 'doctor'

        elif title == 'assistant':
            created_record = request.env['assistant.model'].sudo().create(common_data)
            attachment_ids = []

            if request.httprequest.files:
                files = request.httprequest.files.getlist('fileUpload')
                _logger.info(f"Found {len(files)} files")

                for file in files:
                    if file and file.filename:
                        file_content = file.read()
                        _logger.info(f"Processing file: {file.filename}")

                        attachment = request.env['ir.attachment'].sudo().create({
                            'name': file.filename,
                            'datas': base64.b64encode(file_content),
                            'res_model': 'assistant.model',
                            'res_id': created_record.id,
                            'mimetype': file.mimetype or 'application/octet-stream',
                            'public': False,
                        })
                        attachment_ids.append(attachment.id)
            else:
                _logger.warning("No files found in the request")

            if attachment_ids:
                _logger.info(f"Linking {len(attachment_ids)} attachments to student")
                created_record.sudo().write({
                    'document_ids': [(6, 0, attachment_ids)]
                })

            record_type = 'assistant'
        else:
            created_record = request.env['op.faculty'].sudo().create(common_data)

        values = {
            'username': username,
            'record_type': record_type,
            'created_record_id': created_record.id if created_record else False,
            'name': name,
        }

        return http.request.render('nexus_nms.doctor_registration_confirm', values)

    @http.route('/partnerRegis', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def partnerRegis(self, **kw):
        department = request.env['masrtech.sub'].sudo().search([])

        return http.request.render('nexus_nms.key_partner_registration', {'department': department, })

    @http.route('/partnerRegisConfirm', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def partnerRegisConfirm(self, **kw):
        # uid = request.session.authenticate('TMS', 'admin', 'REDACTED')
        user = request.env.user

        name = kw.get('company_name')
        company_address = kw.get('company_address')
        responsible_person = kw.get('responsible_person')
        phone_number = kw.get('phone_number')
        email = kw.get('email')
        company_details_name = kw.get('company_details_name')

        key_partner = request.env['masrtech.register.partner'].sudo().create({
            'name': name,
            'company_address': company_address,
            'responsible_person': responsible_person,
            'phone_number': phone_number,
            'email': email,
            'type_sub': kw.get('department'),
            'company_details_name': company_details_name,
        })

        return http.request.render('nexus_nms.key_partner_registration_confirm', {})

    @http.route('/consultation/form', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def consultation_form(self, **kw):
        sectors = request.env['masrtech.sub'].sudo().search([])
        return http.request.render('nexus_nms.consultation_template', {'sector': sectors})

    @http.route('/consultation/form/confirm', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def consultation_form_confirm(self, **kw):
        user = request.env.user
        create_project_task = request.env['project.task'].sudo().create({
            'name': kw.get('company'),
            'project_id': 1,
            'company_name': kw.get('company'),
            'email': kw.get('last_name'),
            'sector': kw.get('sector'),
            'project_requirements': kw.get('message'),

        })
        return http.request.render('nexus_nms.consultation_template_confirm', {})

    @http.route('/payment', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def payment_page(self, **kw):
        course_name = kw.get('course_name', 'Course')
        course_price = kw.get('course_price', '0')
        return http.request.render('nexus_nms.payment_page', {
            'course_name': course_name,
            'course_price': course_price,
        })

    @http.route('/programCategory', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def program_category(self, **kw):
        departments = request.env['op.department'].sudo().search([])
        return http.request.render('nexus_nms.all_categories', {
            'departments': departments
        })

    @http.route('/payment/process', type='http', auth='public', methods=['POST', 'GET'], csrf=False, website=True)
    def process_payment(self, **kw):

        return http.request.render('nexus_nms.payment_success', {

        })

    @http.route('/all_programs', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def all_programs(self, department=None, subdepartment=None, **kw):
        try:
            if subdepartment:
                try:
                    subdept_id = int(subdepartment)
                    subdept = request.env['sub.department.model'].sudo().browse(subdept_id)
                    department_obj = None

                    if department:
                        department_id = int(department)
                        department_obj = request.env['op.department'].sudo().browse(department_id)
                    else:
                        department_obj = subdept.department

                    courses = subdept.course_ids

                    universities = {}
                    for course in courses:
                        if course.university:
                            uni_name = course.university.name
                            if uni_name not in universities:
                                universities[uni_name] = {}

                            faculty_name = course.faculty.name if course.faculty else 'General'
                            if faculty_name not in universities[uni_name]:
                                universities[uni_name][faculty_name] = []

                            universities[uni_name][faculty_name].append(course)

                    departments = request.env['op.department'].sudo().search([])

                    return request.render('nexus_nms.all_programs', {
                        'courses': courses,
                        'universities': universities,
                        'course_count': len(courses),
                        'selected_department_id': department,
                        'selected_subdepartment_id': subdepartment,
                        'departments': departments,
                        'department_obj': department_obj,
                        'subdepartment': subdept,
                        'view_mode': 'subdepartment_courses'
                    })

                except Exception as e:
                    _logger.error(f"Error loading subdepartment courses: {str(e)}")
                    return request.redirect('/programCategory')

        except Exception as e:
            _logger.error(f"Error loading courses: {str(e)}")
            return request.render('nexus_nms.all_programs', {
                'courses': [],
                'universities': {},
                'course_count': 0,
                'error': str(e),
                'departments': request.env['op.department'].sudo().search([]),
                'view_mode': 'error'
            })

    @http.route('/program_details', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def program_details(self, course_id=None, **kw):
        try:
            if not course_id:
                return request.redirect('/all_programs')

            course = request.env['op.course'].sudo().browse(int(course_id))

            if not course.exists():
                return request.redirect('/all_programs')

            subjects = course.subject_ids

            _logger.info(f"Course: {course.name}, Found {len(subjects)} subjects")

            return request.render('nexus_nms.program_details', {
                'course': course,
                'subjects': subjects,
                'university': getattr(course, 'university', None),
                'faculty': getattr(course, 'faculty', None),
                'department': getattr(course, 'department_id', None),
                'duration_weeks': getattr(course, 'duration_weeks', 0),
                'days_per_week': getattr(course, 'days_per_week', 0),
                'target_audience': getattr(course, 'target_audience', ''),
            })

        except Exception as e:
            _logger.error(f"Error loading program details: {str(e)}")
            return request.redirect('/all_programs')

    # @http.route('/training_pagee', type='http', auth='public', website=True)
    # def simple_training_search(self, student_id=None, **kwargs):
    #     student_data = None
    #     training_data = []
    #
    #     if student_id:
    #         student_id = str(student_id).strip()
    #         student_record = request.env['op.student'].sudo().search([('faculty_id', '=', student_id)], limit=1)
    #
    #         if student_record:
    #             if student_record.training_course_idd:
    #                 student_training_course = student_record.training_course_idd.training_name
    #                 print(f'Training course ID: {student_training_course}')
    #
    #                 gender = None
    #                 if student_record.gender == 'm':
    #                     gender = 'Male'
    #                 elif student_record.gender == 'f':
    #                     gender = 'Female'
    #
    #                 student_level_raw = student_record.level
    #                 level = None
    #                 if student_record.level == 'one':
    #                     level = 'L 1st'
    #                 elif student_record.level == 'two':
    #                     level = 'L 2nd'
    #                 elif student_record.level == 'three':
    #                     level = 'L 3rd'
    #                 elif student_record.level == 'four':
    #                     level = 'L 4th'
    #
    #                 student_data = {
    #                     'name': student_record.name or 'Unknown Student',
    #                     'student_id': student_record.student_id or student_id,
    #                     'faculty_name': student_record.faculty.name if student_record.faculty else 'No Faculty',
    #                     'level': level,
    #                     'level_raw': student_level_raw,
    #                     'type': gender,
    #                     'university_name': student_record.university.name if student_record.university else 'No University',
    #                     'training_course_idd': student_training_course,
    #                 }
    #
    #                 confirmed_registration = request.env['training.registration'].sudo().search([
    #                     ('student_namee', '=', student_record.id),
    #                     ('registration_status', '=', 'confirmed')
    #                 ], limit=1)
    #
    #                 if confirmed_registration:
    #                     print(
    #                         f"Student has confirmed registration for training: {confirmed_registration.training_course_id.id}")
    #
    #                     partners = request.env['masrtech.register.partner'].sudo().search([])
    #
    #                     for partner in partners:
    #                         if partner.training_table:
    #                             for training in partner.training_table:
    #                                 if training.id == confirmed_registration.training_course_id.id:
    #                                     total_registered = training.registered_count or 0
    #                                     remaining_spots = training.remaining_capacity or 0
    #                                     total_capacity = training.capacity or 0
    #
    #                                     training_name = 'No Training Name'
    #                                     if training.training and hasattr(training.training,
    #                                                                      'training_name') and training.training.training_name:
    #                                         training_name = training.training.training_name
    #                                     else:
    #                                         training_name = 'Unnamed Training'
    #
    #                                     if remaining_spots <= 0:
    #                                         availability_status = "full"
    #                                     elif remaining_spots <= 5:
    #                                         availability_status = "limited"
    #                                     else:
    #                                         availability_status = "available"
    #
    #                                     price_display = f"{training.cost} EGP" if training.cost else ""
    #
    #                                     levels = []
    #                                     if training.level_ids:
    #                                         levels = [{'id': level_record.id, 'name': level_record.name} for
    #                                                   level_record in training.level_ids]
    #
    #                                     training_info = {
    #                                         'partner': partner,
    #                                         'training': training,
    #                                         'company_name': partner.name or 'Unnamed Company',
    #                                         'company_details': partner.company_details_name or f'{partner.name} provides comprehensive training programs.',
    #                                         'image': partner.image,
    #                                         'training_title': partner.name or training_name,
    #                                         'duration': training.duration or 'Not specified',
    #                                         'code': training.code or 'No Code',
    #                                         'students_capacity': total_capacity,
    #                                         'registered_count': total_registered,
    #                                         'remaining_spots': remaining_spots,
    #                                         'availability_status': availability_status,
    #                                         'is_full': remaining_spots <= 0,
    #                                         'price_display': price_display,
    #                                         'training_name': training_name,
    #                                         'levels': levels,
    #                                         'total_no': partner.representatives or total_capacity or 0,
    #                                         'is_registered': True,
    #                                         'registration_status': 'confirmed'
    #                                     }
    #                                     training_data.append(training_info)
    #                                     break
    #                 else:
    #                     print("Student has no confirmed registration, showing all available trainings")
    #
    #                     partners = request.env['masrtech.register.partner'].sudo().search([])
    #
    #                     for partner in partners:
    #                         if partner.training_table:
    #                             for training in partner.training_table:
    #                                 total_capacity = training.capacity or 0
    #                                 available_weeks_info = []
    #                                 students_capacity = 0
    #                                 remaining_spots = 0
    #                                 max_students = 0
    #                                 total_registered = 0
    #                                 training_matches = False
    #                                 level_matches = False
    #
    #                                 if training.training and training.training.training_name == student_training_course:
    #                                     training_matches = True
    #
    #                                 if training.level_ids:
    #                                     for training_level in training.level_ids:
    #                                         if training_level.name == student_level_raw:
    #                                             level_matches = True
    #                                             break
    #                                         elif training_level.name == level:
    #                                             level_matches = True
    #                                             break
    #                                         elif training_level.name.lower() == student_level_raw.lower():
    #                                             level_matches = True
    #                                             break
    #                                         elif hasattr(training_level,
    #                                                      'key') and training_level.key == student_level_raw:
    #                                             level_matches = True
    #                                             break
    #
    #                                         level_mapping = {
    #                                             'one': ['L 1st', '1st', 'Level 1', 'First', 'one', 'One', 'ONE'],
    #                                             'two': ['L 2nd', '2nd', 'Level 2', 'Second', 'two', 'Two', 'TWO'],
    #                                             'three': ['L 3rd', '3rd', 'Level 3', 'Third', 'three', 'Three',
    #                                                       'THREE'],
    #                                             'four': ['L 4th', '4th', 'Level 4', 'Fourth', 'four', 'Four', 'FOUR']
    #                                         }
    #                                         if training_level.name in level_mapping.get(student_level_raw, []):
    #                                             level_matches = True
    #                                             break
    #                                 else:
    #                                     level_matches = True
    #
    #                                 if training_matches and level_matches:
    #                                     existing_registration = request.env['training.registration'].sudo().search([
    #                                         ('student_namee', '=', student_record.id),
    #                                         ('training_course_id', '=', training.id)
    #                                     ], limit=1)
    #
    #                                     total_registered = training.registered_count or 0
    #                                     remaining_spots = training.remaining_capacity or 0
    #                                     total_capacity = training.capacity or 0
    #
    #                                     training_name = 'No Training Name'
    #                                     if training.training and hasattr(training.training,
    #                                                                      'training_name') and training.training.training_name:
    #                                         training_name = training.training.training_name
    #                                     else:
    #                                         training_name = 'Unnamed Training'
    #                                     if training.is_weekly_breakdown and training.weekly_schedule_ids:
    #                                         sorted_weeks = training.weekly_schedule_ids.sorted('week_start_date')
    #                                         first_available = next((w for w in sorted_weeks if w.remaining_spots > 0),
    #                                                                None)
    #                                         week = first_available or (sorted_weeks[0] if sorted_weeks else None)
    #
    #                                         if week:
    #                                             available_weeks_info.append({
    #                                                 'week_number': week.week_number,
    #                                                 'start_date': week.week_start_date.strftime(
    #                                                     '%Y-%m-%d') if week.week_start_date else '',
    #                                                 'end_date': week.week_end_date.strftime(
    #                                                     '%Y-%m-%d') if week.week_end_date else '',
    #                                                 'remaining_spots': week.remaining_spots,
    #                                                 'max_students': week.max_students,
    #                                                 'registered_count': week.registered_count,
    #                                                 'is_active': week.is_active
    #                                             })
    #                                             remaining_spots = week.remaining_spots or 0
    #                                             max_students = week.max_students or 0
    #                                             total_registered = week.registered_count or 0
    #                                             students_capacity = max_students
    #                                     else:
    #                                         total_registered = training.registered_count or 0
    #                                         remaining_spots = training.remaining_capacity or 0
    #                                         students_capacity = total_capacity
    #
    #                                     if remaining_spots <= 0:
    #                                         availability_status = "full"
    #                                     elif remaining_spots <= 5:
    #                                         availability_status = "limited"
    #                                     else:
    #                                         availability_status = "available"
    #
    #                                     price_display = f"{training.cost} EGP" if training.cost else "Free"
    #
    #                                     levels = []
    #                                     if training.level_ids:
    #                                         levels = [{'id': level_record.id, 'name': level_record.name} for
    #                                                   level_record in training.level_ids]
    #
    #                                     training_info = {
    #                                         'partner': partner,
    #                                         'training': training,
    #                                         'company_name': partner.name or 'Unnamed Company',
    #                                         'company_details': partner.company_details_name or f'{partner.name} provides comprehensive training programs.',
    #                                         'image': partner.image,
    #                                         'training_title': partner.name or training_name,
    #                                         'duration': training.duration or 'Not specified',
    #                                         'code': training.code or 'No Code',
    #                                         'availability_status': availability_status,
    #                                         'is_full': remaining_spots <= 0,
    #                                         'price_display': price_display,
    #                                         'training_name': training_name,
    #                                         'levels': levels,
    #                                         'students_capacity': training.capacity,
    #                                         'total_capacity': total_capacity,
    #                                         'registered_count': total_registered,
    #                                         'remaining_spots': remaining_spots,
    #                                         'is_registered': bool(existing_registration),
    #                                         'total_no': partner.representatives,
    #                                         'is_weekly_breakdown': training.is_weekly_breakdown,
    #                                         'total_weeks': training.total_weeks if training.is_weekly_breakdown else 0,
    #                                         'students_per_week': max_students,
    #                                         'available_weeks_info': available_weeks_info,
    #                                         'available_weeks_count': len(available_weeks_info),
    #                                         'registration_status': existing_registration.registration_status if existing_registration else None
    #                                     }
    #                                     training_data.append(training_info)
    #
    #             else:
    #                 student_data = {
    #                     'name': student_record.name or 'Unknown Student',
    #                     'student_id': student_record.student_id or student_id,
    #                     'faculty_name': student_record.faculty.name if student_record.faculty else 'No Faculty',
    #                     'level': student_record.level or 'No Level',
    #                     'type': student_record.gender or 'No gender',
    #                     'university_name': student_record.university.name if student_record.university else 'No University',
    #                     'training_course_idd': None,
    #                     'no_training_course': True,
    #                 }
    #                 template_context = {
    #                     'student_data': student_data,
    #                     'training_data': [],
    #                     'student_id': student_id,
    #                     'search_performed': bool(student_id),
    #                 }
    #                 return request.render('nexus_nms.student_profile_template', template_context)
    #
    #         else:
    #             print(f"No student found with faculty_id: {student_id}")
    #             student_data = None
    #
    #     if training_data:
    #         training_data.sort(key=lambda x: (-x['remaining_spots'], x['company_name']))
    #
    #     if student_data:
    #         print(f"Student: {student_data['name']}")
    #         if student_data.get('training_course_idd'):
    #             print(f"Training course: {student_data['training_course_idd']}")
    #         print(f"Total matching trainings found: {len(training_data)}")
    #
    #     if training_data:
    #         for training_item in training_data:
    #             print(f"Found training: {training_item['company_name']} - {training_item['training_name']}")
    #
    #     template_context = {
    #         'student_data': student_data,
    #         'training_data': training_data,
    #         'student_id': student_id,
    #         'search_performed': bool(student_id),
    #     }
    #
    #     return request.render('nexus_nms.student_profile_template', template_context)
    @http.route('/training_pagee', type='http', auth='public', website=True)
    def simple_training_search(self, student_id=None, **kwargs):
        student_data = None
        training_data = []
        course_data = []
        my_courses_data = []
        my_certifications = []

        if student_id:
            student_id = str(student_id).strip()
            student_record = request.env['op.student'].sudo().search([('faculty_id', '=', student_id)], limit=1)

            if student_record:
                # if student_record.courses_id:
                #     for course in student_record.courses_id:
                #         my_courses_data.append({
                #             'name': course.name,
                #             'dr_name': course.dr_name.name if course.dr_name else '',
                #             'department': course.department.name if course.department else '',
                #         })

                if student_record.student_certification:
                    for certf in student_record.student_certification:
                        my_certifications.append({
                            'name': certf.name,
                            'course': certf.course_id.name if certf.course_id else '',
                            'certification_type': certf.certification_type,
                        })

                # Get student basic info
                gender = None
                if student_record.gender == 'm':
                    gender = 'Male'
                elif student_record.gender == 'f':
                    gender = 'Female'

                student_level_raw = student_record.level
                level = None
                if student_record.level == 'one':
                    level = 'L 1st'
                elif student_record.level == 'two':
                    level = 'L 2nd'
                elif student_record.level == 'three':
                    level = 'L 3rd'
                elif student_record.level == 'four':
                    level = 'L 4th'

                has_all_levels = getattr(student_record, 'all_levels', False)

                # ========== HANDLE TRAININGS ==========
                if student_record.training_course_idd:
                    student_training_course = student_record.training_course_idd.training_name
                    print(f'Training course ID: {student_training_course}')

                    student_data = {
                        'name': student_record.name or 'Unknown Student',
                        'student_id': student_record.student_id or student_id,
                        'faculty_name': student_record.faculty.name if student_record.faculty else 'No Faculty',
                        'level': level,
                        'level_raw': student_level_raw,
                        'type': gender,
                        'university_name': student_record.university.name if student_record.university else 'No University',
                        'training_course_idd': student_training_course,
                        'all_levels': has_all_levels,
                    }

                    confirmed_registrations = request.env['training.registration'].sudo().search([
                        ('student_namee', '=', student_record.id),
                        ('registration_status', '=', 'confirmed'),
                        ('is_course', '=', False)
                    ])

                    if confirmed_registrations:
                        registered_training_ids = confirmed_registrations.mapped('training_course_id.id')
                        print(f"Student has confirmed registrations for trainings: {registered_training_ids}")

                        partners = request.env['masrtech.register.partner'].sudo().search([('is_course', '=', False)])
                        for partner in partners:
                            if partner.training_table:
                                for training in partner.training_table:
                                    if training.id in registered_training_ids:
                                        registration = confirmed_registrations.filtered(
                                            lambda r: r.training_course_id.id == training.id)
                                        state = registration[0].course_status if registration else None

                                        total_registered = training.registered_count or 0
                                        remaining_spots = training.remaining_capacity or 0
                                        total_capacity = training.capacity or 0

                                        training_name = 'No Training Name'
                                        if training.training and hasattr(training.training,
                                                                         'training_name') and training.training.training_name:
                                            training_name = training.training.training_name
                                        else:
                                            training_name = 'Unnamed Training'

                                        if remaining_spots <= 0:
                                            availability_status = "full"
                                        elif remaining_spots <= 5:
                                            availability_status = "limited"
                                        else:
                                            availability_status = "available"

                                        price_display = f"{training.cost} EGP" if training.cost else ""

                                        levels = []
                                        if training.level_ids:
                                            levels = [{'id': level_record.id, 'name': level_record.name} for
                                                      level_record in training.level_ids]

                                        training_info = {
                                            'partner': partner,
                                            'training': training,
                                            'company_name': partner.name or 'Unnamed Company',
                                            'company_details': partner.company_details_name or f'{partner.name} provides comprehensive training programs.',
                                            'image': partner.image,
                                            'training_title': partner.name or training_name,
                                            'duration': training.duration or 'Not specified',
                                            'code': training.code or 'No Code',
                                            'students_capacity': total_capacity,
                                            'registered_count': total_registered,
                                            'remaining_spots': remaining_spots,
                                            'availability_status': availability_status,
                                            'is_full': remaining_spots <= 0,
                                            'price_display': price_display,
                                            'training_name': training_name,
                                            'levels': levels,
                                            'total_no': partner.representatives or total_capacity or 0,
                                            'is_registered': True,
                                            'registration_status': 'confirmed',
                                            'state': state
                                        }
                                        training_data.append(training_info)
                                        print('training_data', training_data)
                                        break
                    else:
                        print("Student has no confirmed registration, showing all available trainings")

                        partners = request.env['masrtech.register.partner'].sudo().search([('is_course', '=', False)])

                        for partner in partners:
                            if partner.training_table:
                                for training in partner.training_table:
                                    total_capacity = training.capacity or 0
                                    available_weeks_info = []
                                    students_capacity = 0
                                    remaining_spots = 0
                                    max_students = 0
                                    total_registered = 0
                                    training_matches = False
                                    level_matches = False

                                    if training.training and training.training.training_name == student_training_course:
                                        training_matches = True

                                    if has_all_levels:
                                        level_matches = True
                                        print(f"Student has all_levels access - showing all training levels")
                                    else:
                                        if training.level_ids:
                                            for training_level in training.level_ids:
                                                if training_level.name == student_level_raw:
                                                    level_matches = True
                                                    break
                                                elif training_level.name == level:
                                                    level_matches = True
                                                    break
                                                elif training_level.name.lower() == student_level_raw.lower():
                                                    level_matches = True
                                                    break
                                                elif hasattr(training_level,
                                                             'key') and training_level.key == student_level_raw:
                                                    level_matches = True
                                                    break

                                                level_mapping = {
                                                    'one': ['L 1st', '1st', 'Level 1', 'First', 'one', 'One', 'ONE'],
                                                    'two': ['L 2nd', '2nd', 'Level 2', 'Second', 'two', 'Two', 'TWO'],
                                                    'three': ['L 3rd', '3rd', 'Level 3', 'Third', 'three', 'Three',
                                                              'THREE'],
                                                    'four': ['L 4th', '4th', 'Level 4', 'Fourth', 'four', 'Four',
                                                             'FOUR']
                                                }
                                                if training_level.name in level_mapping.get(student_level_raw, []):
                                                    level_matches = True
                                                    break
                                        else:
                                            level_matches = True

                                    if training_matches and level_matches:
                                        existing_registration = request.env['training.registration'].sudo().search([
                                            ('student_namee', '=', student_record.id),
                                            ('training_course_id', '=', training.id)
                                        ], limit=1)

                                        total_registered = training.registered_count or 0
                                        remaining_spots = training.remaining_capacity or 0
                                        total_capacity = training.capacity or 0

                                        training_name = 'No Training Name'
                                        if training.training and hasattr(training.training,
                                                                         'training_name') and training.training.training_name:
                                            training_name = training.training.training_name
                                        else:
                                            training_name = 'Unnamed Training'

                                        if training.is_weekly_breakdown and training.weekly_schedule_ids:
                                            sorted_weeks = training.weekly_schedule_ids.sorted('week_start_date')
                                            first_available = next((w for w in sorted_weeks if w.remaining_spots > 0),
                                                                   None)
                                            week = first_available or (sorted_weeks[0] if sorted_weeks else None)

                                            if week:
                                                available_weeks_info.append({
                                                    'week_number': week.week_number,
                                                    'start_date': week.week_start_date.strftime(
                                                        '%Y-%m-%d') if week.week_start_date else '',
                                                    'end_date': week.week_end_date.strftime(
                                                        '%Y-%m-%d') if week.week_end_date else '',
                                                    'remaining_spots': week.remaining_spots,
                                                    'max_students': week.max_students,
                                                    'registered_count': week.registered_count,
                                                    'is_active': week.is_active
                                                })
                                                remaining_spots = week.remaining_spots or 0
                                                max_students = week.max_students or 0
                                                total_registered = week.registered_count or 0
                                                students_capacity = max_students
                                        else:
                                            total_registered = training.registered_count or 0
                                            remaining_spots = training.remaining_capacity or 0
                                            students_capacity = total_capacity

                                        if remaining_spots <= 0:
                                            availability_status = "full"
                                        elif remaining_spots <= 5:
                                            availability_status = "limited"
                                        else:
                                            availability_status = "available"

                                        price_display = f"{training.cost} EGP" if training.cost else "Free"

                                        levels = []
                                        if training.level_ids:
                                            levels = [{'id': level_record.id, 'name': level_record.name} for
                                                      level_record in training.level_ids]

                                        training_info = {
                                            'partner': partner,
                                            'training': training,
                                            'company_name': partner.name or 'Unnamed Company',
                                            'company_details': partner.company_details_name or f'{partner.name} provides comprehensive training programs.',
                                            'image': partner.image,
                                            'training_title': partner.name or training_name,
                                            'duration': training.duration or 'Not specified',
                                            'code': training.code or 'No Code',
                                            'availability_status': availability_status,
                                            'is_full': remaining_spots <= 0,
                                            'price_display': price_display,
                                            'training_name': training_name,
                                            'levels': levels,
                                            'students_capacity': training.capacity,
                                            'total_capacity': total_capacity,
                                            'registered_count': total_registered,
                                            'remaining_spots': remaining_spots,
                                            'is_registered': bool(existing_registration),
                                            'total_no': partner.representatives,
                                            'is_weekly_breakdown': training.is_weekly_breakdown,
                                            'total_weeks': training.total_weeks if training.is_weekly_breakdown else 0,
                                            'students_per_week': max_students,
                                            'available_weeks_info': available_weeks_info,
                                            'available_weeks_count': len(available_weeks_info),
                                            'registration_status': existing_registration.registration_status if existing_registration else None
                                        }
                                        training_data.append(training_info)

                if student_record.courses_id:
                    student_course_ids = student_record.courses_id.ids
                    print(f'Student course IDs: {student_course_ids}')

                    if not student_data:
                        student_data = {
                            'name': student_record.name or 'Unknown Student',
                            'student_id': student_record.student_id or student_id,
                            'faculty_name': student_record.faculty.name if student_record.faculty else 'No Faculty',
                            'level': level,
                            'level_raw': student_level_raw,
                            'type': gender,
                            'university_name': student_record.university.name if student_record.university else 'No University',
                            'courses_ids': student_course_ids,
                            'all_levels': has_all_levels,
                        }

                    confirmed_course_registrations = request.env['training.registration'].sudo().search([
                        ('student_namee', '=', student_record.id),
                        ('registration_status', '=', 'confirmed'),
                        ('is_course', '=', True)
                    ])

                    if confirmed_course_registrations:
                        registered_course_ids = confirmed_course_registrations.mapped('training_course_id.id')
                        print(f"Student has confirmed registrations for courses: {registered_course_ids}")

                        partners = request.env['masrtech.register.partner'].sudo().search([('is_course', '=', True)])
                        for partner in partners:
                            if partner.training_table:
                                for course in partner.training_table:
                                    if course.id in registered_course_ids:
                                        registration = confirmed_course_registrations.filtered(
                                            lambda r: r.training_course_id.id == course.id)
                                        state = registration[0].course_status if registration else None

                                        total_registered = course.registered_count or 0
                                        remaining_spots = course.remaining_capacity or 0
                                        total_capacity = course.capacity or 0

                                        course_name = 'No Course Name'
                                        if course.training and hasattr(course.training,
                                                                       'training_name') and course.training.training_name:
                                            course_name = course.training.training_name
                                        else:
                                            course_name = 'Unnamed Course'

                                        if remaining_spots <= 0:
                                            availability_status = "full"
                                        elif remaining_spots <= 5:
                                            availability_status = "limited"
                                        else:
                                            availability_status = "available"

                                        price_display = f"{course.cost} EGP" if course.cost else ""

                                        levels = []
                                        if course.level_ids:
                                            levels = [{'id': level_record.id, 'name': level_record.name} for
                                                      level_record in course.level_ids]

                                        course_info = {
                                            'partner': partner,
                                            'training': course,
                                            'company_name': partner.name or 'Unnamed Company',
                                            'company_details': partner.company_details_name or f'{partner.name} provides comprehensive courses.',
                                            'image': partner.image,
                                            'training_title': partner.name or course_name,
                                            'duration': course.duration or 'Not specified',
                                            'code': course.code or 'No Code',
                                            'students_capacity': total_capacity,
                                            'registered_count': total_registered,
                                            'remaining_spots': remaining_spots,
                                            'availability_status': availability_status,
                                            'is_full': remaining_spots <= 0,
                                            'price_display': price_display,
                                            'training_name': course_name,
                                            'levels': levels,
                                            'total_no': partner.representatives or total_capacity or 0,
                                            'is_registered': True,
                                            'registration_status': 'confirmed',
                                            'state': state
                                        }
                                        course_data.append(course_info)
                                        print('course_data', course_data)
                                        break
                    else:
                        print("Student has no confirmed course registration, showing all available courses")

                        partners = request.env['masrtech.register.partner'].sudo().search([('is_course', '=', True)])

                        for partner in partners:
                            if partner.training_table:
                                for course in partner.training_table:
                                    total_capacity = course.capacity or 0
                                    available_weeks_info = []
                                    students_capacity = 0
                                    remaining_spots = 0
                                    max_students = 0
                                    total_registered = 0
                                    course_matches = False
                                    level_matches = False

                                    # Check if course matches student's courses (check if course.training.id is in student_course_ids)
                                    if course.training and course.training.id in student_course_ids:
                                        course_matches = True

                                    if has_all_levels:
                                        level_matches = True
                                        print(f"Student has all_levels access - showing all course levels")
                                    else:
                                        if course.level_ids:
                                            for course_level in course.level_ids:
                                                if course_level.name == student_level_raw:
                                                    level_matches = True
                                                    break
                                                elif course_level.name == level:
                                                    level_matches = True
                                                    break
                                                elif course_level.name.lower() == student_level_raw.lower():
                                                    level_matches = True
                                                    break
                                                elif hasattr(course_level,
                                                             'key') and course_level.key == student_level_raw:
                                                    level_matches = True
                                                    break

                                                level_mapping = {
                                                    'one': ['L 1st', '1st', 'Level 1', 'First', 'one', 'One', 'ONE'],
                                                    'two': ['L 2nd', '2nd', 'Level 2', 'Second', 'two', 'Two', 'TWO'],
                                                    'three': ['L 3rd', '3rd', 'Level 3', 'Third', 'three', 'Three',
                                                              'THREE'],
                                                    'four': ['L 4th', '4th', 'Level 4', 'Fourth', 'four', 'Four',
                                                             'FOUR']
                                                }
                                                if course_level.name in level_mapping.get(student_level_raw, []):
                                                    level_matches = True
                                                    break
                                        else:
                                            level_matches = True

                                    if course_matches and level_matches:
                                        existing_registration = request.env['training.registration'].sudo().search([
                                            ('student_namee', '=', student_record.id),
                                            ('training_course_id', '=', course.id)
                                        ], limit=1)

                                        total_registered = course.registered_count or 0
                                        remaining_spots = course.remaining_capacity or 0
                                        total_capacity = course.capacity or 0

                                        course_name = 'No Course Name'
                                        if course.training and hasattr(course.training,
                                                                       'training_name') and course.training.training_name:
                                            course_name = course.training.training_name
                                        else:
                                            course_name = 'Unnamed Course'

                                        if course.is_weekly_breakdown and course.weekly_schedule_ids:
                                            sorted_weeks = course.weekly_schedule_ids.sorted('week_start_date')
                                            first_available = next((w for w in sorted_weeks if w.remaining_spots > 0),
                                                                   None)
                                            week = first_available or (sorted_weeks[0] if sorted_weeks else None)

                                            if week:
                                                available_weeks_info.append({
                                                    'week_number': week.week_number,
                                                    'start_date': week.week_start_date.strftime(
                                                        '%Y-%m-%d') if week.week_start_date else '',
                                                    'end_date': week.week_end_date.strftime(
                                                        '%Y-%m-%d') if week.week_end_date else '',
                                                    'remaining_spots': week.remaining_spots,
                                                    'max_students': week.max_students,
                                                    'registered_count': week.registered_count,
                                                    'is_active': week.is_active
                                                })
                                                remaining_spots = week.remaining_spots or 0
                                                max_students = week.max_students or 0
                                                total_registered = week.registered_count or 0
                                                students_capacity = max_students
                                        else:
                                            total_registered = course.registered_count or 0
                                            remaining_spots = course.remaining_capacity or 0
                                            students_capacity = total_capacity

                                        if remaining_spots <= 0:
                                            availability_status = "full"
                                        elif remaining_spots <= 5:
                                            availability_status = "limited"
                                        else:
                                            availability_status = "available"

                                        price_display = f"{course.cost} EGP" if course.cost else "Free"

                                        levels = []
                                        if course.level_ids:
                                            levels = [{'id': level_record.id, 'name': level_record.name} for
                                                      level_record in course.level_ids]

                                        course_info = {
                                            'partner': partner,
                                            'training': course,
                                            'company_name': partner.name or 'Unnamed Company',
                                            'company_details': partner.company_details_name or f'{partner.name} provides comprehensive courses.',
                                            'image': partner.image,
                                            'training_title': partner.name or course_name,
                                            'duration': course.duration or 'Not specified',
                                            'code': course.code or 'No Code',
                                            'availability_status': availability_status,
                                            'is_full': remaining_spots <= 0,
                                            'price_display': price_display,
                                            'training_name': course_name,
                                            'levels': levels,
                                            'students_capacity': course.capacity,
                                            'total_capacity': total_capacity,
                                            'registered_count': total_registered,
                                            'remaining_spots': remaining_spots,
                                            'is_registered': bool(existing_registration),
                                            'total_no': partner.representatives,
                                            'is_weekly_breakdown': course.is_weekly_breakdown,
                                            'total_weeks': course.total_weeks if course.is_weekly_breakdown else 0,
                                            'students_per_week': max_students,
                                            'available_weeks_info': available_weeks_info,
                                            'available_weeks_count': len(available_weeks_info),
                                            'registration_status': existing_registration.registration_status if existing_registration else None
                                        }
                                        course_data.append(course_info)

                # If no training or course assigned
                if not student_record.training_course_idd and not student_record.courses_id:
                    student_data = {
                        'name': student_record.name or 'Unknown Student',
                        'student_id': student_record.student_id or student_id,
                        'faculty_name': student_record.faculty.name if student_record.faculty else 'No Faculty',
                        'level': student_record.level or 'No Level',
                        'type': student_record.gender or 'No gender',
                        'university_name': student_record.university.name if student_record.university else 'No University',
                        'training_course_idd': None,
                        'no_training_course': True,
                    }
                    template_context = {
                        'student_data': student_data,
                        'training_data': [],
                        'course_data': [],
                        'student_id': student_id,
                        'search_performed': bool(student_id),
                        'my_courses_data': my_courses_data,
                        'my_certifications': my_certifications,
                    }
                    return request.render('nexus_nms.student_profile_template', template_context)

            else:
                print(f"No student found with faculty_id: {student_id}")
                student_data = None

        # Sort data
        if training_data:
            training_data.sort(key=lambda x: (-x['remaining_spots'], x['company_name']))
        if course_data:
            course_data.sort(key=lambda x: (-x['remaining_spots'], x['company_name']))

        if student_data:
            print(f"Student: {student_data['name']}")
            if student_data.get('training_course_idd'):
                print(f"Training course: {student_data['training_course_idd']}")
            if student_data.get('courses_ids'):
                print(f"Course IDs: {student_data['courses_ids']}")
            if student_data.get('all_levels'):
                print(f"Student has access to all levels")
            print(f"Total matching trainings found: {len(training_data)}")
            print(f"Total matching courses found: {len(course_data)}")

        if training_data:
            for training_item in training_data:
                print(f"Found training: {training_item['company_name']} - {training_item['training_name']}")

        if course_data:
            for course_item in course_data:
                print(f"Found course: {course_item['company_name']} - {course_item['training_name']}")

        template_context = {
            'student_data': student_data,
            'training_data': training_data,
            'course_data': course_data,
            'student_id': student_id,
            'my_courses_data': my_courses_data,
            'my_certifications': my_certifications,
            'search_performed': bool(student_id),
        }

        return request.render('nexus_nms.student_profile_template', template_context)
    # @http.route('/training_pagee', type='http', auth='public', website=True)
    # def simple_training_search(self, student_id=None, **kwargs):
    #     student_data = None
    #     training_data = []
    #     my_courses_data = []
    #     my_certifications = []
    #     if student_id:
    #         student_id = str(student_id).strip()
    #         student_record = request.env['op.student'].sudo().search([('faculty_id', '=', student_id)], limit=1)
    #
    #         if student_record:
    #             if student_record.courses_id:
    #                 for course in student_record.courses_id:
    #                     my_courses_data.append({
    #                         'name': course.name,
    #                         'dr_name': course.dr_name.name,
    #                         'department': course.department.name,
    #                     })
    #             if student_record.student_certification:
    #                 for certf in student_record.student_certification:
    #                     my_certifications.append({
    #                         'name': certf.name,
    #                         'course': certf.course_id.name,
    #                         'certification_type': certf.certification_type,
    #                     })
    #             if student_record.training_course_idd:
    #                 student_training_course = student_record.training_course_idd.training_name
    #                 print(f'Training course ID: {student_training_course}')
    #
    #                 gender = None
    #                 if student_record.gender == 'm':
    #                     gender = 'Male'
    #                 elif student_record.gender == 'f':
    #                     gender = 'Female'
    #
    #                 student_level_raw = student_record.level
    #                 level = None
    #                 if student_record.level == 'one':
    #                     level = 'L 1st'
    #                 elif student_record.level == 'two':
    #                     level = 'L 2nd'
    #                 elif student_record.level == 'three':
    #                     level = 'L 3rd'
    #                 elif student_record.level == 'four':
    #                     level = 'L 4th'
    #
    #                 has_all_levels = getattr(student_record, 'all_levels', False)
    #
    #                 student_data = {
    #                     'name': student_record.name or 'Unknown Student',
    #                     'student_id': student_record.student_id or student_id,
    #                     'faculty_name': student_record.faculty.name if student_record.faculty else 'No Faculty',
    #                     'level': level,
    #                     'level_raw': student_level_raw,
    #                     'type': gender,
    #                     'university_name': student_record.university.name if student_record.university else 'No University',
    #                     'training_course_idd': student_training_course,
    #                     'all_levels': has_all_levels,
    #                 }
    #                 confirmed_registrations = request.env['training.registration'].sudo().search([
    #                     ('student_namee', '=', student_record.id),
    #                     ('registration_status', '=', 'confirmed')
    #                 ])
    #                 state =confirmed_registrations.course_status
    #                 print(state,'state')
    #                 if confirmed_registrations:
    #                     registered_training_ids = confirmed_registrations.mapped('training_course_id.id')
    #                     print(f"Student has confirmed registrations for trainings: {registered_training_ids}")
    #
    #                     partners = request.env['masrtech.register.partner'].sudo().search([])
    #                     for partner in partners:
    #                         if partner.training_table:
    #                             for training in partner.training_table:
    #                                 if training.id in registered_training_ids:
    #                                     total_registered = training.registered_count or 0
    #                                     remaining_spots = training.remaining_capacity or 0
    #                                     total_capacity = training.capacity or 0
    #
    #                                     training_name = 'No Training Name'
    #                                     if training.training and hasattr(training.training,
    #                                                                      'training_name') and training.training.training_name:
    #                                         training_name = training.training.training_name
    #                                     else:
    #                                         training_name = 'Unnamed Training'
    #
    #                                     if remaining_spots <= 0:
    #                                         availability_status = "full"
    #                                     elif remaining_spots <= 5:
    #                                         availability_status = "limited"
    #                                     else:
    #                                         availability_status = "available"
    #
    #                                     price_display = f"{training.cost} EGP" if training.cost else ""
    #
    #                                     levels = []
    #                                     if training.level_ids:
    #                                         levels = [{'id': level_record.id, 'name': level_record.name} for
    #                                                   level_record in training.level_ids]
    #
    #                                     training_info = {
    #                                         'partner': partner,
    #                                         'training': training,
    #                                         'company_name': partner.name or 'Unnamed Company',
    #                                         'company_details': partner.company_details_name or f'{partner.name} provides comprehensive training programs.',
    #                                         'image': partner.image,
    #                                         'training_title': partner.name or training_name,
    #                                         'duration': training.duration or 'Not specified',
    #                                         'code': training.code or 'No Code',
    #                                         'students_capacity': total_capacity,
    #                                         'registered_count': total_registered,
    #                                         'remaining_spots': remaining_spots,
    #                                         'availability_status': availability_status,
    #                                         'is_full': remaining_spots <= 0,
    #                                         'price_display': price_display,
    #                                         'training_name': training_name,
    #                                         'levels': levels,
    #                                         'total_no': partner.representatives or total_capacity or 0,
    #                                         'is_registered': True,
    #                                         'registration_status': 'confirmed',
    #                                         'state':state
    #
    #                                     }
    #                                     training_data.append(training_info)
    #                                     print('training_data',training_data)
    #                                     break
    #                 else:
    #                     print("Student has no confirmed registration, showing all available trainings")
    #
    #                     partners = request.env['masrtech.register.partner'].sudo().search([])
    #
    #                     for partner in partners:
    #                         if partner.training_table:
    #                             for training in partner.training_table:
    #                                 total_capacity = training.capacity or 0
    #                                 available_weeks_info = []
    #                                 students_capacity = 0
    #                                 remaining_spots = 0
    #                                 max_students = 0
    #                                 total_registered = 0
    #                                 training_matches = False
    #                                 level_matches = False
    #
    #                                 if training.training and training.training.training_name == student_training_course:
    #                                     training_matches = True
    #
    #                                 if has_all_levels:
    #                                     level_matches = True
    #                                     print(f"Student has all_levels access - showing all training levels")
    #                                 else:
    #                                     if training.level_ids:
    #                                         for training_level in training.level_ids:
    #                                             if training_level.name == student_level_raw:
    #                                                 level_matches = True
    #                                                 break
    #                                             elif training_level.name == level:
    #                                                 level_matches = True
    #                                                 break
    #                                             elif training_level.name.lower() == student_level_raw.lower():
    #                                                 level_matches = True
    #                                                 break
    #                                             elif hasattr(training_level,
    #                                                          'key') and training_level.key == student_level_raw:
    #                                                 level_matches = True
    #                                                 break
    #
    #                                             level_mapping = {
    #                                                 'one': ['L 1st', '1st', 'Level 1', 'First', 'one', 'One', 'ONE'],
    #                                                 'two': ['L 2nd', '2nd', 'Level 2', 'Second', 'two', 'Two', 'TWO'],
    #                                                 'three': ['L 3rd', '3rd', 'Level 3', 'Third', 'three', 'Three',
    #                                                           'THREE'],
    #                                                 'four': ['L 4th', '4th', 'Level 4', 'Fourth', 'four', 'Four',
    #                                                          'FOUR']
    #                                             }
    #                                             if training_level.name in level_mapping.get(student_level_raw, []):
    #                                                 level_matches = True
    #                                                 break
    #                                     else:
    #                                         level_matches = True
    #
    #                                 if training_matches and level_matches:
    #                                     existing_registration = request.env['training.registration'].sudo().search([
    #                                         ('student_namee', '=', student_record.id),
    #                                         ('training_course_id', '=', training.id)
    #                                     ], limit=1)
    #
    #                                     total_registered = training.registered_count or 0
    #                                     remaining_spots = training.remaining_capacity or 0
    #                                     total_capacity = training.capacity or 0
    #
    #                                     training_name = 'No Training Name'
    #                                     if training.training and hasattr(training.training,
    #                                                                      'training_name') and training.training.training_name:
    #                                         training_name = training.training.training_name
    #                                     else:
    #                                         training_name = 'Unnamed Training'
    #                                     if training.is_weekly_breakdown and training.weekly_schedule_ids:
    #                                         sorted_weeks = training.weekly_schedule_ids.sorted('week_start_date')
    #                                         first_available = next((w for w in sorted_weeks if w.remaining_spots > 0),
    #                                                                None)
    #                                         week = first_available or (sorted_weeks[0] if sorted_weeks else None)
    #
    #                                         if week:
    #                                             available_weeks_info.append({
    #                                                 'week_number': week.week_number,
    #                                                 'start_date': week.week_start_date.strftime(
    #                                                     '%Y-%m-%d') if week.week_start_date else '',
    #                                                 'end_date': week.week_end_date.strftime(
    #                                                     '%Y-%m-%d') if week.week_end_date else '',
    #                                                 'remaining_spots': week.remaining_spots,
    #                                                 'max_students': week.max_students,
    #                                                 'registered_count': week.registered_count,
    #                                                 'is_active': week.is_active
    #                                             })
    #                                             remaining_spots = week.remaining_spots or 0
    #                                             max_students = week.max_students or 0
    #                                             total_registered = week.registered_count or 0
    #                                             students_capacity = max_students
    #                                     else:
    #                                         total_registered = training.registered_count or 0
    #                                         remaining_spots = training.remaining_capacity or 0
    #                                         students_capacity = total_capacity
    #
    #                                     if remaining_spots <= 0:
    #                                         availability_status = "full"
    #                                     elif remaining_spots <= 5:
    #                                         availability_status = "limited"
    #                                     else:
    #                                         availability_status = "available"
    #
    #                                     price_display = f"{training.cost} EGP" if training.cost else "Free"
    #
    #                                     levels = []
    #                                     if training.level_ids:
    #                                         levels = [{'id': level_record.id, 'name': level_record.name} for
    #                                                   level_record in training.level_ids]
    #
    #                                     training_info = {
    #                                         'partner': partner,
    #                                         'training': training,
    #                                         'company_name': partner.name or 'Unnamed Company',
    #                                         'company_details': partner.company_details_name or f'{partner.name} provides comprehensive training programs.',
    #                                         'image': partner.image,
    #                                         'training_title': partner.name or training_name,
    #                                         'duration': training.duration or 'Not specified',
    #                                         'code': training.code or 'No Code',
    #                                         'availability_status': availability_status,
    #                                         'is_full': remaining_spots <= 0,
    #                                         'price_display': price_display,
    #                                         'training_name': training_name,
    #                                         'levels': levels,
    #                                         'students_capacity': training.capacity,
    #                                         'total_capacity': total_capacity,
    #                                         'registered_count': total_registered,
    #                                         'remaining_spots': remaining_spots,
    #                                         'is_registered': bool(existing_registration),
    #                                         'total_no': partner.representatives,
    #                                         'is_weekly_breakdown': training.is_weekly_breakdown,
    #                                         'total_weeks': training.total_weeks if training.is_weekly_breakdown else 0,
    #                                         'students_per_week': max_students,
    #                                         'available_weeks_info': available_weeks_info,
    #                                         'available_weeks_count': len(available_weeks_info),
    #                                         'registration_status': existing_registration.registration_status if existing_registration else None
    #                                     }
    #                                     training_data.append(training_info)
    #
    #
    #             else:
    #                 student_data = {
    #                     'name': student_record.name or 'Unknown Student',
    #                     'student_id': student_record.student_id or student_id,
    #                     'faculty_name': student_record.faculty.name if student_record.faculty else 'No Faculty',
    #                     'level': student_record.level or 'No Level',
    #                     'type': student_record.gender or 'No gender',
    #                     'university_name': student_record.university.name if student_record.university else 'No University',
    #                     'training_course_idd': None,
    #                     'no_training_course': True,
    #                 }
    #                 template_context = {
    #                     'student_data': student_data,
    #                     'training_data': [],
    #                     'student_id': student_id,
    #                     'search_performed': bool(student_id),
    #                     'my_courses_data': my_courses_data,
    #                     'my_certifications': my_certifications,
    #                 }
    #                 return request.render('nexus_nms.student_profile_template', template_context)
    #
    #         else:
    #             print(f"No student found with faculty_id: {student_id}")
    #             student_data = None
    #
    #     if training_data:
    #         training_data.sort(key=lambda x: (-x['remaining_spots'], x['company_name']))
    #
    #     if student_data:
    #         print(f"Student: {student_data['name']}")
    #         if student_data.get('training_course_idd'):
    #             print(f"Training course: {student_data['training_course_idd']}")
    #         if student_data.get('all_levels'):
    #             print(f"Student has access to all levels")
    #         print(f"Total matching trainings found: {len(training_data)}")
    #
    #     if training_data:
    #         for training_item in training_data:
    #             print(f"Found training: {training_item['company_name']} - {training_item['training_name']}")
    #
    #     template_context = {
    #         'student_data': student_data,
    #         'training_data': training_data,
    #         'student_id': student_id,
    #         'my_courses_data': my_courses_data,
    #         'my_certifications': my_certifications,
    #         'search_performed': bool(student_id),
    #     }
    #
    #     return request.render('nexus_nms.student_profile_template', template_context)

    @http.route('/chatbot', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def chatbot_ai(self, **kw):
        return request.render('nexus_nms.chatbot_template', {})

    @http.route('/ai/ask', type='http', auth='user', methods=['POST'], csrf=False)
    def ask_ai(self):
        try:
            # For type='http' routes, parse JSON from request body
            import json

            # Get raw request data
            raw_data = request.httprequest.get_data()
            data = json.loads(raw_data.decode('utf-8'))

            question = data.get('question')

            if not question:
                return http.Response(
                    json.dumps({'error': 'Missing question'}),
                    content_type='application/json',
                    status=400
                )

            payload = {"question": question}
            icp = request.env['ir.config_parameter'].sudo()
            ai_endpoint = icp.get_param('nexus_nms.ai_endpoint', 'http://209.38.41.253:8001/ask')

            response = requests.post(ai_endpoint, json=payload, timeout=30)

            if response.status_code != 200:
                return http.Response(
                    json.dumps({'error': f'External API error: {response.status_code}'}),
                    content_type='application/json',
                    status=500
                )

            return http.Response(
                json.dumps(response.json()),
                content_type='application/json'
            )

        except Exception as e:
            return http.Response(
                json.dumps({"error": str(e)}),
                content_type='application/json',
                status=500
            )

    @http.route("/discuss/channel/<int>", type='http', auth='public')
    def student_check(self, training_id, student_id=None):
        training = request.env['training.weekly.schedule'].sudo().browse(int(training_id))

        if student_id:
            # Check if student is registered
            registration = request.env['training.registration'].sudo().search([
                ('student_id', '=', student_id),
                ('training_schedule_id', '=', training.id),
                ('registration_status', '=', 'confirmed')
            ])

            if registration:
                # Valid student - redirect to chat
                return request.redirect(f'/web#action=discuss.action_discuss&invitation_url={training.invitation_url}')
            else:
                error = "Student not registered for this training"
        else:
            error = ""

        # Show form
        return f"""
            <html>
            <body style="font-family: Arial; padding: 50px; background: #f5f5f5;">
                <div style="max-width: 400px; margin: auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 20px rgba(0,0,0,0.1);">
                    <h2 style="text-align: center; color: #333;">Join Training Session</h2>
                    <form method="GET">
                        <input type="hidden" name="training_id" value="{training_id}">
                        <label style="display: block; margin: 15px 0 5px; font-weight: bold;">Student ID:</label>
                        <input type="text" name="student_id" style="width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px;" placeholder="Enter your Student ID" required>
                        {f'<div style="color: red; margin: 10px 0; font-size: 14px;">{error}</div>' if error else ''}
                        <button type="submit" style="width: 100%; padding: 12px; background: #007cba; color: white; border: none; border-radius: 5px; font-size: 16px; margin-top: 15px; cursor: pointer;">Join Chat</button>
                    </form>
                </div>
            </body>
            </html>
            """
    # ############################cocacola####################

    # @http.route('/cocacola/apply', type='http',methods=['POST','GET'], auth='public', website=True)
    # def application_form(self, **kw):
    #     universities = request.env['masrtech.universities'].sudo().search([])
    #     return request.render('nexus_nms.registration_for_cocacola',{
    #         'universities': universities,
    #     })
    #
    # @http.route('/cocacola/submit', type='http', auth='public', methods=['POST', 'GET'], csrf=False, website=True)
    # def submit_application_cocacola(self, **kw):
    #     national_id = kw.get('national_id')
    #     student_name = kw.get('name')
    #
    #     student = request.env['op.student'].sudo().search([('vat', '=', national_id)], limit=1)
    #
    #     if not student:
    #         student_data = {
    #             'name': kw.get('name'),
    #             'email': kw.get('email'),
    #             'phone': kw.get('phone'),
    #             'vat': national_id,
    #             'university': kw.get('university'),
    #         }
    #         student = request.env['op.student'].sudo().create(student_data)
    #
    #     application_data = {
    #         'student_namee': student.id,
    #         'email': kw.get('email'),
    #         'password': kw.get('password'),
    #         'phone': kw.get('phone'),
    #         'university': kw.get('university'),
    #         'age': int(kw.get('age', 0)) if kw.get('age') else 0,
    #         'national_id': national_id,
    #     }
    #     application = request.env['cocacola.model'].sudo().create(application_data)
    #
    #     return request.render('nexus_nms.registration_for_cocacola_confirm', {
    #         'application': application,
    #         'student': student,
    #     })
    @http.route('/cocacola/apply', type='http', methods=['POST', 'GET'], auth='public', website=True)
    def application_form(self, **kw):
        universities = request.env['masrtech.universities'].sudo().search([])
        return request.render('nexus_nms.registration_for_cocacola', {
            'universities': universities,
        })

    @http.route('/cocacola/submit', type='http', auth='public', methods=['POST', 'GET'], csrf=False, website=True)
    def submit_application_cocacola(self, **kw):
        password = kw.get('password', '')

        if len(password) < 8:
            universities = request.env['masrtech.universities'].sudo().search([])
            return request.render('nexus_nms.registration_for_cocacola', {
                'universities': universities,
                'error_message': 'Password must be at least 8 characters long',
                'form_data': kw
            })

        national_id = kw.get('national_id')
        student = request.env['op.student'].sudo().search([('vat', '=', national_id)], limit=1)

        if not student:
            student_data = {
                'name': kw.get('name'),
                'email': kw.get('email'),
                'phone': kw.get('phone'),
                'vat': national_id,
            }
            student = request.env['op.student'].sudo().create(student_data)

        university_value = kw.get('university')
        if university_value:
            try:
                university_value = int(university_value)
            except:
                university_record = request.env['masrtech.universities'].sudo().search(
                    [('name', '=', university_value)], limit=1)
                if university_record:
                    university_value = university_record.id

        application_data = {
            'student_namee': student.id,
            'email': kw.get('email'),
            'password': password,
            'phone': kw.get('phone'),
            'age': int(kw.get('age', 0)) if kw.get('age') else 0,
            'national_id': national_id,
            'gender': kw.get('gender'),
        }

        if university_value:
            application_data['university_id'] = university_value

        application = request.env['cocacola.model'].sudo().create(application_data)

        return request.render('nexus_nms.registration_for_cocacola_confirm', {
            'application': application,
            'student': student,
        })
