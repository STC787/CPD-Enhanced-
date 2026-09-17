from odoo import api, models, fields


class MasrtechStudentPortfolio(models.Model):
    _name = 'masrtech.student.portfolio'
    _rec_name = 'student_name'

    student_name = fields.Many2one('op.student', string='Student')
    student_id = fields.Char(string='Student ID', related='student_name.student_id', readonly=False)
    gender = fields.Selection([
        ('m', 'Male'),
        ('f', 'Female'),
    ], 'Gender', default='m', related='student_name.gender', readonly=False)
    birth_date = fields.Date(string='Birth Date', related='student_name.birth_date', readonly=False)
    email = fields.Char(string='Email', related='student_name.email', readonly=False)
    mobile = fields.Char(string='Mobile', related='student_name.mobile', readonly=False)
    university = fields.Many2one('masrtech.universities', string='University', related='student_name.university',
                                 readonly=False)
    faculty = fields.Many2one('masrtech.faculty', string='College', related='student_name.faculty', readonly=False)
    department = fields.Many2one('op.department', string='Department', related='student_name.department',
                                 readonly=False)
    semester = fields.Integer(string='Current Semester', related='student_name.semester', readonly=False)
    gpa = fields.Float(string='GPA', related='student_name.gpa', readonly=False)
    clubs = fields.Text(string='Clubs', related='student_name.clubs', readonly=False)
    graduation_date = fields.Date(string='Graduation Date', related='student_name.graduation_date', readonly=False)
    student_semester = fields.One2many('masrtech.student.semester', 'student_portfolio')
    course_name = fields.Char(string='Course Name')
    academic_supervisor = fields.Char(string='Academic Supervisor')
    level = fields.Selection(
        [('one', 'الفرقة الاولي'), ('two', 'الفرقة الثانية'), ('three', 'الفرقة الثالثة'), ('four', 'الفرقة الرابعة')],
        string='Level')
    program_coordinator = fields.Char(string='منسق البرنامج')
    training_supervisor = fields.Char(string='مشرف التدريب')

    student_practical_study = fields.One2many('masrtech.practical.study', 'student_portfolio')
    program_coordinator_practical = fields.Char(string='منسق البرنامج')
    academic_year_practical = fields.Char(string='Academic Year')
    college_agent = fields.Char(string='وكيل الكلية لشئون التعليم والطلاب')
    college_dean_health = fields.Char(string='عميد كلية العلوم الصحية')

    student_training_summery = fields.One2many('masrtech.training.summer', 'student_portfolio')
    program_coordinator_training = fields.Char(string='منسق البرنامج')
    summer_training_supervisor = fields.Char(string='مشرف التدريب')
    academic_year_training = fields.Char(string='Academic Year')
    academic_supervisor_training = fields.Char(string='Academic Supervisor')
    level_training = fields.Selection(
        [('one', 'الفرقة الاولي'), ('two', 'الفرقة الثانية'), ('three', 'الفرقة الثالثة'), ('four', 'الفرقة الرابعة')],
        string='Level')
    student_soft_skills = fields.One2many('masrtech.soft.skills', 'student_portfolio')
    academic_year_soft_skills = fields.Char(string='Academic Year')
    academic_supervisor_soft_skills = fields.Char(string='Academic Supervisor')
    level_soft_skills = fields.Selection(
        [('one', 'الفرقة الاولي'), ('two', 'الفرقة الثانية'), ('three', 'الفرقة الثالثة'), ('four', 'الفرقة الرابعة')],
        string='Level')
    program_coordinator_soft = fields.Char(string='منسق البرنامج')
    training_supervisor_soft = fields.Char(string='مشرف التدريب')
    college_agent_soft = fields.Char(string='وكيل الكلية لشئون التعليم والطلاب')
    college_dean_soft = fields.Char(string='عميد كلية')

    image = fields.Binary(string='Image')

    @api.onchange('student_name')
    def add_lines_student_summer_training(self):
        new_records = self.env['masrtech.training.summer']
        for i in range(1, 9):  # Adjusted range to create 18 records
            values = {
                'week': f"{i}st",  # Use f-string to include the value of i
            }
            new_records += self.env['masrtech.training.summer'].new(values)

        self.student_training_summery = new_records

    @api.onchange('student_name')
    def add_lines_student_soft_skills(self):
        new_records = self.env['masrtech.soft.skills']
        for i in range(1, 18):  # Adjusted range to create 18 records
            values = {
                'week': f"{i}st",  # Use f-string to include the value of i
            }
            new_records += self.env['masrtech.soft.skills'].new(values)

        self.student_soft_skills = new_records

    @api.onchange('student_name')
    def add_lines_student_semester(self):
        new_records = self.env['masrtech.student.semester']
        for i in range(1, 18):  # Adjusted range to create 18 records
            values = {
                'week': f"{i}st",  # Use f-string to include the value of i
            }
            new_records += self.env['masrtech.student.semester'].new(values)

        self.student_semester = new_records


class MasrtechStudentSemester(models.Model):
    _name = 'masrtech.student.semester'

    course_name = fields.Char(string='Course Name')
    academic_supervisor = fields.Char(string='Academic Supervisor')
    level = fields.Selection(
        [('one', 'الفرقة الاولي'), ('two', 'الفرقة الثانية'), ('three', 'الفرقة الثالثة'), ('four', 'الفرقة الرابعة')],
        string='Level')
    student_portfolio = fields.Many2one('masrtech.student.portfolio')
    semester_type = fields.One2many('masrtech.student.semester.type', 'student_type')
    week = fields.Char(string='Week')
    practical_title = fields.Char(string='Practical title')
    practical_training = fields.Char(string='Practical Training')
    institute = fields.Char(string='Institute')
    competence = fields.Char(string='Competence')


class MasrtechStudentSemesterType(models.Model):
    _name = 'masrtech.student.semester.type'

    course_name = fields.Char(string='Course Name')
    week = fields.Char(string='Week')
    practical_title = fields.Char(string='Practical title')
    practical_training = fields.Char(string='Practical Training')
    institute = fields.Char(string='Institute')
    competence = fields.Char(string='Competence')
    academic_supervisor = fields.Char(string='Academic Supervisor')
    level = fields.Selection(
        [('one', 'الفرقة الاولي'), ('two', 'الفرقة الثانية'), ('three', 'الفرقة الثالثة'), ('four', 'الفرقة الرابعة')],
        string='Level')
    student_portfolio = fields.Many2one('masrtech.student.portfolio')
    student_type = fields.Many2one('masrtech.student.semester')
    student_name = fields.Many2one('op.student', related='student_portfolio.student_name')


class MasrtechPracticalStudy(models.Model):
    _name = 'masrtech.practical.study'

    course_code = fields.Char(string='Course Code')
    course_name = fields.Char(string='Course Name')
    practical_topics = fields.Char(string='Practical Topics')
    practical_location = fields.Char(string='Practical Location')
    student_portfolio = fields.Many2one('masrtech.student.portfolio')


class MasrtechTrainingSummer(models.Model):
    _name = 'masrtech.training.summer'

    week = fields.Char(string='Week')
    practical_title = fields.Char(string='Practical title')
    practical_training = fields.Char(string='Practical Training')
    institute = fields.Char(string='Institute')
    competence = fields.Char(string='Competence')
    student_portfolio = fields.Many2one('masrtech.student.portfolio')


class MasrtechSoftSkills(models.Model):
    _name = 'masrtech.soft.skills'

    week = fields.Char(string='Week')
    soft_skill = fields.Char(string='Soft Skills')
    institute = fields.Char(string='Institute')
    competence = fields.Char(string='Competence')
    supervisor = fields.Char(string='Supervisor')
    level = fields.Selection(
        [('one', 'الفرقة الاولي'), ('two', 'الفرقة الثانية'), ('three', 'الفرقة الثالثة'), ('four', 'الفرقة الرابعة')],
        string='Level')
    student_portfolio = fields.Many2one('masrtech.student.portfolio')
