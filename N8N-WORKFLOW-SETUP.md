# N8N Meeting Summarizer Workflow Setup

## 🎯 **Overview**

This N8N workflow automatically processes audio recordings from the Meeting Recorder application and creates intelligent meeting summaries in Notion.

## 🔄 **Workflow Process**

```
Audio Recording → Transcription → AI Summary → Notion Page
     ↓               ↓              ↓            ↓
  Webhook         Google Gemini   Claude AI    Notion API
```

## 📋 **Workflow Components**

### 1. **Webhook Node** 🌐
- **Purpose**: Receives audio files from Meeting Recorder
- **Method**: POST
- **Authentication**: Basic Auth (matches Meeting Recorder config)
- **Binary Property**: `data`

### 2. **Google Gemini Transcription** 🎤
- **Purpose**: Converts audio to text
- **Model**: `gemini-2.0-flash-lite`
- **Input**: Binary audio file
- **Output**: Transcribed text

### 3. **Claude AI Summarization** 🤖
- **Purpose**: Creates intelligent meeting summaries
- **Model**: `claude-3-5-haiku-20241022`
- **Features**:
  - Names speakers
  - Highlights key points
  - Identifies action items
  - Special mentions (customizable)
  - Emoji formatting

### 4. **Notion Page Creation** 📝
- **Purpose**: Saves summary to Notion workspace
- **Title Format**: `Meeting Summary dd/MM/yyyy HH:mm`
- **Content**: AI-generated summary with rich formatting

## 🛠️ **Setup Instructions**

### **Prerequisites**
1. **N8N Instance**: Self-hosted or cloud
2. **API Keys**:
   - Google Gemini API key
   - Anthropic Claude API key
   - Notion API integration

### **Step 1: Import Workflow**
1. Open N8N workflow editor
2. Click "Import from file"
3. Select `n8n-meeting-summarizer-workflow.json`
4. Import the workflow

### **Step 2: Configure Credentials**

#### **Basic Auth (Webhook)**
1. Create Basic Auth credential
2. Set username/password (match Meeting Recorder config)
3. Assign to Webhook node

#### **Google Gemini API**
1. Get API key from [Google AI Studio](https://aistudio.google.com/)
2. Create "Google PaLM API" credential in N8N
3. Assign to "Transcribe a recording" node

#### **Anthropic Claude API**
1. Get API key from [Anthropic Console](https://console.anthropic.com/)
2. Create "Anthropic" credential in N8N
3. Assign to "Message a model" node

#### **Notion API**
1. Create Notion integration at [developers.notion.com](https://developers.notion.com/)
2. Get integration token
3. Share target Notion page with integration
4. Create "Notion" credential in N8N
5. Update page URL in "Create a page" node

### **Step 3: Customize Settings**

#### **Update Webhook URL**
1. Copy the webhook URL from N8N
2. Update `n8n_webhook_url` in Meeting Recorder's `config.json`

#### **Customize Summary Prompt**
Edit the Claude prompt in "Message a model" node:
```
**Special highlight whenever someone mentions me *[YOUR_NAME]***
```
Replace `[YOUR_NAME]` with your actual name.

#### **Update Notion Page**
Replace `https://www.notion.so/your-notion-page-id` with your actual Notion page URL.

## 🔧 **Configuration Example**

### **Meeting Recorder config.json**
```json
{
    "n8n_webhook_url": "https://your-n8n.com/webhook/your-webhook-id",
    "credentials": {
        "username": "your-username",
        "password": "your-password"
    },
    "watch_folder": "path/to/meeting-recorder/audio"
}
```

## ✅ **Features**

- **🎤 Audio Transcription**: High-quality speech-to-text
- **🤖 AI Summarization**: Intelligent meeting insights
- **👥 Speaker Identification**: Names who said what
- **📌 Action Items**: Automatically identifies next steps
- **🎯 Personal Mentions**: Highlights when you're mentioned
- **📝 Notion Integration**: Automatic documentation
- **⚡ Real-time Processing**: Instant summaries after recording

## 🎯 **Sample Output**

```markdown
# Meeting Summary 22/08/2025 14:30

## Summary
- Sean is working on feature XYZ and is blocked by task assigned to John 🔄
- John will finish his task this afternoon but needs code review first 👨‍💻
- Mark will work on a PoC about service bus 🚀

## Attention ⚠️
- You need to code review John's task to unblock Sean

## Taking Actions 📋
- Mark will work on PoC
- Schedule code review session
```

## 🔧 **Troubleshooting**

### **Common Issues**

1. **Webhook not receiving data**
   - Check webhook URL in Meeting Recorder config
   - Verify Basic Auth credentials match

2. **Transcription fails**
   - Verify Google Gemini API key
   - Check audio file format (should be WAV)

3. **Summary generation fails**
   - Verify Anthropic API key
   - Check Claude model availability

4. **Notion page creation fails**
   - Verify Notion integration token
   - Ensure page is shared with integration
   - Check page URL format

### **Testing the Workflow**
1. Use N8N's "Execute Workflow" with test audio file
2. Check each node's output
3. Verify Notion page creation

## 📚 **Additional Resources**

- [N8N Documentation](https://docs.n8n.io/)
- [Google Gemini API Docs](https://ai.google.dev/docs)
- [Anthropic Claude API Docs](https://docs.anthropic.com/)
- [Notion API Docs](https://developers.notion.com/)

---

**Ready to transform your meeting recordings into actionable insights!** 🎵✨📝
