from odoo import _, api, models, fields
import qrcode
from io import BytesIO
import base64
from odoo.exceptions import UserError, ValidationError
import pandas as pd

import base64
import os
import smtplib
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.utils import secure_filename


class InheritMasrtechStudent(models.Model):
    _inherit = 'op.student'

    training_hours = fields.Integer(string='Training')
    student_id_ref = fields.Many2one('discuss.channel')
    student_id_reff = fields.Many2one('discuss.channel')
    document_ids = fields.Many2many(
        'ir.attachment',
        string='All Documents'
    )
    faculty_id = fields.Char('Faculty Id')
    student_id = fields.Char(string='Student ID')
    street = fields.Char(string='Street')
    city = fields.Char(string='City')
    all_levels = fields.Boolean(string="Access All Levels", default=False,
                                help="Allow student to see trainings from all levels")
    # nationality = fields.Char(string='Nationality')
    country = fields.Char(string='Country')
    state = fields.Char(string='state')
    parent_name = fields.Char(string='Parent Name')
    parent_contact = fields.Char(string='Parent Contact')
    semester = fields.Integer(string='Current Semester')
    gpa = fields.Float(string='GPA')
    clubs = fields.Text(string='Clubs')
    graduation_date = fields.Date(string='Graduation Date')
    university = fields.Many2one('masrtech.universities', string='University')
    faculty = fields.Many2one('masrtech.faculty', string='College')
    department = fields.Many2one('op.department', string='Department')
    image_1920 = fields.Binary()
    student_portfolio = fields.Many2one('masrtech.student.portfolio')
    portfolio = fields.Boolean()
    training = fields.Boolean()
    related_id = fields.Integer()
    related = fields.Integer()
    count_training_recommendation = fields.Integer(compute='_compute_training_count', string='Training Recommendations')
    count_job_opportunity_recommendation = fields.Integer(compute='_compute_job_opportunity_count',
                                                          string='Training Recommendations')
    count_project_recommendation = fields.Integer(compute='_compute_project_count', string='Projects Recommendations')
    count_accepting_student = fields.Integer(compute='_compute_accepting_student', string='Accepting')

    training_recommendation = fields.Many2one('martech.training.recommendation')
    project = fields.Many2one('masrtech.project')
    user_id = fields.Many2one('res.users', string="user", readonly=False)
    birth_date = fields.Date(string='Birth Date', required=False)

    @api.constrains('birth_date')
    def _check_birthdate(self):
        for record in self:
            if record.birth_date and record.birth_date > fields.Date.today():
                raise ValidationError(_('Birth Date cannot be greater than today.'))
    training_course_id = fields.Many2one('registrar.partner.training.table', string='Training Course')
    training_course_idd = fields.Many2one('registrar.partner.training.table.category', string='Training Course')
    training_course = fields.Many2one('registrar.partner.training.table.category', string='Courses')
    gender = fields.Selection([
        ('m', 'Male'),
        ('f', 'Female'),
    ], 'Gender', required=False, default='m')

    level = fields.Selection(
        [('one', 'الفرقة الاولي'), ('two', 'الفرقة الثانية'), ('three', 'الفرقة الثالثة'), ('four', 'الفرقة الرابعة')],
        string='Level')
    job_name = fields.Char(string='Student job title')
    soft_skills = fields.Text(string='Soft Skills')
    trainings = fields.Text(string='Trainings')
    attachments = fields.One2many('ir.attachment', 'res_id', string='Attachments')

    certificates_binary = fields.Binary(string="Certificates")
    graduated_skills = fields.One2many('graduated.skills.table', 'relation_id')
    student_skills = fields.One2many('student.skills.table', 'relation_id')
    quiz_ids = fields.One2many('courses.table', 'student_id')
    academic_track = fields.Selection([
        ('student', 'Student'),
        ('graduated', 'Graduated'),
    ], 'Academic track', default='student')
    qr_code = fields.Binary(string="QR Code", attachment=True)
    duplicate_check = fields.Boolean(default=False)
    receiver_email = fields.Boolean(default=False)
    check_qr = fields.Boolean(default=False)
    first_name = fields.Char('First Name', translate=True, required=False)
    middle_name = fields.Char('Middle Name', size=128)
    last_name = fields.Char('Last Name', size=128)
    student_certification = fields.Many2many('student.certification', 'student_id')
    courses_ids = fields.Many2many('op.course')
    courses_id = fields.Many2many(
        'masrtech.register.partner',
        domain=[('is_course', '=', True)]
    )
    id_attachment = fields.Binary(string="ID Attachment")
    is_complete = fields.Boolean(default=False)
    def calc_is_complete(self):
        for rec in self.env['op.student'].search([]):
            if rec.training_course_idd:
                student = self.env['training.registration'].search([('student_namee', '=', rec.id)],limit=1)
                if student.registration_status == 'confirmed':
                    rec.is_complete=True
                else:
                    rec.is_complete = False
            else:
                rec.is_complete = False

    @api.onchange('first_name', 'middle_name', 'last_name')
    def _onchange_name(self):
        pass

    def set_duplicate_check(self):
        for rec in self:
            students = self.env['op.student'].search([])
            students.write({'duplicate_check': False})  # Reset duplicate check flag

            for student in students:
                student.duplicate_check = False

            for i, student in enumerate(students):
                for j, other_student in enumerate(students):
                    if i != j and student.student_id == other_student.student_id:
                        if student.student_id:
                            students_to_update = self.env['op.student'].search(
                                [('student_id', '=', student.student_id)])
                            students_to_update.write({'duplicate_check': True})

    def generate_qr_code(self):
        for record in self:
            students = self.env['op.student'].search([])
            for student in students:
                qr_data = f"Name: {student.name},student_id: {student.student_id}"

                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(qr_data)
                qr.make(fit=True)

                img = qr.make_image(fill_color="black", back_color="white")
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                qr_image = base64.b64encode(buffer.getvalue())
                buffer.close()

                student.qr_code = qr_image
                student.check_qr = True

    def send_qr_code_email(self):
        for rec in self:

            if not rec.qr_code:
                raise UserError("QR Code is not generated for this record.")
            attachment = {
                'name': 'QR_Code.png',
                'datas': rec.qr_code,
                'res_model': rec._name,
                'res_id': rec.id,
                'type': 'binary',
                'mimetype': 'image/png',
            }
            attachment_id = self.env['ir.attachment'].create(attachment)

            mail_values = {
                'subject': "Your QR Code",
                'body_html': "<p>اهلا بيك في ملتقي التوظيف الاول لجامعة برج العرب التكنولوجية</p><p>Find the QR Code tickect attached .</p>",
                'email_to': rec.email,
                'attachment_ids': [(4, attachment_id.id)],
            }
            mail = self.env['mail.mail'].create(mail_values)
            mail.send()
            rec.receiver_email = True

    file = fields.Binary(string="Upload File", help="Upload the Excel file")
    filename = fields.Char(string="Filename")

    def import_students(self):
        # Decode the uploaded file
        if not self.file:
            raise ValueError("Please upload a file before importing.")

        if not self.filename:
            raise ValueError("Uploaded file has no filename.")

        # Reject path separators / traversal attempts and keep the basename only
        filename = secure_filename(os.path.basename(str(self.filename)))

        # Only allow Excel workbooks
        allowed_extensions = ('.xlsx', '.xls', '.xlsm')
        if not filename.lower().endswith(allowed_extensions):
            raise ValueError("Only Excel files (.xlsx, .xls, .xlsm) are allowed.")

        file_data = base64.b64decode(self.file)
        file_path = os.path.join('/tmp', filename)

        # Save file temporarily
        with open(file_path, "wb") as f:
            f.write(file_data)

        # Read the Excel file using pandas
        try:
            df = pd.read_excel(file_path)
        except Exception as e:
            raise ValueError("Invalid Excel file format. Error: {}".format(e))

        # Validate columns
        required_columns = {'Name', 'Student ID', 'Mobile', 'Email'}
        if not required_columns.issubset(df.columns):
            raise ValueError("Excel file must contain the following columns: {}".format(", ".join(required_columns)))

        # Create student records
        for _, row in df.iterrows():
            self.env['op.student'].create({
                'name': row['Name'],
                'student_id': row['Student ID'],
                'mobile': row['Mobile'],
                'email': row['Email'],
            })

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    # def send_email_with_qr_code(self):
    #     for record in self:
    #         if not record.qr_code:
    #             raise ValueError("Please generate the QR Code before sending the email.")
    #
    #         email_template = self.env.ref('masrtech.email_template_with_qr_code')
    #         attachment_id = self.env['ir.attachment'].create({
    #             'name': f"QR_{record.name}.png",
    #             'type': 'binary',
    #             'datas': record.qr_code,
    #             'res_model': 'op.student',
    #             'res_id': record.id,
    #             'mimetype': 'image/png',
    #         })
    #         email_template.attachment_ids = [(6, 0, [attachment_id.id])]
    #         email_template.send_mail(record.id, force_send=True)

    def _get_smtp_credentials(self):
        icp = self.env['ir.config_parameter'].sudo()
        sender_email = icp.get_param('masrtech.smtp_user', '')
        sender_password = icp.get_param('masrtech.smtp_password', '')
        if not sender_email or not sender_password:
            return False, False
        return sender_email, sender_password

    def send_custom_email(self):
        students = self.env['op.student'].search([])
        sender_email, sender_password = self._get_smtp_credentials()
        if not sender_email:
            raise UserError(
                "SMTP credentials are not configured. Please set the "
                "'masrtech.smtp_user' and 'masrtech.smtp_password' system parameters."
            )
        for student in students:
            recipient_email = self.email
            subject = "Your QR Code"
            body = ("اهلا بيك في ملتقي التوظيف الاول لجامعة برج العرب التكنولوجية<br>"
                    "Below is your QR Code ticket:")

            # Retrieve binary content and filename
            binary_content = self.qr_code
            filename = "qr_code.png"

            if not binary_content:
                return "No attachment provided"
            try:
                file_content = base64.b64decode(binary_content)
            except Exception as decode_error:
                return f"Failed to decode QR code binary content: {str(decode_error)}"

            # Send the email
            result = self.send_email_with_inline_image(
                sender_email, sender_password, recipient_email, subject, body, filename, file_content
            )
            return result

    def send_email_with_inline_image(self, sender_email, sender_password, recipient_email, subject, body, filename,
                                     file_content):
        import logging
        _logger = logging.getLogger(__name__)
        try:
            smtp_server = "smtp.gmail.com"
            port = 587  # TLS port

            # Create the email
            msg = MIMEMultipart("related")
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject

            # HTML body with the embedded image
            html_body = f"""
            <html>
            <body>
                <p>{body}</p>
                <img src="cid:{filename}" alt="QR Code">
            </body>
            </html>
            """

            # Attach the HTML body
            msg.attach(MIMEText(html_body, 'html'))

            # Attach the image as an inline image
            img = MIMEImage(file_content, name=filename)
            img.add_header('Content-ID', f'<{filename}>')  # Reference ID for the image
            img.add_header('Content-Disposition', 'inline', filename=filename)
            msg.attach(img)

            # Connect to the SMTP server
            server = smtplib.SMTP(smtp_server, port)
            server.starttls()  # Enable TLS encryption
            server.login(sender_email, sender_password)

            # Send the email
            server.sendmail(sender_email, recipient_email, msg.as_string())
            server.quit()
            self.receiver_email = True  # Update the status on successful email
            return "Email sent successfully"
        except smtplib.SMTPAuthenticationError as auth_error:
            _logger.error("SMTP authentication failed for sender %s", sender_email)
            return "Authentication failed. Please verify SMTP credentials."
        except smtplib.SMTPException as smtp_error:
            _logger.error("SMTP error: %s", str(smtp_error))
            return "SMTP error occurred"
        except Exception as general_error:
            _logger.error("Failed to send email: %s", str(general_error))
            return "Failed to send email"

    def go_to_student_Portfolio(self):
        self.check_student_portfolio()
        if self.portfolio == True:
            return {
                'name': 'Student Portfolio',
                'domain': [],
                'view_type': 'form',
                'res_model': 'masrtech.student.portfolio',
                'view_id': False,
                'view_mode': 'form',
                'type': 'ir.actions.act_window',
                'res_id': self.related_id,

            }
        elif self.portfolio == False:
            return {
                'name': 'Student Portfolio',
                'domain': [],
                'view_type': 'form',
                'res_model': 'masrtech.student.portfolio',
                'view_id': False,
                'view_mode': 'form',
                'type': 'ir.actions.act_window',
            }

    def check_student_portfolio(self):
        records = self.env['masrtech.student.portfolio'].search([])
        for rec in records:
            if self.id == rec.student_name.id:
                self.portfolio = True
                self.related_id = rec.id

    def get_training(self):
        return {
            'name': 'Training',
            'domain': [],
            'view_type': 'form',
            'res_model': 'masrtech.student.training',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    def get_accepting_student(self):
        return {
            'name': 'Accepting',
            'domain': [('student_name', '=', self.id)],
            'view_type': 'form',
            'res_model': 'masrtech.student.accept',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            'context': {
                'group_by': 'type',
            },
        }

    def _compute_accepting_student(self):
        for record in self:
            count = self.env['masrtech.student.accept'].search_count([('student_name', '=', record.id)])
            record.count_accepting_student = count

    def go_to_training_recommendation(self):
        # self.get_student_id()
        # if self.training == True:
        return {
            'name': 'Training Recommendations',
            'domain': [('student_name', '=', self.id)],
            'view_type': 'form',
            'res_model': 'masrtech.training.recommendation',
            'view_id': False,
            'view_mode': 'kanban,form',
            'type': 'ir.actions.act_window',
            # 'res_id': self.related,
        }

        # elif self.training == False

    def _compute_training_count(self):
        for record in self:
            count = self.env['masrtech.training.recommendation'].search_count([('student_name', '=', record.id)])
            record.count_training_recommendation = count

    def go_to_job_opportunity_recommendation(self):
        # self.get_student_id()
        # if self.training == True:
        return {
            'name': 'Job Opportunities Recommendations',
            'domain': [('student_name', '=', self.id)],
            'view_type': 'form',
            'res_model': 'masrtech.job.opportunity.recommendation',
            'view_id': False,
            'view_mode': 'kanban,form',
            'type': 'ir.actions.act_window',
            # 'res_id': self.related,
        }

    def _compute_job_opportunity_count(self):
        for record in self:
            count = self.env['masrtech.job.opportunity.recommendation'].search_count([('student_name', '=', record.id)])
            record.count_job_opportunity_recommendation = count

    def go_to_project_recommendation(self):
        # self.get_student_id()
        # if self.training == True:
        return {
            'name': 'Projects Recommendations',
            'domain': [('student_name', '=', self.id)],
            'view_type': 'form',
            'res_model': 'masrtech.project.recommendation',
            'view_id': False,
            'view_mode': 'kanban,form',
            'type': 'ir.actions.act_window',
            # 'res_id': self.related,
        }

    def _compute_project_count(self):
        for record in self:
            count = self.env['masrtech.project.recommendation'].search_count([('student_name', '=', record.id)])
            record.count_project_recommendation = count


class MasrtechTraining(models.Model):
    _name = 'masrtech.student.training'

    student_id = fields.Many2one('op.student', 'Student', required=True)
    training_hours = fields.Integer(string='Training')


class graduatedSkillsTable(models.Model):
    _name = 'graduated.skills.table'

    graduated_title = fields.Char(string='JOP TITLE')
    graduated_qualification = fields.Char(string='Qualification')
    graduated_experience = fields.Char(string='Experience')
    graduated_skills = fields.Char(string='Skills')
    work_locations = fields.Char(string='Work Locations')
    relation_id = fields.Many2one('op.student')


class studentSkillsTable(models.Model):
    _name = 'student.skills.table'

    student_title = fields.Char(string='JOP TITLE')
    student_education = fields.Char(string='Education')
    student_skills = fields.Char(string='Skills')
    student_soft_skills = fields.Char(string='Soft Skills')
    relation_id = fields.Many2one('op.student')


class CoursesTable(models.Model):
    _name = 'courses.table'

    exam_id = fields.Many2one('survey.survey', string='quiz')
    faculty_id = fields.Many2one('op.faculty')
    training_course_id = fields.Many2one('registrar.partner.training.table', string='Training Course')
    opened_quiz = fields.Boolean(string='Opened Quiz', default=False)
    student_id = fields.Many2one('op.student')

