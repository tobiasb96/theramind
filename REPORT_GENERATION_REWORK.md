# Report Generation Feature Rework

## Overview

The report generation feature has been completely reworked to provide a more flexible and intuitive workflow. Previously, reports were tied to therapy sessions and required session notes as input. The new system allows users to:

- Create reports independently of sessions
- Upload various file types (PDF, Word, TXT) as context
- Add manual text input as context
- Generate reports using AI templates based on the provided context
- Manage context files similar to audio recordings in sessions

## Key Changes

### 1. Model Changes

#### Report Model
- **Removed**: `sessions` ManyToMany field
- **Modified**: `content` field now allows blank values
- **Added**: Properties for context management (`has_context`, `context_files_count`)

#### New ReportContextFile Model
- Stores uploaded files and their extracted text
- Supports multiple file types: PDF, Word, TXT, and manual text input
- Tracks extraction success/failure with error messages
- Provides helper methods for display and file management

### 2. Service Layer Updates

#### New TextExtractionService
- Handles text extraction from various file formats
- Uses PyPDF2 for PDF files
- Uses python-docx for Word documents
- Provides text cleaning and validation
- Graceful error handling for unsupported formats

#### Updated ReportService
- Reworked to use context files instead of session transcriptions
- New methods: `add_context_file()`, `add_context_text()`, `get_context_summary()`
- Updated `generate_with_template()` to build context from files
- Enhanced error handling and logging

### 3. New Workflow

#### Report Creation Process
1. User creates a new report with basic information (title, template)
2. System redirects to report detail view
3. User can:
   - Upload files (PDF, Word, TXT)
   - Add manual text input
   - View context summary and file previews
4. User selects a template and generates report content
5. User can edit generated content and save

#### Context Management
- Files are automatically processed for text extraction
- Failed extractions are logged with error messages
- Users can preview extracted text
- Context files can be deleted individually
- System provides summary statistics

### 4. User Interface

#### New Report Detail View
- **Context Summary**: Shows file count, extraction success rate, and text length
- **Context Files Section**: Lists all uploaded files with previews
- **Report Generation Section**: Template selection and generation controls
- **Content Editor**: Rich text editor for report content
- **Modals**: File upload and text input modals

#### Updated Forms
- Simplified report creation form (removed sessions field)
- New context file upload form
- New manual text input form

### 5. API Endpoints

#### New Context Management Endpoints
- `POST /reports/{id}/upload-context-file/` - Upload file
- `POST /reports/{id}/add-context-text/` - Add manual text
- `POST /reports/{id}/delete-context-file/` - Delete context file

#### Updated Generation Endpoints
- `POST /reports/{id}/generate-content/` - Generate report content
- `POST /reports/{id}/save-content/` - Save report content

## Technical Implementation

### Dependencies Added
- `PyPDF2` - PDF text extraction
- `python-docx` - Word document processing

### File Storage
- Context files stored in `media/report_context/YYYY/MM/DD/`
- Automatic cleanup on file deletion
- File size tracking and display

### Error Handling
- Comprehensive logging for text extraction failures
- Graceful degradation for unsupported file types
- User-friendly error messages

## Usage Examples

### Creating a Report with Context Files

```python
# Create report
report = Report.objects.create(title="Patient Assessment Report")

# Add context files
report_service = ReportService()
context_file = report_service.add_context_file(report, uploaded_file)

# Add manual text
text_context = report_service.add_context_text(
    report, 
    "Patient showed improvement in anxiety levels...", 
    "Session Notes 2024-01-15"
)

# Generate report
template = DocumentTemplate.objects.get(name="Assessment Report")
generated_content = report_service.generate_with_template(report, template)
```

### Context Summary

```python
# Get context summary
summary = report_service.get_context_summary(report)
print(f"Total files: {summary['total_files']}")
print(f"Successful extractions: {summary['successful_extractions']}")
print(f"Total text length: {summary['total_text_length']}")
```

## Migration Guide

### Database Migration
Run the migration to update the database schema:
```bash
python manage.py migrate
```

### Template Updates
Update any custom templates that reference the old session-based workflow.

### Dependencies
Install new dependencies:
```bash
pip install PyPDF2 python-docx
```

## Benefits

1. **Flexibility**: Reports no longer tied to sessions
2. **Multiple Input Sources**: Support for various file types
3. **Better UX**: Intuitive workflow similar to session management
4. **Scalability**: Easy to add new file type support
5. **Reliability**: Robust error handling and logging
6. **Maintainability**: Clear separation of concerns

## Future Enhancements

1. **OCR Support**: Extract text from scanned documents
2. **Batch Processing**: Upload multiple files at once
3. **File Versioning**: Track changes to context files
4. **Smart Categorization**: Automatically categorize context files
5. **Integration**: Connect with external document systems

## Testing

The system includes comprehensive error handling and logging. Test scenarios:

1. Upload supported file types (PDF, Word, TXT)
2. Upload unsupported file types
3. Upload corrupted files
4. Add manual text input
5. Generate reports with various templates
6. Edit and save generated content

## Support

For issues related to file extraction:
- Check logs for detailed error messages
- Verify file format compatibility
- Ensure files are not corrupted or password-protected