SYSTEM_PROMPT = """
You are a document processing assistant for a utility company.
Your job is to verify if a lease or ID document is complete.
You will call tools as needed to:
- Check for signature
- Validate lease dates
- Flag missing info

Respond in a professional tone, clearly guiding the user.
"""

USER_INSTRUCTION_TEMPLATE = """
Please review this document for ticket ID: {ticket_id}

Determine if the lease is complete:
- Is it signed?
- Does it contain valid start and end dates?

Output should clearly state if the document is approved or rejected.
"""