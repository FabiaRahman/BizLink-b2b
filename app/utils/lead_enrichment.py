from sqlalchemy.orm import Session
from datetime import datetime
import re

from app.models.lead import Lead, LeadStatus

class LeadEnrichmentService:
    """Enrich lead with metadata: domain extraction, phone formatting, lead scoring"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def enrich_lead(self, lead_id: int) -> Lead:
        lead = self.db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            return None
        
        # Extract email domain
        domain = self._extract_domain(lead.email)
        
        # Format phone
        if lead.phone:
            lead.phone = self._format_phone(lead.phone)
        
        # Calculate lead score
        score = self._calculate_score(lead, domain)
        
        # Update status
        lead.status = LeadStatus.enriched
        lead.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(lead)
        return lead
    
    def _extract_domain(self, email: str) -> str:
        try:
            return email.split('@')[1].lower()
        except:
            return "unknown"
    
    def _format_phone(self, phone: str) -> str:
        cleaned = re.sub(r'[^\d+]', '', phone)
        return cleaned if len(cleaned) >= 10 else phone
    
    def _calculate_score(self, lead: Lead, domain: str) -> int:
        score = 0
        if lead.name: score += 20
        if lead.phone and len(lead.phone) >= 10: score += 15
        if lead.company: score += 15
        if lead.area_of_interest: score += 10
        if lead.source_url: score += 10
        
        # Business email bonus
        free_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
        if domain not in free_domains:
            score += 10
        
        return score