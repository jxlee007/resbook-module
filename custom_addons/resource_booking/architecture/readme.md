

## PU

1. **What problem does this solve?**
   - This project exist because it made me learn abt 
   how to work and add a custom addon/module in odoo codebase
   while let allow to showcase my architecture reasoning and code understanding

2. **Who uses it?**
   - (Answer: User type. What do they need?)
   - Is to be used by junior dev users who wnat to learn 
   abt working is odoo codebase and contribute 

3. **What are the constraints?**
   - Time is the major constraint and team size is s minor

4. **How do I measure success?**
   - Visible usable UI with dynamic data
   - pgsql db read wirtes in realtime
   - Adherence of code quality and design

## AD

5. **What are my modules/domains?**
   🏢 Resource Definition Domain: Managing the items or entities available for booking (such as equipment, rooms, or vehicles), including attributes like categories, descriptions, and capacity.

   📅 Booking Transaction Domain: Handling the core reservations, tracking fields like start dates, end dates, assigned users, and workflow states (e.g., draft, confirmed, cancelled).

   🔒 Availability and Validation Domain: Implementing business logic and constraints to prevent scheduling conflicts or double-booking overlapping time slots.

6.  **How do modules communicate?**
      - Modules communicate through the ORM registry 
      — env['model.name'] gives any installed model's recordset; 
      _inherit merges code into another module's model; 
      depends in the manifest formalizes the dependency. 
      No explicit interfaces; 
      "direct DB access" via env.cr is reserved for performance-critical internals.

      Notes
      Your resource_booking module with depends: ['base'] 
      can already call self.env['res.partner'], self.env['ir.access'], etc. 
      — nothing else needed.
      
      For your hackathon write-up, 
      this contrasts with typical layered architectures: Odoo favors a monolithic shared-model design 
      where extension points are _inherit overrides, computed fields, 
      and documented "meant to be overridden" methods, rather than interfaces.

7. **What data does each module own?**
   🗄️ Data & Models Layer (models/resource_booking.py): 
   Owns the data schema, fields, and database table definitions.   
   
   🎨 Presentation Layer (views/resource_views.xml): 
   Owns how the user interacts with the data through lists, forms, and menus.   
   
   🔒 Security Layer (security/ir.access.csv): 
   Owns the permissions and access rights defining who can read, write, or create records.

8. **What are the dependencies?**
      resource_booking → base (single edge). 
      Odoo builds a ModuleGraph from ir.module.module.dependency rows, 
      loads base first, then modules in topological order. 
      Deps are transitive — I only declare direct ones.

         resource_booking  
         (your module)  
              |  
           depends on  
              |  
              v  
             base        <- always the root;  
           (ir.model,       loaded FIRST  
            ir.access,     before any other  
            res.users,     module  
            ir.ui.menu,  
            web framework) 

      That's it — your __manifest__.py declares 'depends': ['base'], 
      so it's a 2-level chain, not A → B → C. 
      base itself has no dependencies 
      and is always loaded first: graph.extend(['base']) in load_modules 

List of features - Layer 🏛️Feature ⚙️Status & Implementation Details 

📋Data & Core Models   
Resource & Booking Records   
Implemented via resource.booking model (name, start_date, end_date, description, state). 

Presentation & UI   
List and Form Views   
Implemented via XML (resource_views.xml) with badges and statusbars.   

Security & Access   
Access Control Rules   
Implemented via ir.model.access.csv granting read/write rights to internal users.   

Business Logic   
Double-Booking Validation   
Planned Python constraints to prevent overlapping resource schedules.   

Workflow & Relations   
Customer Relationship Tracking   
Planned Many2one link to res.partner for tracking who booked the resource.   

## FI

   Feature 1: Resource & Booking Records  

      1. what is happy path

      the happy path for our **Resource & Booking Records** feature 
      Here is the step-by-step path:

      * 📥 **Input:** The user navigates to the Resource Booking view, creates a new record, fills in the required fields (`name`, `start_date`, `end_date`), and clicks **Save**.

      * ⚙️ **Process:** Odoo's ORM validates the input data against the `resource.booking` model schema, initializes the record with the default `state='draft'`, and saves it to the database. When the user clicks the **Confirm** button, the model method `action_confirm()` runs, updating the `state` field to `'confirmed'`.

      * 📤 **Output:** The form re-renders, displaying the updated statusbar reflecting the active **Confirmed** state.

      2. what can go wrong ?

      3 edge cases for resource.booking
      Double-booking (overlapping start_date/end_date) 
      — two records for the same resource overlapping in time.
      
      Invalid date range — end_date earlier than start_date.
      Concurrent confirm race — two users confirming bookings for the same slot simultaneously.
      
      Edge case 1 — Overlapping bookings (the core one)
         Your resource.booking model has start_date/end_date but currently no overlap check. Odoo's hr.attendance solves the identical problem with @api.constrains — _check_validity searches for the latest record before check_in and raises ValidationError if its check_out exceeds your check_in, and separately rejects a second "open" record hr_attendance.py:197-228 .

         Adapted pattern for your model (needs a resource_id or similar key once you split resource vs booking per your notes.txt plan):

         @api.constrains('start_date', 'end_date')  
         def _check_overlap(self):  
            for booking in self:  
               overlap = self.search([  
                     ('id', '!=', booking.id),  
                     ('state', '=', 'confirmed'),  
                     ('start_date', '<', booking.end_date),  
                     ('end_date', '>', booking.start_date),  
               ], limit=1)  
               if overlap:  
                     raise ValidationError("Resource already booked in this period")

         For a stronger guarantee add a SQL constraint too 
         — models.Constraint('CHECK(...)') as used on _check_time_efficiency in resource.

         Edge case 2 — end_date < start_date
         Same @api.constrains mechanism, simpler check — mirrored almost exactly by _check_validity_check_in_check_out which raises when check_out < check_in hr_attendance.py:189-195 :

         @api.constrains('start_date', 'end_date')  
         def _check_dates(self):  
            for b in self:  
               if b.end_date < b.start_date:  
                     raise ValidationError("End date must be after start date")


         Edge case 3 — Concurrent confirm race
         Two users click "Confirm" on overlapping bookings in the same second. Python-level constrains alone can pass for both transactions before either commits.

         Keep the overlap check inside a confirm() method so it runs in the same transaction that writes state='confirmed'.
         Odoo raises ConcurrencyError when a record was modified since it was read (imported in odoo/orm/registry.py ); the HTTP layer's retrying wrapper automatically retries the request on serialization failures — your earlier traceback went through odoo/http/retrying.py:56.
         For the MVP, catching this in write/confirm and returning a friendly UserError is sufficient; for real safety, a Postgres exclusion constraint on the date range is the bulletproof version.

            For your questionnaire answer (Q10)
            Overlapping bookings → @api.constrains overlap query (pattern from hr.attendance._check_validity).
            Inverted date range → @api.constrains end_date < start_date check (pattern from _check_validity_check_in_check_out).
            Confirm race → check inside the write transaction; ConcurrencyError + retrying handles lost races.
            Notes
            Your current resource.py merges "resource" and "booking" into one model — the overlap edge case only becomes meaningful once you add a resource_id Many2one (or a resource.booking.slot model per notes.txt Hour 2–3) so two bookings can actually collide.
            resource.resource._get_unavailable_intervals / _get_valid_work_intervals in addons/resource/models/resource_resource.py show the more advanced interval-math approach (Intervals class) if you later integrate with resource.calendar resource_resource.py:155-176 — overkill for the MVP but good to mention as the "alternative" in Q31.


      
      3. Which layer does each piece live in?
         - (Domain = business rule? UseCase = orchestration? Adapter = database?)
         📊 Data Model & Fields (name, start_date, end_date, state): These define the core entity structure, living primarily in the Domain layer while mapping directly to the Adapter (Database) layer via Odoo’s ORM.

         ⚙️ State Transition Methods (action_confirm, action_cancel): These act as part of the Use Case layer, handling workflow orchestration and state changes.

      4. 

     
