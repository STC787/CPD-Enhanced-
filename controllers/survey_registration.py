# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.exceptions import UserError
from odoo.http import request


class SurveyRegistrationController(http.Controller):
    """Public 'enter your name to register' gate shown before a respondent
    is sent into the standard Odoo survey-taking flow (/survey/start/...).
    """

    def _get_survey(self, survey_token):
        return request.env['survey.survey'].sudo().search(
            [('access_token', '=', survey_token)], limit=1
        )

    def _get_existing_answer(self, survey_sudo, answer_token):
        if not answer_token:
            return None
        return request.env['survey.user_input'].sudo().search([
            ('access_token', '=', answer_token),
            ('survey_id', '=', survey_sudo.id),
        ], limit=1)

    @http.route('/survey/register/<string:survey_token>', type='http', auth='public',
                website=True, csrf=False)
    def survey_register_form(self, survey_token, answer_token=None, **kw):
        survey_sudo = self._get_survey(survey_token)
        if not survey_sudo:
            return request.render('nexus_nms.survey_register_not_found', {})

        # Resuming an already-registered answer (e.g. a reminder/invite email
        # link) skips the name form and goes straight into the real survey.
        if self._get_existing_answer(survey_sudo, answer_token):
            return request.redirect(
                '/survey/start/%s?answer_token=%s' % (survey_token, answer_token)
            )

        if survey_sudo._is_not_yet_open():
            return request.render('nexus_nms.survey_register_not_open', {'survey': survey_sudo})

        if not survey_sudo.active or survey_sudo._is_deadline_expired():
            return request.render('nexus_nms.survey_register_expired', {'survey': survey_sudo})

        return request.render('nexus_nms.survey_register_form', {
            'survey': survey_sudo,
            'error_message': kw.get('error_message', ''),
            'name': kw.get('name', ''),
            'email': kw.get('email', ''),
        })

    @http.route('/survey/register/<string:survey_token>/submit', type='http', auth='public',
                website=True, methods=['POST'], csrf=False)
    def survey_register_submit(self, survey_token, **post):
        survey_sudo = self._get_survey(survey_token)
        if not survey_sudo:
            return request.render('nexus_nms.survey_register_not_found', {})

        if survey_sudo._is_not_yet_open():
            return request.render('nexus_nms.survey_register_not_open', {'survey': survey_sudo})

        if not survey_sudo.active or survey_sudo._is_deadline_expired():
            return request.render('nexus_nms.survey_register_expired', {'survey': survey_sudo})

        name = (post.get('name') or '').strip()
        email = (post.get('email') or '').strip()

        if not name:
            return request.render('nexus_nms.survey_register_form', {
                'survey': survey_sudo,
                'error_message': _('Please enter your name to register for this survey.'),
                'name': name,
                'email': email,
            })

        try:
            answer_sudo = survey_sudo._create_answer(
                user=request.env.user,
                email=email or False,
                nickname=name,
            )
        except UserError as e:
            return request.render('nexus_nms.survey_register_form', {
                'survey': survey_sudo,
                'error_message': str(e),
                'name': name,
                'email': email,
            })

        return request.redirect(
            '/survey/start/%s?answer_token=%s' % (survey_sudo.access_token, answer_sudo.access_token)
        )
