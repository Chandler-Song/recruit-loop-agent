import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
from app.core.exceptions import SMTPException
from app.repositories.outreach_log import OutreachLogRepository
from app.models.outreach_log import OutreachLog
from app.schemas.outreach_log import OutreachLogCreate
import asyncio
from typing import Optional
import uuid


class EmailService:
    """
    Service for sending emails to candidates
    """
    
    def __init__(self, outreach_log_repo: OutreachLogRepository):
        self.outreach_log_repo = outreach_log_repo
        self.smtp_host = settings.smtp_host
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.smtp_port = settings.smtp_port
        self.sender_email = settings.EMAIL_FROM
    
    async def send_email(self, recipient_email: str, subject: str, body: str, pipeline_id: uuid.UUID) -> bool:
        """
        Send an email to a candidate and log the result
        """
        # Create the outreach log entry
        outreach_log_data = OutreachLogCreate(
            pipeline_id=pipeline_id,
            subject=subject,
            body=body,
            status="pending"
        )
        
        outreach_log = await self.outreach_log_repo.create(outreach_log_data)
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            # Add body to email
            msg.attach(MIMEText(body, 'html'))
            
            # Create SMTP session
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()  # Enable encryption
            server.login(self.smtp_user, self.smtp_password)
            
            # Send email
            text = msg.as_string()
            server.sendmail(self.sender_email, recipient_email, text)
            server.quit()
            
            # Update outreach log status to sent
            await self.outreach_log_repo.update_status(outreach_log.id, "sent")
            
            return True
            
        except Exception as e:
            # Update outreach log status to failed
            await self.outreach_log_repo.update_status_with_error(outreach_log.id, "failed", str(e))
            raise SMTPException(f"Failed to send email: {str(e)}")
    
    async def send_bulk_emails(self, recipients: list, subject: str, body: str) -> dict:
        """
        Send bulk emails and return statistics
        """
        stats = {
            "total": len(recipients),
            "sent": 0,
            "failed": 0
        }
        
        for recipient in recipients:
            try:
                success = await self.send_email(recipient["email"], subject, body, recipient["pipeline_id"])
                if success:
                    stats["sent"] += 1
                else:
                    stats["failed"] += 1
            except Exception:
                stats["failed"] += 1
                
            # Small delay to avoid overwhelming the SMTP server
            await asyncio.sleep(1)
        
        return stats
    
    def generate_email_template(self, candidate_name: str, position_title: str, company_name: str) -> str:
        """
        Generate a personalized email template
        """
        template = f"""
        <html>
        <body>
            <p>Dear {candidate_name},</p>
            
            <p>I came across your profile on GitHub and noticed your expertise in technologies that align with our current opening for a {position_title} at {company_name}. Given your impressive contributions, I thought this opportunity might interest you.</p>
            
            <p>We are looking for someone with skills in {position_title.split()[0] if position_title else 'software development'} and would love to discuss how you could contribute to our team.</p>
            
            <p>Would you be interested in learning more about this opportunity?</p>
            
            <p>Best regards,<br/>
            Recruiting Loop Agent</p>
        </body>
        </html>
        """
        return template