from typing import List, Optional
from pydantic import BaseModel, Field


class TicketAnalysis(BaseModel):
    customer_name: Optional[str] = Field(
        description="Customer name if identified in the ticket, else null"
    )
    customer_email: Optional[str] = Field(
        description="Customer email if identified, else null"
    )
    intent: str = Field(
        description="Primary intent category (e.g., Billing & Refunds, Technical Bug, Account Access, Feature Request, General Inquiry)"
    )
    sentiment: str = Field(
        description="Customer sentiment (e.g., Frustrated, Angry, Neutral, Satisfied)"
    )
    urgency_score: float = Field(
        description="Urgency score from 0.0 to 1.0 based on business impact and tone"
    )
    priority_queue: str = Field(
        description="Assigned priority queue: P0-Critical, P1-High, P2-Normal, or P3-Low"
    )
    confidence_score: float = Field(
        description="Model confidence score in the intent and priority classification from 0.0 to 1.0"
    )
    key_entities: List[str] = Field(
        description="Extracted key technical entities, error codes, invoice IDs, or product features mentioned"
    )
    summary: str = Field(
        description="Brief 1-sentence executive summary of the customer's issue"
    )
    suggested_response: str = Field(
        description="A professional, empathetic draft response template tailored to resolve or acknowledge the ticket"
    )
