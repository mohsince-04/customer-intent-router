The **Automated Customer Support Intent & Sentiment Router** is an enterprise-grade customer support triage and routing CLI tool.

![Summary](https://github.com/user-attachments/assets/7eac9f7d-68bf-4fca-9c5d-854175bfdf14 "Note: Ignore vepython, it's just an alias.")

Instead of manual ticket sorting or basic keyword rules, this tool uses **Gemini 2.5 Flash** to perform deep natural language understanding on incoming support tickets. It extracts key details, analyzes customer sentiment and urgency, determines the appropriate priority queue (`P0-Critical` down to `P3-Low`), extracts technical identifiers (like error codes or account IDs), and automatically drafts an empathetic, professional response template for support agents.

---

### Breakdown of Each File

The project relies on two main Python files and a sample input file:

#### 1. `schemas.py` (The Data Contract & Output Schema)

This file uses **Pydantic V2** to define the exact data model (`TicketAnalysis`) required for the Gemini API response. By passing this schema into Gemini's `response_schema`, it guarantees that the output will be strictly validated JSON matching our exact specifications every single time.

* **Fields Captured:** `customer_name`, `customer_email`, `intent`, `sentiment`, `urgency_score`, `priority_queue`, `confidence_score`, `key_entities`, `summary`, and `suggested_response`.

---

#### 2. `router.py` (The Core CLI Engine)

This file handles the application logic, file parsing, API interaction, error handling, and terminal UI rendering.

* **File & Text Extraction:** Checks if the provided ticket input is a file path and reads it, or treats it as an inline text string.
* **Gemini API Integration:** Sends the ticket content to `gemini-2.5-flash` with strict JSON constraints and a system prompt tailored for enterprise triage.
* **Stderr Redirection:** Wraps the API call in a `sys.stderr` suppression block to keep the terminal output clean and free of background SDK warning prints.
* **Rich Terminal UI:** Leverages Python's `rich` library to render a color-coded triage dashboard, complete with priority badges, confidence percentages, extracted entity tags, and a formatted response draft panel.

---

#### 3. `ticket.txt` (Sample Input File)

A local text file containing a simulated incoming support email or ticket (e.g., reporting a production server crash with error code `ERR_STRIPE_503`), used as input for testing the CLI router.
