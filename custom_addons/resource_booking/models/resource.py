from odoo import models, fields

class ResourceBooking(models.Model):
    _name = 'resource.booking'
    _description = 'Resource Booking'

    name = fields.Char(string='Resource Name', required=True)

    start_date = fields.Datetime(string='Start Date', required=True, default=fields.Datetime.now)
    end_date = fields.Datetime(string='End Date', required=True)
    description = fields.Text(string='Description')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True)