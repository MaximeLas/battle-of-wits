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

## Development Log Protocol ⚠️ IMPORTANT
- **ALWAYS maintain DEVELOPMENT_LOG.md** - This file tracks all architectural decisions, issues, and solutions
- **READ the development log** at start of each session to understand current state and avoid repeating work
- **UPDATE the log** when making significant changes, encountering issues, or implementing new features
- **Document your reasoning** for architectural decisions and approaches taken
- **Include evidence** (logs, screenshots) when documenting issues
- This ensures continuity across Claude sessions and builds institutional knowledge

## UX Guidelines Protocol ⚠️ CRITICAL
- **ALWAYS consult UX_GUIDELINES.md** before making ANY user experience changes
- **READ the UX guidelines** when user reports UX issues or requests UX improvements
- **VERIFY all UX requirements** from the checklist before implementing changes
- **UPDATE UX_GUIDELINES.md** when making UX decisions or discovering new requirements
- **TEST against UX scenarios** defined in the guidelines after changes
- This prevents UX regressions and ensures consistent user experience across sessions

### When to Use UX_GUIDELINES.md:
1. **Before UI Changes**: Always check existing UX requirements first
2. **User Reports Issues**: Reference guidelines to understand expected behavior  
3. **New Features**: Ensure new features align with established UX principles
4. **Bug Fixes**: Verify fixes don't break other UX requirements
5. **Testing**: Use defined test scenarios to validate changes

## Current Status  
- ✅ Background processing architecture implemented (see DEVELOPMENT_LOG.md)
- ✅ Manual advance debate system with user-controlled pacing
- ✅ Enhanced token/cost tracking for Chat + TTS APIs
- ✅ Comprehensive UX guidelines established (see UX_GUIDELINES.md)
- ✅ All major UX issues resolved: proper completion logic, user feedback, button states
- **SYSTEM STATUS**: Fully functional manual advance debate system ready for use