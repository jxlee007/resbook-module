# Resbook module: Odoo POC

## Resource Booking MVP

This module demonstrates internal-user booking of predefined time slots with a basic availability check and booking-state workflow.

## 1. What problem does this solve?

| Problem | Implementation |
|---|---|
| Track bookable time slots and customer bookings in Odoo | `resource.booking.slot` stores time and availability; `resource.booking` links a customer to a slot |
| Reflect reservation progress | Booking states: `draft`, `confirmed`, `cancelled`; slot states: `available`, `booked` |

## 2. (Architecture)[..\custom_addons\resource_booking\architecture\readme.md]

| Layer | Components | Responsibility |
|---|---|---|
| UI | Form, list, Kanban views; menus | Create and review slots and bookings |
| ORM | `resource.booking`, `resource.booking.slot` | Persist records and expose workflow actions |
| Validation | `_check_slot_available` | Reject a booking whose selected slot is not available |
| Access | `ir.access.csv` | Grant internal users CRUD access |
| Demo | `demo/booking_demo.xml` | Seed customers, 50 slots, and 10 bookings when demo data loads |

| Workflow step | Result |
|---|---|
| Create slot | Slot starts `available` |
| Create booking | Booking references an available slot |
| Confirm booking | Booking becomes `confirmed`; slot becomes `booked` |
| Cancel booking | Booking becomes `cancelled`; slot becomes `available` |
| Return to draft | Booking becomes `draft` |

## 3. Key files & their jobs

| File | Job |
|---|---|
| `__manifest__.py` | Declares `base`, access/views data, and demo data |
| `models/booking_slot.py` | Defines slot times and availability state |
| `models/resource_booking.py` | Defines bookings, related slot times, validation, and workflow actions |
| `models/utils.py` | Defines an overlap helper; booking validation does not currently call it |
| `security/ir.access.csv` | Grants internal users CRUD access to both models |
| `views/resource_views.xml` | Defines booking/slot forms, lists, Kanban, actions, and menus |
| `demo/booking_demo.xml` | Creates demo customers, slots, and bookings |

## 4. How to run/test it

| Task | Command or condition |
|---|---|
| Upgrade an installed module | `python odoo\odoo-bin -c odoo\odoo.conf -d resbook_db -u resource_booking` |
| Install and load demo data | `python odoo\odoo-bin -c odoo\odoo.conf -d resbook_db -i resource_booking` with demo data enabled |
| Automated tests | `custom_addons/resource_booking/tests/test_utils.py` is currently empty; no module tests are defined |

## 5. Known limitations

| Limitation | Impact |
|---|---|
| Availability validation checks slot state at booking write time | No database-level locking or uniqueness constraint prevents concurrent double-booking |
| `check_overlap` is not used | Overlapping slot times are not rejected |
| No resource, pricing, payment, or revenue models | Slots are standalone time windows |
| Access rules target `base.group_user` | Portal/public customer self-service is not implemented |
| Demo records load on install with demo data enabled | A normal module upgrade does not seed demo records |

## How to use

- Install the `resource_booking` module with demo data enabled to load sample records.
- Open **Resource Booking → Bookings** to create or manage bookings.
- Open **Resource Booking → Booking Slots** to manage available time slots.
- Confirm or cancel a booking with its form actions.
- Run the upgrade command after changing module code or views.
