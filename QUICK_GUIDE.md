# 🚀 Memory Mapping - Quick User Guide

## Getting Started

**Production URL**: https://d22o2tuls1800z.cloudfront.net

---

## Main Features

### 1. 📊 Dashboard
**What it does**: Overview of your entire system

**Features:**
- Project statistics
- Recent decisions
- Knowledge items count
- Quick navigation

**How to use:**
- Click "Dashboard" in the navigation
- View summary cards
- Click on any metric to explore details

---

### 2. 📁 Projects View

#### View All Projects
- See all your projects in a grid layout
- Filter by status: All, Active, Planning, Completed
- Sort by name or progress

#### Create New Project
1. Click "+ New Project" button (lime green)
2. Fill in:
   - Project Name (required)
   - Description (optional)
   - Status (Planning/Active/Completed)
3. Click "Create Project"

#### Delete a Project
1. Find the project card
2. Click the red trash icon (🗑️) in the top-right corner
3. Confirm deletion in the popup
4. Project is permanently removed

#### View Analytics
1. Click "View Analytics" button (blue with chart icon)
2. See comprehensive statistics:
   - Total/Active/Planning/Completed counts
   - Progress bars for all projects
   - Status distribution chart
   - Activity metrics (decisions, knowledge items, team members)
3. Close modal when done

---

### 3. 💬 Ask Memory (RAG Query)

**What it does**: Ask questions about your projects in natural language

**How to use:**
1. Click "Ask Memory" in navigation
2. Type your question in the chat input
3. Press Enter or click Send
4. View AI-generated answer with sources
5. Click on source references to see original documents

**Example Questions:**
- "Why was Feature X delayed in March?"
- "What decisions were made about the API redesign?"
- "Who worked on the mobile app project?"
- "What are the main challenges in the Platform Rebuild?"

**Features:**
- ChatGPT-style conversation interface
- Message history preserved
- Source references with links
- Confidence scores
- Auto-scrolling to latest message

---

### 4. 🕸️ Knowledge Graph

**What it does**: Visualize relationships between projects, decisions, people, and events

**How to use:**
1. Click "Knowledge Graph" in navigation
2. View interactive graph visualization
3. Drag nodes to rearrange
4. Zoom in/out with mouse wheel
5. Hover over nodes to see details
6. Click nodes to highlight connections

**Node Types:**
- 🟢 Projects (lime green)
- 🔵 Decisions (blue)
- 🟣 People (purple)
- 🟠 Artifacts (orange)

---

### 5. 📅 Decision Timeline

**What it does**: Track all decisions chronologically

**How to use:**
1. Click "Decision Timeline" in navigation
2. View decisions in chronological order
3. Filter by project (dropdown)
4. Filter by date range
5. Click on decision cards to see details
6. View source links for each decision

**Information Shown:**
- Decision title and description
- People involved
- Timestamp
- Associated project
- Source documents

---

### 6. 🤖 AI Assistant

**What it does**: Specialized AI help for different tasks

**How to use:**
1. Click "AI Assistant" in navigation
2. Choose a tab:
   - **Review Code**: Get code analysis and suggestions
   - **Explain Decision**: Understand why decisions were made
   - **Suggest Next Steps**: Get action recommendations
   - **Summarize Project**: Get project overview
3. Enter your request in the chat
4. View AI response with sources

**Features:**
- 4 specialized modes
- Separate conversation history per tab
- Source references
- ChatGPT-style interface

---

## Tips & Tricks

### 🎯 Best Practices

1. **Create Projects First**
   - Set up your projects before adding data
   - Use descriptive names and descriptions
   - Set appropriate status (Planning → Active → Completed)

2. **Ask Specific Questions**
   - Include project names in queries
   - Mention dates for time-specific questions
   - Reference people by name

3. **Use the Knowledge Graph**
   - Explore relationships visually
   - Find unexpected connections
   - Understand project dependencies

4. **Track Decisions**
   - Review the Decision Timeline regularly
   - Link decisions to projects
   - Include source references

5. **Monitor Analytics**
   - Check project progress regularly
   - Identify bottlenecks
   - Track team activity

### ⚡ Keyboard Shortcuts

- **Enter**: Send message in chat
- **Esc**: Close modals
- **Ctrl + Mouse Wheel**: Zoom in Knowledge Graph

### 🎨 Color Coding

**Project Status:**
- 🟢 Lime: Active projects
- 🔵 Blue: Planning projects
- ⚫ Gray: Completed projects

**UI Elements:**
- 🟢 Lime: Primary actions (Create, Submit)
- 🔵 Blue: Secondary actions (Analytics, View)
- 🔴 Red: Destructive actions (Delete)
- ⚫ Gray: Cancel actions

---

## Common Tasks

### Add New Data to the System

**Via API:**
```bash
curl -X POST https://1ud60s1obg.execute-api.us-east-1.amazonaws.com/prod/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "sourceType": "email",
    "content": "Your email content here...",
    "metadata": {
      "sourceRef": "https://mail.example.com/thread/123",
      "projectId": "your-project-id",
      "author": "user@example.com",
      "timestamp": "2024-03-20T10:00:00Z"
    }
  }'
```

### Query the System

**Via UI:**
1. Go to "Ask Memory"
2. Type your question
3. Get AI-powered answer with sources

**Via API:**
```bash
curl -X POST https://1ud60s1obg.execute-api.us-east-1.amazonaws.com/prod/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Why was Feature X delayed?"}'
```

### Export Project Data

**Current Method:**
- Use browser DevTools to copy data
- API calls return JSON format

**Future Enhancement:**
- Export to CSV/Excel
- PDF reports
- Automated backups

---

## Troubleshooting

### Issue: "No projects found"
**Solution**: Create a new project using the "+ New Project" button

### Issue: "Query returns no results"
**Solution**: 
- Make sure data has been ingested
- Try broader search terms
- Check if projects exist

### Issue: "Knowledge Graph is empty"
**Solution**: 
- Ingest data first
- Wait for graph updates to process
- Check Neptune connection

### Issue: "Delete button not working"
**Solution**: 
- Refresh the page
- Check browser console for errors
- Verify API endpoint is accessible

### Issue: "Analytics not showing data"
**Solution**: 
- Create projects first
- Refresh the page
- Check if projects have progress values

---

## Support & Resources

### Documentation
- `ARCHITECTURE.md` - System architecture
- `API_DOCUMENTATION.md` - Complete API reference
- `PROJECT_MANAGEMENT_FEATURES.md` - New features guide
- `MODEL_BENCHMARKS.md` - AI model performance

### API Endpoints
- **Base URL**: https://1ud60s1obg.execute-api.us-east-1.amazonaws.com/prod/
- **Query**: POST /query
- **Projects**: GET/POST /projects, DELETE /projects/{id}
- **Decisions**: GET /decisions
- **Graph**: POST /graph
- **Ingest**: POST /ingest

### AWS Resources
- **Region**: us-east-1
- **Account**: 140023380330
- **CloudFront**: https://d22o2tuls1800z.cloudfront.net

---

## What's New (Latest Update)

### Version 2.0.0 - March 9, 2026

✅ **Delete Projects**: Remove completed or unwanted projects
✅ **Project Analytics**: Comprehensive visualization dashboard
✅ **Improved UI**: Better layout and user experience
✅ **Status Distribution**: Visual chart of project statuses
✅ **Activity Metrics**: Track decisions, knowledge items, and team members

---

**Need Help?** Check the documentation files or contact your system administrator.

**Last Updated**: March 9, 2026
