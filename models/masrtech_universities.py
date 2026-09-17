from odoo import api, models, fields


class MasrtechuUniversities(models.Model):
    _name = 'masrtech.universities'

    name = fields.Char(string="name")
    university_name_ar = fields.Char(string="الاسم")
    faculty = fields.One2many('masrtech.faculty', 'university_id', string='colleges')

    def action_masrtech_colleges(self):
        return {
            'name': 'colleges',
            'domain': [('university_id.name', '=', self.name)],
            'view_type': 'form',
            'res_model': 'masrtech.faculty',
            'view_mode': 'kanban,tree,form',
            'type': 'ir.actions.act_window',
        }


class MasrtechuFaculty(models.Model):
    _name = 'masrtech.faculty'

    name = fields.Char(string="name")
    university_id = fields.Many2one('masrtech.universities', string="University")
    masrtech_staff = fields.One2many('op.faculty', 'staff_faculty', string='Staff')
    masrtech_course = fields.One2many('op.course', 'course_faculty', string='Course')
    masrtech_department = fields.One2many('op.department', 'department_faculty', string='department')
    masrtech_subject = fields.One2many('op.subject', 'subject_faculty', string='Subjects')
    masrtech_classroom = fields.One2many('op.classroom', 'classroom_faculty', string='Class Rooms')
    masrtech_activity_type = fields.One2many('op.activity.type', 'activity_type_faculty', string='Activity Types')

    def action_masrtech_type(self):
        self.send_data_to_type()
        return {
            'name': self.name,
            'domain': [],
            'view_type': 'form',
            'res_model': 'masrtech.type',
            'view_mode': 'kanban,tree,form',
            'type': 'ir.actions.act_window',
            # 'context': {'default_faculty': self.id},
        }

    def send_data_to_type(self):
        source_records = self.env['masrtech.type'].search([])
        for source_record in source_records:
            source_record.faculty = self.id


class MasrtechType(models.Model):
    _name = 'masrtech.type'

    name = fields.Char(string="name")
    faculty = fields.Many2one('masrtech.faculty', string="faculty")
    university = fields.Many2one('masrtech.universities', related='faculty.university_id', string="University")

    def action_masrtech_dep(self):
        if self.name == 'Departments':
            return {
                'name': 'Departments',
                'domain': [('university', '=', self.university.id), ('department_faculty', '=', self.faculty.id)],
                'view_type': 'form',
                'res_model': 'op.department',
                'view_mode': 'kanban,tree,form',
                'type': 'ir.actions.act_window',
                # 'context': {'default_faculty': self.id},
            }
        elif self.name == 'Staff':
            return {
                'name': 'Staff',
                'domain': [('university', '=', self.university.id)],
                'view_type': 'form',
                'res_model': 'op.faculty',
                'view_mode': 'kanban,tree,form',
                'type': 'ir.actions.act_window',
                # 'context': {'default_faculty': self.id},
            }

        elif self.name == 'College':
            return {
                'name': 'Staff',
                # 'domain': [('name', '=', self.faculty.name)],
                'view_type': 'form',
                'res_model': 'masrtech.faculty',
                'view_mode': 'form',
                'type': 'ir.actions.act_window',
                'res_id': self.faculty.id,

            }
