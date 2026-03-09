# 📁 File Upload Feature - Complete Documentation

## Overview

Users can now upload files (documents, images, code, etc.) to projects, creating a complete project container with all related files stored securely in AWS S3.

---

## ✅ What's Deployed

### Backend
- ✅ S3 Bucket: `memory-mapping-documents-140023380330`
- ✅ Lambda Function: `FileUploadHandler`
- ✅ API Endpoints: POST/GET/DELETE for file management
- ✅ DynamoDB metadata storage
- ✅ CORS configuration for browser uploads

### Frontend
- ✅ File upload modal in Projects View
- ✅ Drag-and-drop interface
- ✅ File list with download/delete options
- ✅ File size display
- ✅ Upload progress indicator

---

## 🎯 Features

### 1. Upload Files to Projects
- Click "Manage Files" button on any project card
- Drag and drop files or click to browse
- Supports all file types:
  - Documents (PDF, DOCX, TXT, MD)
  - Images (PNG, JPG, GIF, SVG)
  - Code files (JS, PY, JAVA, etc.)
  - Archives (ZIP, TAR, GZ)
  - Any other file type

### 2. View Project Files
- See all files uploaded to a project
- Display file name, size, and upload date
- Files organized in a clean list view

### 3. Download Files
- Click download icon to get the file
- Secure presigned URLs (valid for 1 hour)
- Original filename preserved

### 4. Delete Files
- Remove files you no longer need
- Confirmation dialog prevents accidents
- Deletes from both S3 and metadata

---

## 📖 How to Use

### Upload a File

1. **Navigate to Projects View**
   - Go to the Projects page
   - Find the project you want to add files to

2. **Open File Manager**
   - Click the "Manage Files" button (blue button at bottom of project card)
   - File management modal opens

3. **Upload File**
   - Click the upload area or drag and drop a file
   - Wait for upload to complete
   - File appears in the list below

4. **Upload Multiple Files**
   - Repeat the process for each file
   - No limit on number of files per project

### Download a File

1. **Open File Manager**
   - Click "Manage Files" on the project card

2. **Click Download Icon**
   - Blue download icon next to each file
   - File downloads to your browser's download folder

### Delete a File

1. **Open File Manager**
   - Click "Manage Files" on the project card

2. **Click Delete Icon**
   - Red trash icon next to each file
   - Confirm deletion in the popup
   - File is permanently removed

---

## 🔧 Technical Details

### API Endpoints

#### Upload File
```
POST /files
```

**Request Body:**
```json
{
  "projectId": "uuid",
  "fileName": "document.pdf",
  "fileContent": "base64-encoded-content",
  "fileType": "application/pdf",
  "description": "Project documentation"
}
```

**Response:**
```json
{
  "fileId": "uuid",
  "fileName": "document.pdf",
  "fileSize": 1024000,
  "downloadUrl": "https://s3.amazonaws.com/...",
  "uploadedAt": "2026-03-09T13:00:00Z"
}
```

#### List Project Files
```
GET /files/project/{projectId}
```

**Response:**
```json
{
  "files": [
    {
      "entityId": "file-uuid",
      "fileName": "document.pdf",
      "fileSize": 1024000,
      "fileType": "application/pdf",
      "uploadedAt": "2026-03-09T13:00:00Z",
      "downloadUrl": "https://s3.amazonaws.com/...",
      "description": "Project documentation"
    }
  ],
  "count": 1
}
```

#### Delete File
```
DELETE /files/{fileId}
```

**Response:**
```json
{
  "message": "File deleted successfully",
  "fileId": "uuid",
  "fileName": "document.pdf"
}
```

### Storage Architecture

```
S3 Bucket Structure:
memory-mapping-documents-140023380330/
├── projects/
│   ├── project-id-1/
│   │   ├── file-id-1/
│   │   │   └── document.pdf
│   │   ├── file-id-2/
│   │   │   └── image.png
│   ├── project-id-2/
│   │   ├── file-id-3/
│   │   │   └── code.py
```

### Metadata Storage (DynamoDB)

```json
{
  "entityId": "file-uuid",
  "entityType": "file",
  "projectId": "project-uuid",
  "fileName": "document.pdf",
  "fileType": "application/pdf",
  "fileSize": 1024000,
  "s3Key": "projects/project-id/file-id/document.pdf",
  "s3Bucket": "memory-mapping-documents-140023380330",
  "description": "Project documentation",
  "uploadedAt": "2026-03-09T13:00:00Z"
}
```

---

## 🔒 Security

### Access Control
- Files are private by default
- Access via presigned URLs only
- URLs expire after 1 hour
- CORS configured for browser uploads

### File Validation
- File size limits enforced by Lambda (512MB max)
- Base64 encoding validation
- Metadata validation before storage

### Data Protection
- S3 server-side encryption enabled
- Bucket versioning enabled
- HTTPS-only access

---

## 💡 Use Cases

### 1. Project Documentation
- Upload requirements documents
- Store design specifications
- Keep meeting notes

### 2. Code Repositories
- Upload source code files
- Store configuration files
- Keep build scripts

### 3. Design Assets
- Upload mockups and wireframes
- Store brand assets
- Keep design files

### 4. Data Files
- Upload datasets
- Store analysis results
- Keep reports

### 5. Reference Materials
- Upload research papers
- Store API documentation
- Keep tutorials

---

## 📊 File Management Best Practices

### Organization
1. **Use Descriptive Names**
   - Name files clearly: `requirements-v2.pdf` not `doc.pdf`
   - Include version numbers when relevant
   - Use consistent naming conventions

2. **Add Descriptions**
   - Describe the file's purpose
   - Note important details
   - Include context for team members

3. **Regular Cleanup**
   - Delete outdated files
   - Archive completed project files
   - Keep only relevant documents

### Performance
1. **File Sizes**
   - Compress large files before upload
   - Use appropriate formats (PDF for docs, PNG for images)
   - Consider splitting very large files

2. **Batch Operations**
   - Upload multiple files in sequence
   - Wait for each upload to complete
   - Check file list after uploads

---

## 🎨 UI Components

### File Upload Modal

**Header:**
- Project name display
- Close button (X)

**Upload Section:**
- Drag-and-drop area
- Click to browse
- Upload progress indicator
- File type icons

**Files List:**
- File name and icon
- File size (formatted)
- Upload date
- Download button (blue)
- Delete button (red)

**Empty State:**
- File icon
- "No files uploaded yet" message
- Helpful prompt to upload first file

---

## 🚀 Future Enhancements

### Planned Features
1. **File Preview**
   - View PDFs in browser
   - Image thumbnails
   - Code syntax highlighting

2. **Bulk Operations**
   - Upload multiple files at once
   - Bulk download as ZIP
   - Bulk delete

3. **File Versioning**
   - Track file versions
   - View version history
   - Restore previous versions

4. **File Sharing**
   - Generate shareable links
   - Set expiration dates
   - Track downloads

5. **File Search**
   - Search by filename
   - Filter by file type
   - Sort by date/size

6. **File Processing**
   - Automatic text extraction
   - Image optimization
   - Document indexing for search

7. **Integrations**
   - Google Drive sync
   - Dropbox integration
   - GitHub repository links

---

## 🐛 Troubleshooting

### Issue: "Failed to upload file"
**Solutions:**
- Check file size (must be < 512MB)
- Verify internet connection
- Try a different browser
- Check browser console for errors

### Issue: "Download URL expired"
**Solutions:**
- Refresh the file list
- URLs are regenerated on each page load
- Valid for 1 hour from generation

### Issue: "File not appearing in list"
**Solutions:**
- Refresh the page
- Check if upload completed successfully
- Verify you're viewing the correct project

### Issue: "Cannot delete file"
**Solutions:**
- Check if you have permissions
- Refresh the page and try again
- Verify file still exists

---

## 📝 API Examples

### Upload with cURL
```bash
# First, base64 encode your file
base64 document.pdf > document.b64

# Then upload
curl -X POST https://1ud60s1obg.execute-api.us-east-1.amazonaws.com/prod/files \
  -H "Content-Type: application/json" \
  -d '{
    "projectId": "your-project-id",
    "fileName": "document.pdf",
    "fileContent": "'"$(cat document.b64)"'",
    "fileType": "application/pdf"
  }'
```

### Upload with JavaScript
```javascript
// Read file as base64
const fileInput = document.getElementById('fileInput');
const file = fileInput.files[0];

const reader = new FileReader();
reader.onload = async (e) => {
  const base64Content = e.target.result.split(',')[1];
  
  const response = await axios.post(`${API_BASE}/files`, {
    projectId: 'your-project-id',
    fileName: file.name,
    fileContent: base64Content,
    fileType: file.type
  });
  
  console.log('Uploaded:', response.data);
};
reader.readAsDataURL(file);
```

### List Files with Python
```python
import requests

API_BASE = 'https://1ud60s1obg.execute-api.us-east-1.amazonaws.com/prod'
project_id = 'your-project-id'

response = requests.get(f'{API_BASE}/files/project/{project_id}')
files = response.json()['files']

for file in files:
    print(f"{file['fileName']} - {file['fileSize']} bytes")
```

---

## 📈 Monitoring

### CloudWatch Metrics
- Lambda invocations
- S3 PUT/GET requests
- DynamoDB read/write units
- API Gateway requests

### Logs
- Lambda execution logs: `/aws/lambda/FileUploadHandler`
- S3 access logs (if enabled)
- API Gateway access logs

---

## 💰 Cost Considerations

### S3 Storage
- $0.023 per GB/month (Standard storage)
- First 5GB free (12 months)

### Lambda
- $0.20 per 1M requests
- $0.0000166667 per GB-second
- First 1M requests free/month

### Data Transfer
- First 100GB free/month
- $0.09 per GB after that

### Estimated Costs
- 100 files (10MB each) = 1GB storage = $0.023/month
- 1000 uploads/month = $0.20
- Total: ~$0.25/month for typical usage

---

**Last Updated**: March 9, 2026
**Version**: 3.0.0
**Status**: ✅ PRODUCTION READY

**Live Application**: https://d22o2tuls1800z.cloudfront.net
