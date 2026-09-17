# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from werkzeug.utils import redirect


class StudentSearchController(http.Controller):

    @http.route('/student/search/<string:is_course>', type='http', auth='public', website=True, csrf=False)
    def student_search(self, is_course, **kw):
        is_course = is_course.lower() == 'true'
        all_courses = request.env['registrar.partner.training.table'].sudo().search([])
        # training_courses = request.env['registrar.partner.training.table'].sudo().search([('is_course', '=', False)])

        return request.render('nexus_nms.student_search_template', {
            'all_courses': all_courses,
            # 'training_courses': training_courses,
            'is_course': is_course,
        })

    @http.route('/student/confirm', type='http', auth='public', website=True, csrf=False)
    def student_confirm(self, **kw):
        search_query = kw.get('search_query', '').strip()
        course_id = kw.get('course_id', False)
        all_courses = request.env['registrar.partner.training.table'].sudo().search([])

        student = None
        if search_query:
            student = request.env['op.student'].sudo().search([('faculty_id', '=', search_query)], limit=1)

        course = None
        if course_id:
            try:
                course = request.env['registrar.partner.training.table'].sudo().browse(int(course_id))
                if not course.exists():
                    course = None
            except:
                course = None

        if not student:
            error_message = "Please Select valid id"
            return request.render('nexus_nms.student_search_template', {
                'student': None,
                'course': None,
                'all_courses': all_courses,
                'search_query': search_query,
                'selected_course_id': course_id,
                'error_message': error_message,
            })

        if not course:
            error_message = "Please select a course before confirming."
            return request.render('nexus_nms.student_search_template', {
                'student': None,
                'course': None,
                'all_courses': all_courses,
                'search_query': search_query,
                'selected_course_id': course_id,
                'error_message': error_message,
            })

        if student and course:
            for line in student.quiz_ids:
                if line.exam_id.state == 'active':
                    if line.opened_quiz:
                        error_message = "The exam is available for one trial."
                        return request.render('nexus_nms.student_search_template', {
                            'student': student,
                            'course': course,
                            'all_courses': all_courses,
                            'search_query': search_query,
                            'selected_course_id': course_id,
                            'error_message': error_message,
                        })
                    else:
                        line.opened_quiz = True
                        session_link = line.exam_id.session_link or ''
                        if session_link.startswith(('http://', 'https://', '/')):
                            return redirect(session_link)

        error_message = "The selected course '{}' does not have an active quiz session available.".format(
            course.name)
        return request.render('nexus_nms.student_search_template', {
            'student': student,
            'course': course,
            'all_courses': all_courses,
            'search_query': search_query,
            'selected_course_id': course_id,
            'error_message': error_message,
        })
