from typing import Dict, Any
from app.database.session import engine
from sqlalchemy import text
import httpx
import asyncio
from app.core.config import settings


class HealthService:
    """
    Service for checking the health of various system components
    """
    
    async def check_database(self) -> Dict[str, Any]:
        """
        Check database connectivity
        """
        try:
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            return {"status": "connected", "message": "Database is accessible"}
        except Exception as e:
            return {"status": "error", "message": f"Database connection failed: {str(e)}"}
    
    async def check_scheduler(self) -> Dict[str, Any]:
        """
        Check scheduler status
        """
        # For now, just return a placeholder
        # In a real implementation, this would check the actual scheduler status
        return {"status": "running", "message": "Scheduler is operational"}
    
    async def check_github(self) -> Dict[str, Any]:
        """
        Check GitHub API connectivity
        """
        try:
            if not settings.github_token:
                return {"status": "warning", "message": "GitHub token not configured"}
            
            headers = {
                "Authorization": f"token {settings.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get("https://api.github.com/user", headers=headers)
                
                if response.status_code == 200:
                    return {"status": "connected", "message": "GitHub API is accessible"}
                else:
                    return {"status": "error", "message": f"GitHub API returned status {response.status_code}"}
        except Exception as e:
            return {"status": "error", "message": f"GitHub API connection failed: {str(e)}"}
    
    async def check_smtp(self) -> Dict[str, Any]:
        """
        Check SMTP connectivity
        """
        try:
            if not settings.smtp_host or not settings.smtp_user or not settings.smtp_password:
                return {"status": "warning", "message": "SMTP credentials not fully configured"}
            
            # For now, just check if the config is available
            # In a real implementation, we'd try to connect to the SMTP server
            return {"status": "configured", "message": "SMTP is configured"}
        except Exception as e:
            return {"status": "error", "message": f"SMTP configuration error: {str(e)}"}
    
    async def get_full_health_status(self) -> Dict[str, Any]:
        """
        Get comprehensive health status of all system components
        """
        # Run all health checks concurrently
        db_task = self.check_database()
        scheduler_task = self.check_scheduler()
        github_task = self.check_github()
        smtp_task = self.check_smtp()
        
        results = await asyncio.gather(
            db_task, scheduler_task, github_task, smtp_task,
            return_exceptions=True
        )
        
        # Process results
        health_status = {
            "database": results[0] if not isinstance(results[0], Exception) else {"status": "error", "message": str(results[0])},
            "scheduler": results[1] if not isinstance(results[1], Exception) else {"status": "error", "message": str(results[1])},
            "github": results[2] if not isinstance(results[2], Exception) else {"status": "error", "message": str(results[2])},
            "smtp": results[3] if not isinstance(results[3], Exception) else {"status": "error", "message": str(results[3])},
        }
        
        # Determine overall status
        overall_status = "healthy"
        for component, status_info in health_status.items():
            if status_info["status"] == "error":
                overall_status = "error"
                break
            elif status_info["status"] == "warning" and overall_status != "error":
                overall_status = "warning"
        
        health_status["overall"] = overall_status
        health_status["timestamp"] = asyncio.get_event_loop().time()
        
        return health_status