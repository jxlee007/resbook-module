from odoo import models, fields, api
from odoo.exceptions import ValidationError
from .utils import check_overlap

class ResourceBooking(models.Model):
    _name = 'resource.booking'
    _description = 'Resource Booking'

    # 🔗 Links & Related Fields
    slot_id = fields.Many2one('resource.booking.slot', required=True, string='Booking Slot')
    customer_id = fields.Many2one('res.partner', required=True, string='Customer')
    name = fields.Char(string='Booking Name', required=True)
    description = fields.Text(string='Description')
    start_date = fields.Datetime(related='slot_id.start_datetime', readonly=True)
    end_date = fields.Datetime(related='slot_id.end_datetime', readonly=True)
    
    # 🔄 State Management
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ], default='draft', required=True, group_expand=True)

    @api.constrains('slot_id')
    def _check_slot_available(self):
        """Ensure the selected slot is available before saving."""
        for rec in self:
            if rec.slot_id.state != 'available':
                raise ValidationError("This slot is already booked!")

    def action_confirm(self):
        """Confirm the booking and mark the slot as booked."""
        self.slot_id.write({'state': 'booked'})
        self.write({'state': 'confirmed'})

    def action_cancel(self):
        """Cancel the booking and free up the slot."""
        self.slot_id.write({'state': 'available'})
        self.write({'state': 'cancelled'})

    def action_draft(self):
        """Return the booking to draft without reserving its slot."""
        self.write({'state': 'draft'})