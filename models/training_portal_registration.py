# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re


class TrainingPortalRegistration(models.Model):
    _name        = 'training.portal.registration'
    _description = 'Student Training Registration'
    _inherit     = ['mail.thread', 'mail.activity.mixin']
    _rec_name    = 'student_name'
    _order       = 'create_date desc'

    # ── Student Information ───────────────────────────────────────────────────

    student_name = fields.Char(string='Full Name', required=True, tracking=True)

    university_name = fields.Selection(
        selection=[('baraj', 'جامعة برج العرب التكنولوجية')],
        string='University Name', required=True, tracking=True)

    university_id = fields.Char(
        string='Student University ID', required=True, tracking=True)

    university_group = fields.Selection(
        selection=[
            ('group_1', 'Group 1'),
            ('group_2', 'Group 2'),
            ('group_3', 'Group 3'),
            ('group_4', 'Group 4'),
        ],
        string='University Group', required=True, tracking=True)

    national_id = fields.Char(
        string='Student National ID', required=True, tracking=True)

    phone_whatsapp = fields.Char(
        string='Phone Number (WhatsApp)', required=True, tracking=True)

    # ── Training Information (Many2one) ───────────────────────────────────────

    training_company_id = fields.Many2one(
        comodel_name='masrtech.register.partner',
        string='Training Company',
        required=True,
        tracking=True,
        ondelete='restrict',
    )

    training_program_id = fields.Many2one(
        comodel_name='registrar.partner.training.table',
        string='Training Program',
        required=True,
        tracking=True,
        ondelete='restrict',
        domain="[('relation_id', '=', training_company_id)]",
    )

    training_week_id = fields.Many2one(
        comodel_name='training.weekly.schedule',
        string='Training Week',
        required=True,
        tracking=True,
        ondelete='restrict',
        domain="[('training_id', '=', training_program_id)]",
    )

    # ── Related convenience fields ────────────────────────────────────────────

    week_start_date = fields.Date(
        related='training_week_id.week_start_date', store=True, readonly=True)

    week_end_date = fields.Date(
        related='training_week_id.week_end_date', store=True, readonly=True)

    # ── Status ────────────────────────────────────────────────────────────────

    state = fields.Selection(
        selection=[
            ('draft',     'Submitted'),
            ('confirmed', 'Confirmed'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        default='draft',
        tracking=True,
        readonly=True,
    )

    # ── Constraints ──────────────────────────────────────────────────────────

    @api.constrains('national_id')
    def _check_national_id(self):
        for rec in self:
            if rec.national_id and not re.match(r'^\d{14}$', rec.national_id):
                raise ValidationError(_('National ID must be exactly 14 digits.'))

    @api.constrains('training_week_id')
    def _check_week_capacity(self):
        """Block registrations beyond the week's max capacity."""
        for rec in self:
            if not rec.training_week_id:
                continue
            week = rec.training_week_id
            if week.is_full:
                raise ValidationError(_(
                    'Sorry, Week %s (%s – %s) is fully booked. '
                    'Please choose another week.'
                ) % (
                    week.week_number,
                    week.week_start_date,
                    week.week_end_date,
                ))

    # ── State actions ─────────────────────────────────────────────────────────

    def action_confirm(self):
        for rec in self:
            if rec.training_week_id and rec.training_week_id.is_full:
                raise ValidationError(_((
                    'Sorry, Week %s (%s – %s) is fully booked. '
                    'Please choose another week.'
                ) % (
                    rec.training_week_id.week_number,
                    rec.training_week_id.week_start_date,
                    rec.training_week_id.week_end_date,
                )))
        self.write({'state': 'confirmed'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_reset(self):
        self.write({'state': 'draft'})