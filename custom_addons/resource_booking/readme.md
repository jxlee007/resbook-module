

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

      4. Can I test this without the full app?
         - In Odoo's framework, models inherit from models.Model, which relies heavily on the ORM registry 🗄️ and a database connection. Because of this tight coupling, testing Odoo models directly requires the Odoo test environment (such as using TransactionCase) rather than running completely isolated standard Python scripts.

         However, if we separate our core business rules—like checking date calculations or overlaps
         —into pure Python helper functions independent of the ORM, 
         we can test that logic modularly 🧪!

         for that we created utils.py


      
   Feature 2: List and Form Views 

      1. What is happy path ??

      📋 1. List View
      Input 📥: User clicks the menu item to open resource bookings.
      Process ⚙️: Odoo queries the database and renders tabular rows displaying core fields like name, customer, and dates.
      Output 📤: A structured, searchable table giving a high-level overview of all records.

      📝 2. Form View
      Input 📥: User clicks "Create" or selects an existing booking row to enter or review details.
      Process ⚙️: The form model evaluates constraints (such as checking if slot_id is available) and executes state actions like confirming or cancelling.
      Output 📤: A saved, validated record with synchronized slot states (available vs booked).

      📊 3. Kanban View
      Input 📥: User switches the view mode to Kanban grouped by state.
      Process ⚙️: Odoo organizes booking cards into distinct visual columns based on their current status (draft, confirmed, cancelled).
      Output 📤: A dynamic board offering visual pipeline tracking of booking states.

      2. what can go wrong ?

      ⏱️ 1. Double Booking the Same Slot

         What goes wrong: Two different customers try to confirm a booking for the exact same slot_id at the same time, potentially bypassing validation if checks are performed out of sequence.

         How to handle: Implement a database-level unique constraint or check constraint on the slot status, combined with @api.constrains in Odoo to re-verify that slot_id.state == 'available' inside a transaction lock before writing.

         🔄 2. Orphaned Bookings on Slot Deletion

         What goes wrong: A user deletes a slot record that already has a linked booking, causing database integrity errors or broken foreign keys.

         How to handle: Set ondelete='restrict' on the slot_id Many2one field in resource_booking.py so Odoo prevents deleting a slot while an active booking depends on it.

         ❌ 3. State Mismatch via Direct Database Edits

         What goes wrong: A booking is cancelled directly in the backend, but the underlying slot remains marked as booked, preventing other customers from reserving it.

         How to handle: Override the unlink or write methods in the model, or rely strictly on action methods (action_cancel) to ensure slot states update symmetrically whenever booking states change.


      3. Which layer does each piece live in?

        🏛️ Interface Adapters (UI & Database): List, Kanban, and Form views live here. XML view definitions and Odoo ORM models act as adapters. They translate data from the application layer into visual formats for the user interface and translate user actions (like clicking buttons or dragging cards) back into system commands.

        ⚙️ Use Cases (Orchestration): Model action methods like action_confirm() and action_cancel() live here, orchestrating workflow logic, state transitions, and coordination between bookings and slots.

        🧠 Domain (Business Rules): Pure utility logic like our check_overlap() function lives here, completely isolated from both the database and UI layers.

      
      4. Can I test this without the full app?

         YES! 🎯 By isolating our core overlap logic into `utils.py`, we can test that business rule independently using standard testing tools like `pytest` without needing to boot up an entire Odoo database instance.

         However, Odoo models and UI views (`resource_booking.py` and XML views) still rely heavily on the ORM registry and require the Odoo test environment (`TransactionCase`).


   Feature 3: Access Control Rules   

      1. What is the happy path ?

         📥 Input: A user with a specific security group (such as a Regular User or Manager) attempts an operation, like creating a new booking or deleting a slot.

         ⚙️ Process: Odoo’s ORM security engine intercepts the request and cross-references the user's group memberships with the permission flags (read, write, create, unlink) defined for that model.

         📤 Output: If the user has the required rights, the database transaction proceeds successfully; otherwise, an access error blocks the action safely.

      2. What can go wrong ?

      Let's look at 3 common edge cases when working with Odoo Access Control Lists (ACLs) and how we handle each:

         * 🚫 **1. The "Implicit Deny" Trap (Missing Read Rights)**
         * **What goes wrong:** A user is given explicit `write` or `create` rights on a model via a security group, but Odoo blocks them completely because they lack underlying `read` permissions.
         * **How to handle:** Always ensure that any custom security group grants foundational `perm_read` (alongside write, create, and unlink as needed) in your `ir.model.access.csv` file.


         * 👥 **2. Group Inheritance Conflicts**
         * **What goes wrong:** A user belongs to multiple groups (e.g., both "Portal" and "Manager"), and an overly restrictive ACL rule from one group unexpectedly overrides the broader permissions of another.
         * **How to handle:** Structure your security groups hierarchically using Odoo's `implied_ids` mechanism so that higher-level roles cleanly inherit and expand upon baseline permissions without conflicting rule overlaps.


         * 📄 **3. Missing CSV Header or Malformed Rows**
         * **What goes wrong:** A typo in the `ir.model.access.csv` column headers or missing model reference IDs causes Odoo to crash on module installation or silently ignore the security rules entirely.
         * **How to handle:** Verify that your CSV uses the exact required column headers: `id`, `name`, `model_id:id`, `group_id:id`, `perm_read`, `perm_write`, `perm_create`, and `perm_unlink`.

      3. Which layer does each piece live in?
      - Let’s map the access control rules feature to Clean Architecture layers:

         * 🗂️ **Interface Adapters (Framework & Database):** **`ir.access.csv` and XML record rules** live here. They are framework-specific configurations that tell Odoo's database and ORM engine how to restrict table-level and row-level access.
         * ⚙️ **Use Cases (Orchestration):** **Authorization checks** performed during application workflows (like verifying whether a user has the right to trigger `action_confirm()`) orchestrate security at the application level.
         * 🧠 **Domain (Business Rules):** **Core permission criteria**—such as defining *who* is allowed to book a resource based on user roles or status—reside as business rules that inform how security boundaries are drawn.
      
      4. Can I test this without the full app?

         Unlike our pure Python utility function, access control rules defined in ir.model.access.csv rely directly on Odoo's ORM and database security engine 🛡️. Therefore, they cannot be tested in complete isolation without the Odoo environment.

         However, this doesn't mean a refactor is needed—framework configurations like security CSVs are naturally tied to Odoo. Instead, we test them using Odoo's built-in integration testing framework.

         📊 Isolated Unit Tests: Not possible, because the CSV rules require the Odoo registry and database to parse and apply.

         🧪 Integration Tests: Conducted using Odoo's TransactionCase, allowing us to simulate specific user permissions.

         👤 Manual Testing: Verified by logging in with different user roles in the UI.

   
   Feature 4: Double-Booking Validation  

      1. What is the happy path ?

         📥 Input: A user attempts to confirm a resource booking linked to a specific slot_id that is currently marked as available.

         ⚙️ Process: Odoo triggers our validation constraint and confirmation logic, verifying that the target slot remains free right up until the database write occurs.

         📤 Output: The validation passes successfully, the slot state updates to booked, and the booking state transitions to confirmed without any collisions.

      2. What can go wrong with this ?

         Here are 3 common edge cases for double-booking validation and how to handle them:

         1. ⏱️ **Concurrent Race Conditions:** Two separate users click confirm on the exact same slot at the exact same millisecond, potentially bypassing a standard Python-level check if both transactions read the slot as available simultaneously.
         * *Handling:* Rely on Odoo's transaction handling or database-level constraints/locks (`SELECT ... FOR UPDATE`) to ensure atomicity during the write operation.


         2. 📅 **Partial Overlapping Intervals:** Bookings might use different slot records, but their start and end datetimes intersect (e.g., booking from 10:00 to 12:00 when another exists from 11:00 to 13:00).
         * *Handling:* Integrate our pure Python `check_overlap` domain function inside a model-level constraint to evaluate interval intersections.


         3. 🔄 **Stale State Desynchronization:** A booking is cancelled or deleted, but the linked slot fails to update its state back to available due to an incomplete transaction rollback.
         * *Handling:* Wrap state transitions and slot updates inside robust Odoo action methods (`action_confirm` and `action_cancel`) to guarantee they commit together.

      3. Which layer does each piece live in?
          🧠 Domain (Business Rules): check_overlap() in utils.py lives here. It contains pure Python logic evaluating datetime interval intersections without any knowledge of Odoo or databases.

          ⚙️ Use Cases (Orchestration): Model constraints and action methods (like @api.constrains and action_confirm()) live here. They orchestrate the workflow by verifying slot availability and coordinating state transitions before database writes occur.

          🗂️ Interface Adapters (Database & Framework): Odoo ORM transactions and field definitions live here, handling database-level persistence and translating framework operations.

      4. Can I test this without the full app?

         YES! 🎯 Because we separated our concerns using Clean Architecture, we can test the core logic independently:

         🧠 Domain Logic (utils.py): The check_overlap() function is pure Python. We can write fast unit tests for this core overlapping algorithm using standard tools like pytest without needing an active Odoo database or server.

         ⚙️ Model Constraints (resource_booking.py): The @api.constrains decorator and ORM-level checks interact directly with Odoo's registry and database, so those model-level validation tests require Odoo's testing environment (TransactionCase).

   Feature 5:Customer Relationship Tracking

      1. What is the happy path ?

         📥 Input: A customer selects a resource slot and submits a new booking, automatically linking their profile (res.partner) to the booking record.

         ⚙️ Process: Odoo's ORM relational fields associate the booking with the correct partner, aggregating past and active bookings under that customer’s profile view.

         📤 Output: A unified customer history where staff can view all associated bookings, contact details, and current booking states directly from the customer's contact form.

      2. What can go wrong with this ?

         👥 1. Orphaned Bookings on Partner Deletion

         What goes wrong: A customer account (res.partner) is deleted from the system while they still have active or historical bookings tied to their ID, causing broken database relations or integrity errors.

         How to handle: Set ondelete='restrict' on the customer_id Many2one field in resource_booking.py so Odoo prevents deleting a partner profile if active bookings depend on them.

         🔀 2. Merging Duplicate Customer Records

         What goes wrong: A customer creates multiple partner profiles with different email addresses or typos, splitting their booking history across separate records and making it difficult to track their full activity.

         How to handle: Utilize Odoo's built-in Partner Merge wizard (base.partner.merge.automatic.wizard), which safely combines duplicate customer profiles while automatically re-pointing all associated resource.booking records to the primary contact.

         🔒 3. Unauthorized Access to Another Customer's History

         What goes wrong: A portal user or regular customer logs in and gains visibility into other customers' booking records and personal contact details due to overly permissive record rules.

         How to handle: Implement strict Record Rules (Domain filters) in Odoo's security configuration (such as filtering domain records by [('customer_id', '=', user.partner_id.id)] for portal users) so customers can only view their own bookings.

      3. Which layer does each piece live in?
         - (Domain = business rule? UseCase = orchestration? Adapter = database?)

         🗂️ Interface Adapters (Database & Framework): The customer_id = fields.Many2one('res.partner', ...) field and the underlying relational database foreign keys live here. They connect our custom resource.booking table to Odoo's built-in partner registry.

         ⚙️ Use Cases (Orchestration): Application-level processes, such as the partner merge wizard (base.partner.merge.automatic.wizard) or methods that orchestrate re-pointing booking history, live here.

         🧠 Domain (Business Rules): Core policies defining customer association requirements—such as whether a booking must be tied to a verified customer profile—reside as business rules.

      4. Can I test this without the full app?
         - (YES = good design. NO = refactor.)

         No, relational fields and database constraints like ondelete='restrict' rely directly on Odoo's ORM and the database registry 🗄️.

         Because these features depend on core Odoo models like res.partner, testing them requires Odoo's framework environment (TransactionCase) rather than an isolated unit test. This isn't a design flaw—it's standard for features that interface directly with the database framework.

         🧪 Testing Boundaries:

         Unit Tests (pytest): Perfect for isolated, pure Python domain logic (like our interval overlap calculations).

         Integration Tests (TransactionCase): Necessary for testing ORM fields, relational integrity, and database-level rules.
      
   
Here's each answer framed for your `resource_booking` addon on Odoo 20.

---

## Level 4 — Code Design

**13. ONE job per function?**
Each `action_*` method does exactly one thing: `action_confirm` transitions state + validates the slot; `action_cancel`/`action_draft` only write state. `_check_slot_available` only validates availability. Odoo itself enforces this — a `<button type="object">` maps to exactly one method, and `@api.constrains` methods get wrapped per-field-set in `_constraint_methods` [1](#23-0) .

**14. In/out contract?**
Model methods operate on `self` (a recordset) — that's the "input"; outputs are usually `None` (state change via `write`) or an action dict. This is the Odoo convention, e.g. `_access_domain` takes an operation string and returns a `Domain` [2](#23-1) .

**15. DB/framework dependency?**
Yes — everything on a `models.Model` lives in the "adapter" layer by definition (`self.env`, `self.search`, `self.env.cr`). Odoo doesn't separate Domain/UseCase like clean architecture; the model *is* both. That's the framework's documented design — `_auto_init` couples the model directly to schema management [3](#23-2) .

**16. Testable alone?**
Yes, via `odoo.tests.common.TransactionCase` — you get a real DB with rollback, and test methods directly (`self.env['resource.booking'].create({...})` then assert the `ValidationError` on double-booking). Not pure unit-testable (needs a DB), but each method is isolated behind `env`.

## Level 5 — Code Quality

**17. Pure?**
No — `action_confirm` mutates state (`self.state = 'confirmed'` → SQL write). Constraints `_check_*` are the closest to pure (read-only, raise-or-nothing). In Odoo, purity matters less than **transactionality** — a raised `ValidationError` inside a constraint rolls back the whole write atomically.

**18. Module boundaries violated?**
No — `resource_booking` only touches `res.partner` and `resource.booking.slot`, both reached through `env[...]` registry lookup, never direct SQL on another module's tables. In Odoo the boundary rule is "call through the registry + ORM", which you did [4](#23-3) .

**19. Rename a module → break?**
Partially tight: `model_id:id` values in `ir.access.csv` (`model_resource_booking`) and XMLIDs in views would break on a rename — they're generated per module/model name [5](#23-4) . But `depends: ['base']` means no other addon couples to yours, so nothing upstream breaks.

**20. 2-minute readable?**
Yes — small file, field names mirror DB columns, `action_*` naming follows Odoo convention (button name = method name). Gap: no docstrings/comments on `_check_slot_available` explaining *why* a two-phase slot check is needed — add a 1-liner.

## Level 6 — Database Design

**21. Normalized?**
Yes — after the split, `resource_booking` stores only `slot_id`/`customer_id` FKs; times live once on `resource_booking_slot`. No duplicated datetime columns on both tables.

**22. Foreign keys?**
Yes — every `Many2one` emits a real Postgres FK automatically; `required=True` gives `ondelete='restrict'` semantics enforced at ORM + DB level [6](#23-5) .

**23. Indexes?**
`slot_id`/`customer_id` get automatic btree indexes (Odoo indexes stored Many2ones by default). Candidate extra: `state` if you filter by it constantly (kanban groupby already benefits), or a composite `(slot_id, state)` — add `index=True` or `index='btree'` only if profiling shows need [7](#23-6) .

**24. N+1?**
No — the ORM prefetches: `self.env.cr.execute`-free recordset iteration batches field fetches; `search_fetch`/`_fetch_query` issue a single SELECT for all requested fields. Relational reads (`booking.slot_id.start_datetime`) hit the in-memory cache/`inselect` batching, not per-record queries. Your overlap `search(..., limit=1)` is one query per record — acceptable inside a constraint; Odoo does exactly this in `hr.attendance._check_validity`.

## Level 7 — API Design

**25. Resource-oriented?**
Your module has no custom REST endpoints — Odoo's generic `/web/dataset/call_kw` + JSON-RPC is the API, and it *is* resource-oriented (`model` + `method` + `args`). If you add endpoints, use `@http.route('/resource_booking/slots', type='json')` style — noun, not verb.

**26. HTTP methods?**
Odoo controllers default to accepting what's declared in `route(methods=[...])`; `call_kw` is always POST since it's an RPC envelope. For any custom endpoint: GET for reads, POST for creates/actions.

**27. Consistent contract?**
The RPC layer guarantees it — success → `{"result": ...}`, failure → `{"error": {...}}` (the RPC_ERROR you saw earlier is this envelope). Custom endpoints should return the same shape.

**28. Errors?**
Mapped for you: `ValidationError`/`UserError` → 400-ish client-visible dialog; `AccessError` → 403; missing record → `MissingError`; unhandled → 500 + traceback (like your `UndefinedColumn` run). Raise `UserError`, not bare `Exception`, for user-facing failures.

## Level 8 — Communication & Documentation

**29. 30-second diagram?**
```
Browser (OWL client)
      |  JSON-RPC /web/dataset/call_kw
      v
ir.http dispatcher ──> resource.booking methods
      |                     |
      |                     +--> env['resource.booking.slot'] (Many2one FK)
      |                     +--> env['res.partner'] (customer_id FK)
      v
Registry (shared env) ──> PostgreSQL resource_booking / resource_booking_slot
```

**30. Main decision in 1 sentence?**
"I split `slot` into its own model with a `state` field so availability is checked atomically at `create()`/`write()` via a Python constraint — the same pattern `hr.attendance` uses to reject overlapping records."

**31. Alternative & why rejected?**
Alternative: single model with `start_date`/`end_date` + overlap constraint (`_check_validity`-style range check), or the `Intervals`-based approach from `resource.resource._get_unavailable_intervals`. Rejected because slot-as-entity gives you the double-booking guard for free (one row = one bookable unit), and interval math was overkill for a 10-hour MVP.

**32. If this changed, what breaks?**
Renaming `resource.booking` breaks: the `model_id:id` XMLID (`model_resource_booking`) in `ir.access.csv`, every `<field name="res_model">`/`action` `res_model` in `resource_views.xml`, and any `env['resource.booking']` callers. Changing `state` selection values breaks the kanban `group_expand`/`default_group_by` and the demo records' `state` literals. Adding a required field breaks demo/data XML lacking it — you hit this exact failure twice already (`UndefinedColumn`, missing-field view errors).

## Notes

- Q15/Q17: strict clean-architecture layering doesn't map onto Odoo — the honest answer is "the ORM is the adapter; my domain logic lives inside model methods, which is the framework's intended extension point."
- For Q24, if you demo with the profiler (`--log-handler=odoo.sql_db:DEBUG`), you can literally show one SQL query per `search_fetch` — nice proof for the rubric.