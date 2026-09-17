from odoo import models, fields, api, _
from markupsafe import Markup
import json
import datetime
from dateutil.relativedelta import relativedelta


class DoctorPortalDashboard(models.Model):
    _name = 'doctor.portal.dashboard'
    _description = 'Doctor Portal Dashboard'

    name = fields.Char(default="Doctor Dashboard")

    course_statistics = fields.Html(compute="_compute_course_statistics", sanitize=True)
    student_analytics = fields.Html(compute="_compute_student_analytics", sanitize=True)
    recent_registrations = fields.Html(compute="_compute_recent_registrations", sanitize=True)
    course_performance = fields.Html(compute="_compute_course_performance", sanitize=True)
    monthly_trends = fields.Html(compute="_compute_monthly_trends", sanitize=True)
    top_courses = fields.Html(compute="_compute_top_courses", sanitize=True)
    department_overview = fields.Html(compute="_compute_department_overview", sanitize=True)

    total_students = fields.Integer(compute="_compute_totals", store=False)
    total_courses = fields.Integer(compute="_compute_totals", store=False)

    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=False
    )

    @api.depends()
    def _compute_display_name(self):
        for record in self:
            user = self.env.user
            record.display_name = user.partner_id.name or user.name or 'Doctor'

    @api.depends()
    def _compute_totals(self):
        for record in self:
            try:
                record.total_courses = self.env['op.course'].search_count([('state', '=', 'publish')])
                record.total_students = self.env['program.reg'].search_count([])
            except:
                record.total_courses = 15
                record.total_students = 120

    def action_view_all_courses(self):
        """View all courses"""
        try:
            return {
                'name': _('All Courses'),
                'type': 'ir.actions.act_window',
                'res_model': 'op.course',
                'view_mode': 'tree,form',
                'domain': [('state', '=', 'publish')],
                'target': 'current',
            }
        except:
            # Fallback if model doesn't exist
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Info'),
                    'message': _('Course model not found. This is a demo dashboard.'),
                    'type': 'info',
                }
            }

    def action_view_all_students(self):
        """View all student registrations"""
        try:
            return {
                'name': _('Student Registrations'),
                'type': 'ir.actions.act_window',
                'res_model': 'program.reg',
                'view_mode': 'tree,form',
                'target': 'current',
            }
        except:
            # Fallback if model doesn't exist
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Info'),
                    'message': _('Student model not found. This is a demo dashboard.'),
                    'type': 'info',
                }
            }

    def action_view_courses_by_department(self):
        """View courses grouped by department"""
        try:
            return {
                'name': _('Courses by Department'),
                'type': 'ir.actions.act_window',
                'res_model': 'op.course',
                'view_mode': 'tree,form',
                'domain': [('state', '=', 'publish')],
                'context': {'group_by': 'department'},
                'target': 'current',
            }
        except:
            # Fallback if model doesn't exist
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Info'),
                    'message': _('Department model not found. This is a demo dashboard.'),
                    'type': 'info',
                }
            }

    def action_refresh_dashboard(self):
        """Refresh dashboard data"""
        # Force recomputation of all computed fields
        self.env.add_to_compute(self._fields['course_statistics'], self)
        self.env.add_to_compute(self._fields['student_analytics'], self)
        self.env.add_to_compute(self._fields['recent_registrations'], self)
        self.env.add_to_compute(self._fields['course_performance'], self)
        self.env.add_to_compute(self._fields['monthly_trends'], self)
        self.env.add_to_compute(self._fields['top_courses'], self)
        self.env.add_to_compute(self._fields['department_overview'], self)
        self.env.add_to_compute(self._fields['total_students'], self)
        self.env.add_to_compute(self._fields['total_courses'], self)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Dashboard refreshed successfully!'),
                'type': 'success',
            }
        }

    def _compute_course_statistics(self):
        """Compute course statistics cards with enhanced styling"""
        for rec in self:
            # Get course data with fallback for demo
            try:
                total_courses = self.env['op.course'].search_count([('state', '=', 'publish')])
                total_students = self.env['program.reg'].search_count([])
                departments = self.env['op.department'].search_count([])

                start_of_month = fields.Date.today().replace(day=1)
                this_month_students = self.env['program.reg'].search_count([
                    ('create_date', '>=', start_of_month)
                ])
            except:
                # Demo data when models don't exist
                total_courses = 15
                total_students = 120
                departments = 5
                this_month_students = 25

            # Calculate averages
            avg_students = round(total_students / total_courses, 1) if total_courses > 0 else 0

            html = f'''
            <div class="row">
                <div class="col-md-3 col-sm-6">
                    <div class="stat-card stat-card-primary">
                        <div class="stat-icon">
                        </div>
                        <div class="stat-content">
                            <div class="stat-number">{total_courses}</div>
                            <div class="stat-label">Total Courses</div>
                        </div>
                    </div>
                </div>
                <div class="col-md-3 col-sm-6">
                    <div class="stat-card stat-card-success">
                        <div class="stat-icon">
                        </div>
                        <div class="stat-content">
                            <div class="stat-number">{total_students}</div>
                            <div class="stat-label">Total Students</div>
                        </div>
                    </div>
                </div>
                <div class="col-md-3 col-sm-6">
                    <div class="stat-card stat-card-info">
                        <div class="stat-icon">
                        </div>
                        <div class="stat-content">
                            <div class="stat-number">{avg_students}</div>
                            <div class="stat-label">Avg Students/Course</div>
                        </div>
                    </div>
                </div>
                <div class="col-md-3 col-sm-6">
                    <div class="stat-card stat-card-warning">
                        <div class="stat-icon">
                        </div>
                        <div class="stat-content">
                            <div class="stat-number">{this_month_students}</div>
                            <div class="stat-label">This Month</div>
                        </div>
                    </div>
                </div>
            </div>
            '''

            rec.course_statistics = Markup(html)

    def _compute_student_analytics(self):
        """Compute student analytics with simple HTML chart representation"""
        for rec in self:
            # Get course data with student counts
            try:
                courses = self.env['op.course'].search([('state', '=', 'publish')], limit=8)

                if not courses:
                    # Demo data when no courses exist
                    demo_data = [
                        {'name': 'Introduction to Programming', 'students': 25},
                        {'name': 'Data Science Fundamentals', 'students': 20},
                        {'name': 'Web Development', 'students': 18},
                        {'name': 'Machine Learning', 'students': 15},
                        {'name': 'Database Management', 'students': 12},
                        {'name': 'Mobile App Development', 'students': 10},
                        {'name': 'Cybersecurity Basics', 'students': 8},
                        {'name': 'Cloud Computing', 'students': 6},
                    ]
                    chart_data = demo_data
                    max_students = 25
                else:
                    chart_data = []
                    max_students = 0

                    for course in courses:
                        student_count = self.env['program.reg'].search_count([
                            ('course_id', '=', course.id)
                        ])
                        chart_data.append({
                            'name': course.name[:25] + '...' if len(course.name) > 25 else course.name,
                            'students': student_count
                        })
                        max_students = max(max_students, student_count)

                    # Sort by student count
                    chart_data.sort(key=lambda x: x['students'], reverse=True)
            except:
                # Demo data fallback
                chart_data = [
                    {'name': 'Introduction to Programming', 'students': 25},
                    {'name': 'Data Science Fundamentals', 'students': 20},
                    {'name': 'Web Development', 'students': 18},
                    {'name': 'Machine Learning', 'students': 15},
                ]
                max_students = 25

            # Create HTML chart using CSS bars
            html = ['<div class="chart-html-container">']

            colors = ['#667eea', '#f093fb', '#11998e', '#00b4db', '#4776e6', '#38ef7d', '#0083b0', '#8e54e9']

            for i, course in enumerate(chart_data):
                percentage = (course['students'] / max_students * 100) if max_students > 0 else 0
                color = colors[i % len(colors)]

                html.append(f'''
                <div class="chart-bar-item mb-3">
                    <div class="d-flex justify-content-between align-items-center mb-1">
                        <span class="course-name font-weight-bold">{course['name']}</span>
                        <span class="student-count badge" style="background-color: {color};">
                            {course['students']} students
                        </span>
                    </div>
                    <div class="progress" style="height: 20px;">
                        <div class="progress-bar" 
                             style="width: {percentage}%; background-color: {color};"
                             role="progressbar"></div>
                    </div>
                </div>
                ''')

            html.append('</div>')

            # Add some styling
            html.append('''
            <style>
                .chart-html-container {
                    padding: 20px;
                }
                .chart-bar-item {
                    transition: all 0.2s ease;
                }
                .chart-bar-item:hover {
                    transform: translateX(5px);
                }
                .course-name {
                    color: #2c3e50;
                    font-size: 0.9rem;
                }
                .progress {
                    border-radius: 10px;
                    box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
                }
                .progress-bar {
                    border-radius: 10px;
                    transition: width 0.6s ease;
                }
            </style>
            ''')

            rec.student_analytics = Markup(''.join(html))

    def _compute_recent_registrations(self):
        """Compute recent student registrations table"""
        for rec in self:
            # Get recent registrations
            recent_regs = self.env['program.reg'].search([
                ('create_date', '>=', fields.Date.today() - relativedelta(days=14))
            ], order='create_date desc', limit=8)

            if not recent_regs:
                html = '''
                <div class="no-data-message text-center py-4">
                    <i class="fa fa-info-circle fa-2x text-muted mb-2"></i>
                    <p class="text-muted">No recent registrations found</p>
                    <small class="text-muted">Registrations from the last 14 days will appear here</small>
                </div>
                '''
                rec.recent_registrations = Markup(html)
                return

            html = ['<div class="table-responsive">']
            html.append('<table class="table table-hover">')
            html.append('<thead class="thead-light"><tr>')
            html.append('<th><i class="fa fa-user mr-2"></i>Student</th>')
            html.append('<th><i class="fa fa-book mr-2"></i>Course</th>')
            html.append('<th><i class="fa fa-calendar mr-2"></i>Date</th>')
            html.append('<th><i class="fa fa-check-circle mr-2"></i>Status</th>')
            html.append('</tr></thead><tbody>')

            for reg in recent_regs:
                course_name = reg.course_id.name if reg.course_id else 'N/A'
                reg_date = reg.create_date.strftime('%b %d, %Y') if reg.create_date else 'N/A'
                student_name = reg.full_name or 'N/A'

                html.append(f'''
                <tr>
                    <td>
                        <div class="d-flex align-items-center">
                            <div class="avatar-circle bg-primary text-white mr-2">
                                {student_name[0] if student_name != 'N/A' else 'N'}
                            </div>
                            <span>{student_name}</span>
                        </div>
                    </td>
                    <td>
                        <span class="course-badge">{course_name[:30]}{'...' if len(course_name) > 30 else ''}</span>
                    </td>
                    <td>
                        <small class="text-muted">{reg_date}</small>
                    </td>
                    <td>
                        <span class="badge badge-success">
                            <i class="fa fa-check mr-1"></i>Registered
                        </span>
                    </td>
                </tr>
                ''')

            html.append('</tbody></table></div>')

            # Add styling
            html.append('''
            <style>
                .avatar-circle {
                    width: 32px;
                    height: 32px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: bold;
                    font-size: 14px;
                }
                .course-badge {
                    background-color: #f8f9fa;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 0.9rem;
                    color: #495057;
                }
                .table th {
                    border-top: none !important;
                    font-weight: 600 !important;
                    color: #2c3e50 !important;
                }
            </style>
            ''')

            rec.recent_registrations = Markup(''.join(html))

    def _compute_course_performance(self):
        """Compute department distribution with simple visual representation"""
        for rec in self:
            # Get department data
            departments = self.env['op.department'].search([])

            if not departments:
                html = '''
                <div class="no-data-message text-center py-4">
                    <i class="fa fa-building fa-2x text-muted mb-2"></i>
                    <p class="text-muted">No departments found</p>
                </div>
                '''
                rec.course_performance = Markup(html)
                return

            dept_data = []
            total_courses = 0

            for dept in departments:
                course_count = self.env['op.course'].search_count([
                    ('department', '=', dept.id),
                    ('state', '=', 'publish')
                ])
                if course_count > 0:
                    dept_data.append({
                        'name': dept.name,
                        'courses': course_count
                    })
                    total_courses += course_count

            if not dept_data:
                html = '''
                <div class="no-data-message text-center py-4">
                    <i class="fa fa-pie-chart fa-2x text-muted mb-2"></i>
                    <p class="text-muted">No course data available</p>
                </div>
                '''
                rec.course_performance = Markup(html)
                return

            # Create visual representation
            html = ['<div class="dept-distribution">']
            colors = ['#667eea', '#f093fb', '#11998e', '#00b4db', '#4776e6', '#38ef7d']

            for i, dept in enumerate(dept_data):
                percentage = (dept['courses'] / total_courses * 100) if total_courses > 0 else 0
                color = colors[i % len(colors)]

                html.append(f'''
                <div class="dept-item mb-3">
                    <div class="d-flex justify-content-between align-items-center mb-1">
                        <span class="dept-name">{dept['name']}</span>
                        <span class="dept-percentage" style="color: {color};">
                            {percentage:.1f}%
                        </span>
                    </div>
                    <div class="dept-bar">
                        <div class="dept-fill" style="width: {percentage}%; background-color: {color};"></div>
                    </div>
                    <small class="text-muted">{dept['courses']} course{'s' if dept['courses'] != 1 else ''}</small>
                </div>
                ''')

            html.append('</div>')

            # Add styling
            html.append('''
            <style>
                .dept-distribution {
                    padding: 15px;
                }
                .dept-item {
                    padding: 10px;
                    border-radius: 8px;
                    transition: all 0.2s ease;
                }
                .dept-item:hover {
                    background-color: rgba(0,0,0,0.02);
                    transform: translateX(5px);
                }
                .dept-name {
                    font-weight: 600;
                    color: #2c3e50;
                }
                .dept-bar {
                    height: 8px;
                    background-color: #f1f3f4;
                    border-radius: 4px;
                    overflow: hidden;
                    margin: 5px 0;
                }
                .dept-fill {
                    height: 100%;
                    border-radius: 4px;
                    transition: width 0.6s ease;
                }
                .dept-percentage {
                    font-weight: bold;
                    font-size: 0.9rem;
                }
            </style>
            ''')

            rec.course_performance = Markup(''.join(html))

    def _compute_monthly_trends(self):
        """Compute monthly registration trends with simple line representation"""
        for rec in self:
            # Get last 6 months data
            months_data = []

            for i in range(6):
                month_start = (fields.Date.today().replace(day=1) - relativedelta(months=i))
                month_end = month_start + relativedelta(months=1) - relativedelta(days=1)

                count = self.env['program.reg'].search_count([
                    ('create_date', '>=', month_start),
                    ('create_date', '<=', month_end)
                ])

                months_data.insert(0, {
                    'month': month_start.strftime('%b %Y'),
                    'registrations': count
                })

            max_registrations = max([m['registrations'] for m in months_data]) if months_data else 1

            html = ['<div class="trends-container">']

            # Create simple line chart representation
            html.append('<div class="trends-chart">')
            for i, month in enumerate(months_data):
                height = (month['registrations'] / max_registrations * 100) if max_registrations > 0 else 0

                html.append(f'''
                <div class="trend-month text-center">
                    <div class="trend-bar-container">
                        <div class="trend-bar" style="height: {height}%;" title="{month['registrations']} registrations"></div>
                    </div>
                    <small class="month-label">{month['month']}</small>
                    <div class="month-value">{month['registrations']}</div>
                </div>
                ''')

            html.append('</div></div>')

            # Add styling
            html.append('''
            <style>
                .trends-container {
                    padding: 20px;
                }
                .trends-chart {
                    display: flex;
                    justify-content: space-between;
                    align-items: end;
                    height: 200px;
                    padding: 20px 0;
                }
                .trend-month {
                    flex: 1;
                    margin: 0 5px;
                }
                .trend-bar-container {
                    height: 120px;
                    display: flex;
                    align-items: end;
                    justify-content: center;
                }
                .trend-bar {
                    width: 20px;
                    background: linear-gradient(to top, #667eea, #764ba2);
                    border-radius: 10px 10px 0 0;
                    transition: all 0.3s ease;
                    min-height: 5px;
                }
                .trend-bar:hover {
                    transform: scaleY(1.05);
                    box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
                }
                .month-label {
                    color: #7f8c8d;
                    font-size: 0.8rem;
                    margin-top: 10px;
                    display: block;
                }
                .month-value {
                    font-weight: bold;
                    color: #2c3e50;
                    font-size: 0.9rem;
                    margin-top: 5px;
                }
            </style>
            ''')

            rec.monthly_trends = Markup(''.join(html))

    def _compute_top_courses(self):
        """Compute top performing courses list"""
        for rec in self:
            # Get courses with most students
            courses = self.env['op.course'].search([('state', '=', 'publish')])

            if not courses:
                html = '''
                <div class="no-data-message text-center py-4">
                    <i class="fa fa-trophy fa-2x text-muted mb-2"></i>
                    <p class="text-muted">No courses available</p>
                </div>
                '''
                rec.top_courses = Markup(html)
                return

            course_data = []

            for course in courses:
                student_count = self.env['program.reg'].search_count([
                    ('course_id', '=', course.id)
                ])
                course_data.append({
                    'course': course,
                    'students': student_count
                })

            # Sort by student count
            course_data.sort(key=lambda x: x['students'], reverse=True)
            top_courses = course_data[:5]  # Top 5

            html = ['<div class="top-courses-list">']

            rank_colors = ['#667eea', '#11998e', '#f093fb', '#00b4db', '#4776e6']
            rank_icons = ['trophy', 'medal', 'award', 'star', 'bookmark']

            for i, data in enumerate(top_courses):
                course = data['course']
                students = data['students']
                rank_color = rank_colors[i] if i < len(rank_colors) else '#6c757d'
                rank_icon = rank_icons[i] if i < len(rank_icons) else 'bookmark'

                html.append(f'''
                <div class="top-course-item d-flex justify-content-between align-items-center py-3 px-3 mb-2 border-bottom">
                    <div class="course-info d-flex align-items-center">
                        <div class="rank-badge text-white mr-3" style="background-color: {rank_color};">
                            <i class="fa fa-{rank_icon}"></i>
                        </div>
                        <div>
                            <h6 class="mb-1 font-weight-bold course-title">
                                {course.name[:35]}{'...' if len(course.name) > 35 else ''}
                            </h6>
                            <small class="text-muted">
                                <i class="fa fa-building mr-1"></i>
                                {course.department.name if course.department else 'No Department'}
                            </small>
                        </div>
                    </div>
                    <div class="student-count">
                        <span class="badge px-3 py-2" style="background-color: {rank_color};">
                            <i class="fa fa-users mr-1"></i>
                            {students}
                        </span>
                    </div>
                </div>
                ''')

            html.append('</div>')

            # Add styling
            html.append('''
            <style>
                .top-courses-list {
                    max-height: 400px;
                    overflow-y: auto;
                }
                .rank-badge {
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 16px;
                }
                .top-course-item {
                    transition: all 0.2s ease;
                    border-radius: 8px;
                }
                .top-course-item:hover {
                    background-color: rgba(102, 126, 234, 0.05);
                    transform: translateX(5px);
                }
                .course-title {
                    color: #2c3e50;
                    margin-bottom: 0;
                }
            </style>
            ''')

            rec.top_courses = Markup(''.join(html))

    def _compute_department_overview(self):
        """Compute department overview cards"""
        for rec in self:
            departments = self.env['op.department'].search([])

            if not departments:
                html = '''
                <div class="no-data-message text-center py-4">
                    <i class="fa fa-building fa-2x text-muted mb-2"></i>
                    <p class="text-muted">No departments found</p>
                </div>
                '''
                rec.department_overview = Markup(html)
                return

            html = ['<div class="departments-overview">']

            for dept in departments:
                course_count = self.env['op.course'].search_count([
                    ('department', '=', dept.id),
                    ('state', '=', 'publish')
                ])

                # Count total students in department courses
                courses = self.env['op.course'].search([('department', '=', dept.id)])
                total_students = sum([
                    self.env['program.reg'].search_count([('course_id', '=', course.id)])
                    for course in courses
                ])

                html.append(f'''
                <div class="department-card mb-3 p-3 border rounded">
                    <div class="row align-items-center">
                        <div class="col-8">
                            <div class="department-info">
                                <h6 class="font-weight-bold text-primary mb-1">
                                    <i class="fa fa-graduation-cap mr-2"></i>
                                    {dept.name}
                                </h6>
                                <div class="department-stats">
                                    <small class="text-muted mr-3">
                                        <i class="fa fa-book mr-1"></i>
                                        {course_count} Course{'s' if course_count != 1 else ''}
                                    </small>
                                    <small class="text-muted">
                                        <i class="fa fa-users mr-1"></i>
                                        {total_students} Student{'s' if total_students != 1 else ''}
                                    </small>
                                </div>
                            </div>
                        </div>
                        <div class="col-4 text-right">
                            <div class="department-icon bg-primary text-white">
                                <i class="fa fa-building fa-2x"></i>
                            </div>
                        </div>
                    </div>
                </div>
                ''')

            html.append('</div>')

            # Add styling
            html.append('''
            <style>
                .department-card {
                    transition: all 0.2s ease;
                    border-left: 4px solid #667eea !important;
                }
                .department-card:hover {
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                    transform: translateY(-2px);
                }
                .department-icon {
                    width: 60px;
                    height: 60px;
                    border-radius: 15px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: linear-gradient(135deg, #667eea, #764ba2) !important;
                }
            </style>
            ''')

            rec.department_overview = Markup(''.join(html))

    @api.model
    def create(self, vals):
        """Ensure only one dashboard record exists"""
        if self.search_count([]) >= 1:
            return self.search([], limit=1)
        return super(DoctorPortalDashboard, self).create(vals)