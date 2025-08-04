# 🔧 Error Handling & Debugging Guide

## Overview
Battle of Wits now has comprehensive error handling that provides clear, actionable feedback when things go wrong. No more cryptic error messages or lengthy debugging sessions!

## 📋 What We've Built

### 1. **Smart Error Categories**
- `CONFIGURATION` - Setup and environment issues
- `API_AUTHENTICATION` - OpenAI API key problems  
- `API_CONNECTION` - Network/connectivity issues
- `API_QUOTA` - Usage limits and rate limiting
- `DEBATE_LOGIC` - Issues with debate flow
- `AUDIO_PROCESSING` - TTS generation problems

### 2. **User-Friendly Error Messages**
Instead of: `Exception: API key not found`
You get: 
```
❌ OpenAI API key is missing

💡 Suggestions:
  • Create a .env file in your project root
  • Add OPENAI_API_KEY=your_api_key_here to the .env file
  • Copy .env.example to .env and edit it with your key
  • Get your API key from https://platform.openai.com/api-keys
```

### 3. **Comprehensive Logging**
- **Console logs**: Clean, timestamped messages during development
- **File logs**: Detailed technical logs with function names and line numbers
- **Automatic log rotation**: Daily log files in `logs/` directory

### 4. **System Status Monitoring**
The UI shows real-time system status:
- ✅ OpenAI API Connected
- ✅ Environment Configured
- Last checked: 04:04:53

## 🎯 Common Error Scenarios & Solutions

### Missing API Key
**What you'll see:** Clear message about missing API key with step-by-step setup instructions
**Quick fix:** Copy `.env.example` to `.env` and add your API key

### Invalid API Key Format
**What you'll see:** Message about invalid format with format requirements
**Quick fix:** Ensure your key starts with `sk-` and has no extra spaces

### Network Issues
**What you'll see:** Connection error with troubleshooting steps
**Quick fix:** Check internet connection and OpenAI service status

### Rate Limiting
**What you'll see:** Quota exceeded message with usage check instructions
**Quick fix:** Wait a few minutes or check your OpenAI account limits

### Debate Flow Issues
**What you'll see:** Specific error about which part of the debate failed
**Quick fix:** Usually resolved by restarting the debate

## 🔍 Debugging Tools

### 1. **Error Details Expander**
Each error shows technical details in a collapsible section for debugging

### 2. **Log Files**
Check `logs/battle_of_wits_YYYYMMDD.log` for detailed technical information

### 3. **System Status Panel**
Real-time status indicators in the sidebar show what's working

### 4. **Test Scripts**
- `python test_setup.py` - Basic functionality test
- `python test_error_handling.py` - Error handling demonstration

## 🚀 Testing Your Setup

```bash
# Basic setup test
python test_setup.py

# Error handling test
python test_error_handling.py

# Full application
streamlit run main.py
```

## 📞 When Things Still Go Wrong

If you encounter an error that isn't handled well:

1. **Check the log file** in `logs/` for technical details
2. **Look for the error category** to understand the type of issue
3. **Follow the suggestions** provided in the error message
4. **Check the system status** panel for component health

The error handling system captures most common issues and provides clear guidance for resolution. This should eliminate most debugging headaches! 🎉