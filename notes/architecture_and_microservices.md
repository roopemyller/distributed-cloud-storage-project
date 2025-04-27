## System Architecture and Microservices
--*Thoughts from Roope + ChatGPT*--

### Services

**What services do we need?**

* Authentication service
    * Login and registration
    * JWT/token
    * bcrypt hashing
    * User authentication
    * Admin authentication
    * API
        * POST /auth/register
        * POST /auth/login
        * GET /auth/authenticate
    * DB
        * users (id, username, email, password hash, role etc.)

* File storage service
    * Upload
    * Download
    * List
    * Delete
    * Folder management

* Metadata service
    * Stores file metadata in DB
        * ID
        * Filename
        * Path
        * Size
        * Owner
        * Timestamps

* Sync service NOT PRIORITY
    * Auto background sync between local & cloud
    * Detect changes to files
    * Trigger upload/download to match states
    * Using threading for tasks


**How does the services communicate?**

* API calls with FastAPI

**Database** (for users, metadata, etc.)

* PostgreSQL

**File Storage** (for the files, posing as the "cloud storage")

Options:
* Local Disk

---
### System Architecture

            Python CLI App (main)      Web App (optional)
                     ↓                          ↓
                            API Calls
                                  ↓
        ┌────────────┬────────────┬──────────────┬────────────┐
        │  Auth Svc  │  File Svc  │ Metadata Svc │  Sync Svc  │
        └────────────┴────────────┴──────────────┴────────────┘
                     ↓                           ↓
                     DB                  Local File Storage
---
### How it works

#### General Flow (From CLI to Disk)

Case: User wants to upload a file

1. CLI -> sends file + metadata to the backend via API
2. Backend:
    * Auth Service verifies the JWT token
    * Metadata service saves file info to database
    * File service stores the file to local disk or object storage (posing as the cloud storage)
