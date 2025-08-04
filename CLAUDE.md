# Battle of Wits - AI vs AI Debate Application

## Project Overview
Building an open-source tool where two AI agents engage in structured, multi-turn debates with real-time voice output. Users pick topics, define stances, and watch AI agents debate in various formats.

## Architecture Decisions Made

### Tech Stack
- **Frontend**: Streamlit (chosen over React for faster MVP development)
- **AI Integration**: OpenAI Chat API + TTS API (not Realtime API for better control)
- **Voice**: OpenAI TTS API for speech synthesis
- **Language**: Python

### Key Design Choices
1. **Text Generation + TTS** over Realtime API for:
   - Better control over debate structure and turn-taking
   - Lower cost
   - Easier implementation in Streamlit
   - Full transcript capabilities

2. **Streamlit** over React for:
   - Faster prototyping
   - Native Python integration with OpenAI
   - Built-in session state for real-time updates
   - Audio component support

## Planned Features
- 🗣️ Real-time AI voice output using OpenAI TTS
- 🔄 Structured multi-turn debates with customizable stances
- 🎭 Multiple debate formats: Formal, Casual, Rapid Fire, Roleplay
- 📄 Full transcript view (text + voice)
- ⚙️ Configurable debate parameters

## Development Plan
See todo list for current implementation roadmap. Priority is:
1. Basic project structure
2. Core debate engine
3. OpenAI integration
4. Streamlit UI
5. Multiple debate formats

## Context7 MCP Setup
- User has Context7 MCP server configured for up-to-date API documentation
- Use Context7 to get current OpenAI API docs and best practices
- Command used: `claude mcp add --transport http context7 https://mcp.context7.com/mcp`

## Working Notes
- This is user's first major Claude Code project - prioritize clear communication and structured approach
- User wants to learn effective collaboration patterns
- Focus on incremental progress with working demos at each stage
- Always run lint/typecheck commands before considering tasks complete

## Current Status
- Repository initialized with README and LICENSE
- Architecture and tech stack decided
- Ready to begin implementation starting with project structure