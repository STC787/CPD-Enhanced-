from odoo import models, fields, api

class PaymentWay(models.Model):
    _name = "payment.way"
    _rec_name = 'payment_type'

    payment_type = fields.Char(string='Type Of Payment', required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    journal_table = fields.One2many('journal.table', 'payment_way_id', string='Journal Table')

    def create_cash_register(self):
        for rec in self.env['payment.way'].search([]):
            for re in rec.journal_table:
                if rec.journal_table:
                    for i in re.cash.ids:
                        statement = self.env['account.bank.statement'].search(
                            [('journal_id', '=', i), ('date', '=', fields.Date.today())])


class JournalTable(models.Model):
    _name = 'journal.table'

    payment_way_id = fields.Many2one('payment.way')
    cashier = fields.Many2one('res.users', string='Cashier')
    cash = fields.Many2many('account.journal', string='Journal')
