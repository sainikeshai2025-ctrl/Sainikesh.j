# LegalEase User Guide & Practical Scenarios

## 1. Quick Start
1. Start the application using `./run.bat` (Windows) or `./run.sh` (Mac/Linux).
2. The Streamlit web UI opens at `http://localhost:8501`.
3. Fill in the Agreement details or select one of the pre-loaded templates from the sidebar.
4. Click **⚡ Generate Document**.
5. Review the dark-mode HTML preview, make any necessary adjustments with **✏️ Click to Edit Document**, and download as `.txt`, `.docx`, or `.pdf`.

---

## 2. Core Scenarios from Documentation

### Scenario 1: Employment Contract / Offer Letter
- **User:** Startup founder hiring a new employee.
- **Document Type:** `Employment Contract`
- **Parties:** `Acme Innovations Corp. (Employer), Alex Taylor (Employee)`
- **Terms:** `Full-time position as Senior Software Engineer; Annual salary of $120,000 paid bi-weekly; Standard health benefits and 20 days PTO; Standard IP assignment and confidentiality clauses; Either party may terminate with 30 days notice`
- **Effective Date:** `May 01, 2025`
- **Outcome:** Generates an employment agreement with clear clauses for role, duties, remuneration, intellectual property, confidentiality, and termination, downloadable as a branded PDF and DOCX with an embedded logo.

### Scenario 2: Non-Disclosure Agreement (NDA)
- **User:** Freelancer / Consultant initiating discussions with a prospective client.
- **Document Type:** `Non-Disclosure Agreement (NDA)`
- **Parties:** `Sarah Jenkins (Disclosing Party), Quantum Leap Studios (Receiving Party)`
- **Terms:** `Information exchanged remains strictly confidential for 24 months; Definition of confidential info covers software architecture and business models; Information shall not be reproduced or distributed; Injunctions and legal damages apply upon breach`
- **Effective Date:** `June 15, 2025`
- **Outcome:** Produces an NDA with standard preamble, confidentiality scope, exceptions, return of materials, and execution blocks.

### Scenario 3: Residential Lease Agreement
- **User:** Landlord drafting a lease for residential property.
- **Document Type:** `Residential Lease Agreement`
- **Parties:** `David Miller (Landlord), Maria Garcia (Tenant)`
- **Terms:** `Monthly rent of $1,800 due on the first day of each month; Security deposit of $1,800 held in escrow; Lease duration of 12 months with automatic month-to-month renewal; No unauthorized alterations or subletting without prior written consent`
- **Effective Date:** `August 01, 2025`
- **Outcome:** Generates a residential tenancy agreement featuring a formatted Terms Schedule Table in the `.docx` export and ready-to-sign PDF format.

---

## 3. Input Formatting Best Practices
- **Document Type:** Specify the exact formal title (e.g. *Freelance Work Contract*, *Master Services Agreement*).
- **Parties Involved:** Clarify both legal names and contractual roles (e.g., `[Name] ([Role]), [Company] ([Role])`).
- **Terms & Conditions:** Separate each key clause with a semicolon (`;`). Each clause will be generated into a distinct, enforceable legal covenant and itemized in Schedule A of Word documents.
- **Effective Date:** Provide date in format `Month DD, YYYY` (e.g. `April 10, 2025`) or standard date notation.
