# Eventura — Event Booking & Waitlist Management System

Eventura is a high-performance RESTful API designed to manage event organization, ticket bookings, automated waitlists, and background notifications.

---

## Technologies Used & Tech Stack

* Framework: Django 6 and Django REST Framework (DRF)
* Language: Python 3.12
* Database Engine: PostgreSQL
* Asynchronous Task Queue: Celery
* In-Memory Broker: Redis
* Documentation Engines: OpenAPI 3.0 (via drf-spectacular) and Postman

---

## Architectural & Technical Highlights

### Concurrency & Race Conditions Mitigation
* Pessimistic Locking: Uses select_for_update() at the database level to lock the TicketType row during booking operations.
* Atomic Transactions: Wraps seat verification and reservation inside @transaction.atomic to prevent overbooking on high-traffic, last-seat scenarios.

### Smart Waitlist Management
* Automated Queue Promotion: When a confirmed booking is cancelled, a strict transaction automatically promotes the first active user in the waitlist based on their position.
* Data Integrity: Deactivating or leaving the queue triggers a Soft Delete (is_active=False) instead of a physical row deletion to preserve historical data.

### Background & Scheduled Tasks (Celery & Redis)
* Message Broker: Powered by Redis as the broker and Celery as the distributed task runner.
* Asynchronous Triggers: Offloads time-consuming notification dispatches (e.g., when an event is cancelled) to background workers using bulk_create() and distinct() filters.
* Scheduled Cron Jobs: Utilizes Celery Beat to run periodic tasks (e.g., 24-hour event reminders checking every hour, and 15-minute event-started alerts).

### Security & Constraints Architecture
* JWT Lifecycle & Blacklisting: Access tokens valid for 6 hours, refresh tokens for 7 days. Refresh tokens are blacklisted upon logout to immediately invalidate sessions on demand.
* Email Normalization: Automatically lowercases user emails during registration and authentication to prevent duplicate accounts with mismatched casing.
* Object-Level Permissions: Custom permission classes (IsOrganizer, IsOwnerOrAdmin) restrict update/delete actions to the resource's actual owner or organizer.

### Database Optimizations & Query Efficiency
* N+1 Query Fixes: Enforces selective use of select_related and prefetch_related across viewsets.
* Database Annotations: Calculates aggregate parameters like average_rating, review_count, and bookings_count directly inside the database query engine via annotate().
* Advanced Indexing: 
  * Composite indexes on (status, start_date) for fast event searches.
  * Partial unique indexes (WHERE status = confirmed / WHERE is_active = true) to enforce strict conditional constraints.
  * Dedicated queue index on (ticket_type_id, is_active, position) for O(1) top-of-waitlist lookups.

### Testing Strategy
* Comprehensive coverage of both Happy and Unhappy Paths across models, serializers, and views using Django TestCase and DRF APITestCase.
* Adheres strictly to the AAA Pattern (Arrange, Act, Assert).
* Uses unittest.mock.patch to isolate database behaviors during complex mock validations.

---

## Database Design & Visuals

* Interactive Schema: [View Live on dbdiagram.io](https://dbdiagram.io/d/Event-Booking-API-69ff2ae97a923b947263ab8f)
* Database Schema Visual:

![Database Schema](DB%20diagram.png)

---

## OpenAPI Specification & Interactive Docs

The project includes an auto-generated API schema compliant with OpenAPI 3.0 specs available via drf-spectacular.


![Endpoints](API%20docs%201.png)
![Endpoints](API%20docs%202.png)
![Endpoints](API%20docs%203.png)
![Endpoints](API%20docs%204.png)
![Endpoints](API%20docs%205.png)



Click on each section below to expand the documentation endpoints and tables:

<details>
<summary>1. Authentication & Security (auth)</summary>

### Authentication Endpoints
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| POST | `/api/auth/register/` | Register a new user account |
| POST | `/api/auth/login/` | Login user & obtain access/refresh JWT tokens (Custom lowercase mapping) |
| POST | `/api/auth/logout/` | Logout user & blacklist refresh token to terminate session |
| POST | `/api/auth/token/refresh/` | Refresh access token using a valid refresh token |

</details>

<details>
<summary>2. User Profiles Management (users)</summary>

### User Profiles Endpoints
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| GET | `/api/users/me/` | View current authenticated user profile |
| PATCH | `/api/users/me/` | Partial profile update management |
| POST | `/api/users/change-password/` | Secure password updating |
| DELETE | `/api/users/delete-account/` | Deactivates profile safely via Soft Delete |

</details>

<details>
<summary>3. Events, Tickets & Categories</summary>

### Events, Ticket-Types & Categories Endpoints
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| GET | `/api/events/` | List all published/active events (Supports filtration, search & ordering) |
| POST | `/api/events/` | Create a new event (Drafted by default) |
| GET | `/api/events/{id}/` | Retrieve detailed event configurations |
| PUT | `/api/events/{id}/` | Full update parameters on an event |
| PATCH | `/api/events/{id}/` | Partial update on specific event fields |
| DELETE | `/api/events/{id}/` | Terminate/delete an event (Organizer/Admin only) |
| PATCH | `/api/events/{id}/status/` | Manage state changes (Drafted to Published to Cancelled) |
| GET | `/api/events/organizer/{organizer_pk}/` | Extract organizer-specific event scopes |
| GET | `/api/ticket-types/` | List available ticket variants and configurations |
| POST | `/api/ticket-types/` | Create seating capacities and pricing for an event |
| GET | `/api/ticket-types/{id}/` | View details of a specific ticket type |
| PUT | `/api/ticket-types/{id}/` | Full update configurations |
| PATCH | `/api/ticket-types/{id}/` | Partial update (Recalculates seats based on bookings) |
| DELETE | `/api/ticket-types/{id}/` | Remove a ticket type if it has no active bookings |
| GET | `/api/categories/` | List all event categories (Supports search filter) |
| POST | `/api/categories/` | Create a new category (Admin only) |
| GET | `/api/categories/{id}/` | Retrieve a specific category detail |
| DELETE | `/api/categories/{id}/` | Category deletion operation (Admin only) |


</details>

<details>
<summary>4. Core System (bookings, waitlist, reviews & notifications)</summary>

### Bookings, Waitlists, Reviews & Notifications Endpoints
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| GET | `/api/bookings/` | List confirmed bookings for the logged-in user |
| POST | `/api/bookings/` | Ticket booking (Returns 201 Confirmed or 202 Waitlisted) |
| GET | `/api/bookings/{id}/` | View ticket booking receipt details |
| POST | `/api/bookings/{id}/cancel/` | Cancel booking (Triggers atomic waitlist promotion) |
| GET | `/api/bookings/event/{event_pk}/` | Extract all bookings assigned to an event (Organizer only) |
| GET | `/api/waitlist/` | Track user's active waitlist queues and current positions |
| DELETE | `/api/waitlist/{id}/` | Leave a waitlist queue manually (Soft Delete) |
| GET | `/api/waitlist/event/{event_pk}/` | Inspect the full waitlist queue for an event (Organizer only) |
| GET | `/api/reviews/` | View user's own compiled reviews |
| POST | `/api/reviews/` | Conditional user reviews (Post-event completion & attendance checks) |
| GET | `/api/reviews/{id}/` | Fetch single review details |
| PATCH | `/api/reviews/{id}/` | Update review rating score or comments |
| DELETE | `/api/reviews/{id}/` | Remove an event review |
| GET | `/api/reviews/event/{event_pk}/` | Pull all historical user reviews for a specific event |
| GET | `/api/notifications/` | Live feed of user notifications ordered by newest |
| GET | `/api/notifications/{id}/` | View a single notification body |
| DELETE | `/api/notifications/{id}/` | Dismiss/delete an alert notification |
| PATCH | `/api/notifications/{id}/read/` | Mark a single notification alert as read |
| PATCH | `/api/notifications/read_all/` | Bulk mark all user notifications as read |

</details>

---

## Postman Testing Suite

* [Live Public Documentation](https://documenter.getpostman.com/view/46689659/2sBXwtqq3H#45516f80-889f-43e4-b016-52f8ab568ca9)
* Local Collection File: Download and import into your Postman workspace: [Eventura.postman_collection.json](./Eventura.postman_collection.json)

---

## Project Blueprint Structure

```text
eventura/
├── src/                  # Settings, URL routing, Celery app config, ASGI/WSGI
├── users/                # User Models, Custom UserManager, and Profile validations
├── events/               # Event, Category & TicketType models, and Status Flow logic
├── bookings/             # Isolated Services layer, Concurrency control, and Queue promotion
├── reviews/              # Event ratings restricted by confirmed booking histories
├── notifications/        # User Notification histories automated via Celery Tasks
└── utils/                # Shareable codebase mixins (e.g., PaginatedActionMixin)