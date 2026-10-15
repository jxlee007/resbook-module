from datetime import datetime

from odoo import models, fields  # type: ignore

class ResourceBooking(models.Model):  # type: ignore[reportUnknownMemberType, reportUntypedBaseClass]
    _name = 'resource.booking'
    _description = 'Resource Booking'

    name: str = fields.Char(string='Resource Name', required=True)  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
    start_date: datetime = fields.Datetime(string='Start Date', required=True, default=fields.Datetime.now)  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
    end_date: datetime = fields.Datetime(string='End Date', required=True)  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
    description: str | None = fields.Text(string='Description')  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
    state: str = fields.Selection(  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
        [
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        default='draft',
        required=True,
    )