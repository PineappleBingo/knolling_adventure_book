"""
Agent Golf: Production Analyst (Tracking)
Mission: Maintain the "Mission Control" Google Sheet.
"""

import logging
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

logger = logging.getLogger("AgentGolf")

class AgentGolf:
    def __init__(self):
        self.scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        self.creds_file = "credentials.json"
        self.client = None
        self.sheet = None
        
        try:
            self.creds = ServiceAccountCredentials.from_json_keyfile_name(self.creds_file, self.scope)
            self.client = gspread.authorize(self.creds)
            # Open the first sheet of the "Mission Control" spreadsheet
            # Note: The user must share the sheet with the service account email
            self.sheet = self.client.open("Mission Control").sheet1
            logger.info("Agent Golf initialized and connected to Mission Control.")
        except Exception as e:
            logger.error(f"Failed to connect to Google Sheets: {e}")
            # We don't raise here to allow the app to start even if sheets fails, 
            # but in production this might be critical.

    def start_job(self, run_id, theme):
        """
        Initializes a new job in the tracking sheet.
        Row Structure: [RunID, Date, Theme, Status, Images_Passed, Drive_Link]
        """
        if not self.sheet:
            logger.warning("Tracking disabled: No connection to sheets.")
            return

        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [run_id, date_str, theme, "STARTED", 0, ""]
        try:
            self.sheet.append_row(row)
            logger.info(f"Job {run_id} started and logged.")
        except Exception as e:
            logger.error(f"Failed to log start_job: {e}")

    def update_progress(self, run_id, status, images_passed=None):
        """
        Updates the status and images passed for a job.
        Note: This is a simplified implementation. In a real scenario, 
        we'd need to find the row by run_id first.
        """
        if not self.sheet:
            return

        try:
            # Find the row with the given run_id
            cell = self.sheet.find(run_id)
            if cell:
                # Update Status (Column 4)
                self.sheet.update_cell(cell.row, 4, status)
                # Update Images Passed (Column 5) if provided
                if images_passed is not None:
                    self.sheet.update_cell(cell.row, 5, images_passed)
                logger.info(f"Job {run_id} updated: {status}")
            else:
                logger.warning(f"Job {run_id} not found in sheet.")
        except Exception as e:
            logger.error(f"Failed to update progress: {e}")

    def finish_job(self, run_id, drive_link):
        """
        Marks the job as finished and adds the Drive link.
        """
        if not self.sheet:
            return

        try:
            cell = self.sheet.find(run_id)
            if cell:
                self.sheet.update_cell(cell.row, 4, "COMPLETED")
                self.sheet.update_cell(cell.row, 6, drive_link)
                logger.info(f"Job {run_id} finished.")
            else:
                logger.warning(f"Job {run_id} not found.")
        except Exception as e:
            logger.error(f"Failed to finish job: {e}")
