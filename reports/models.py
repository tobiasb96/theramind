from core.models import BaseDocument


class Report(BaseDocument):
    class Meta:
        verbose_name = "Report"
        verbose_name_plural = "Reports"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

    @property
    def has_context(self):
        """Check if report has any inputs"""
        return self.all_inputs["total_count"] > 0

    @property
    def context_files_count(self):
        """Get count of all inputs (backward compatibility)"""
        return self.all_inputs["total_count"]
