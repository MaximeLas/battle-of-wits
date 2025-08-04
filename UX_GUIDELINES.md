# Battle of Wits - UX Guidelines & Requirements

## Purpose
This document defines the agreed-upon user experience for the Battle of Wits application. **All Claude sessions must reference this file before making UX-related changes** to ensure consistency and prevent regressions.

---

## 🎯 Core UX Principles

### 1. **User Control First**
- Users should have full control over debate pacing
- No forced navigation or automatic state changes without user consent
- Clear feedback for all user actions

### 2. **Progressive Disclosure**
- Show relevant information at the right time
- Don't overwhelm users with unnecessary details
- Provide clear status indicators

### 3. **Graceful Degradation**
- Handle errors gracefully without breaking the experience
- Provide clear recovery paths
- Never leave users in a broken state

---

## 📋 Detailed UX Requirements

### **Debate Setup Phase**

#### ✅ **REQUIRED BEHAVIOR**
- **Setup Form**: Single-page form with topic, positions, and advanced settings
- **Manual Mode Only**: No auto-advance options (simplified for better UX)  
- **Validation**: Clear error messages for missing required fields
- **Submission**: "🚀 Start Debate" button initiates background processing

#### ❌ **FORBIDDEN BEHAVIOR**
- Auto-advance configuration options
- Complex timing settings that confuse users
- Starting debate without proper validation

---

### **Debate Execution Phase**

#### ✅ **REQUIRED BEHAVIOR**

**First Turn Auto-Start**:
- First response auto-displays when ready (no manual trigger needed)
- Status message: "🚀 Debate starting - generating first response..."
- Seamless transition to manual control after first turn

**Manual Advancement**:
- "➡️ Next Turn" button when content is ready (primary, enabled)
- "⏳ Generating..." button when content NOT ready (secondary, disabled)
- "🔄 Check Again" button available when generating for impatient users

**User Feedback**:
- ✅ Content ready: "✅ Next turn ready! Click 'Next Turn' to continue."
- ⏳ Still generating: "⏳ Generating next response in background..."
- ❌ Click when not ready: "⏳ Next turn is still being generated, please wait..."

**Content Presentation**:
- Each turn displays: transcript text + audio player
- Audio auto-plays when turn is presented
- Previous turns remain visible in scrollable transcript
- Current turn is clearly distinguished in transcript

**Progress Indicators**:
- Progress bar shows current turn / total turns
- Turn counter: "Turn X of Y"
- Debater identification: "Next Speaker: Debater A 🔵"
- Token usage and cost tracking visible

#### ❌ **FORBIDDEN BEHAVIOR**
- Audio interruption by automatic advancement
- Hiding previous turns from transcript
- Unclear button states or missing feedback
- Forced progression without user consent

---

### **Debate Completion Phase**

#### ✅ **REQUIRED BEHAVIOR**

**Completion Logic**:
- Debate runs exactly `max_turns * 2` messages (e.g., 4 turns each = 8 total)
- Completion triggered only by reaching max messages OR user stopping
- NO automatic return to setup form

**Completion UI**:
- "🎉 Debate Complete!" message with celebration (balloons)
- Full transcript and audio remain visible
- Summary statistics displayed
- Controls: "🔄 New Debate" (primary) + "📤 Export Transcript" (secondary)

**Post-Completion**:
- User controls when to start new debate
- All content remains accessible until user chooses to leave
- No data loss or forced navigation

#### ❌ **FORBIDDEN BEHAVIOR**
- Automatic return to setup form after completion
- Premature ending before max_turns * 2 messages
- Loss of debate content after completion
- Forced navigation without user choice

---

### **Error Handling & Edge Cases**

#### ✅ **REQUIRED BEHAVIOR**

**API Failures**:
- Clear error messages: "❌ Error generating response - please try again"
- Recovery options provided (retry buttons)
- Graceful fallback without breaking UI

**Network Issues**:
- Loading indicators during requests
- Timeout handling with user feedback
- Retry mechanisms for failed operations

**Invalid States**:
- Prevent impossible states through proper validation
- Clear error messages for any issues
- Always provide path forward for users

#### ❌ **FORBIDDEN BEHAVIOR**
- Silent failures without user notification
- Broken states with no recovery options
- Technical error messages without context

---

## 🎨 Visual Design Standards

### **Button States**
- **Primary Actions**: Bright color, high contrast (e.g., "Next Turn" when ready)
- **Secondary Actions**: Muted colors (e.g., "Stop Debate", "Check Again")  
- **Disabled States**: Grayed out with clear visual indication
- **Loading States**: Show activity indicators (⏳, 🔄)

### **Status Messages**
- **Success**: Green checkmark ✅ with positive language
- **Warning**: Orange/yellow ⏳ for waiting states
- **Error**: Red X ❌ with clear next steps
- **Info**: Blue ℹ️ for neutral information

### **Layout Principles**
- **Two-column layout**: Controls on left, transcript/audio on right
- **Responsive design**: Works on different screen sizes
- **Clear hierarchy**: Important actions prominently displayed
- **Consistent spacing**: Uniform margins and padding

---

## 🔄 State Transitions

### **Valid State Flow**
```
Setup Form → First Turn Auto-Start → Manual Control → Completion → New Debate
     ↑                                      ↓
     ←─────────── User chooses restart ─────←
```

### **Invalid Transitions (Prevent These)**
- Setup → Completion (skipping debate)
- Manual Control → Setup (without user choosing restart)
- Completion → Setup (automatic, without user consent)

---

## 📝 Content Guidelines

### **Status Messages**
- Use action-oriented language ("Click Next Turn", not "Waiting")
- Include time estimates when possible ("Next turn ready!", not "Processing")
- Provide clear next steps in error messages

### **Button Labels**
- Action verbs: "Start Debate", "Next Turn", "Stop Debate"
- Status indicators: "⏳ Generating...", "✅ Ready"
- Icons enhance but don't replace text: "🔄 New Debate"

---

## 🚨 Critical Requirements Checklist

Before any UX changes, verify ALL of these requirements are met:

- [ ] First turn auto-starts when ready
- [ ] Manual control for all subsequent turns  
- [ ] Clear feedback when "Next Turn" clicked but not ready
- [ ] Debates run full length (max_turns * 2 messages)
- [ ] Completed debates stay visible with controls
- [ ] No audio interruption during playback
- [ ] All previous turns visible in transcript
- [ ] User controls all major transitions
- [ ] Error states have recovery options
- [ ] Button states clearly indicate availability

---

## 📋 Testing Scenarios

### **Standard Flow Test**
1. Fill setup form → Start debate
2. First turn appears automatically
3. Click "Next Turn" for each subsequent turn
4. Debate completes at correct length
5. Completion UI appears with controls
6. User can start new debate when ready

### **Edge Case Tests**
1. Click "Next Turn" before content ready → Warning appears
2. Stop debate mid-way → Returns to setup with user consent
3. Network failure during generation → Error with retry option
4. Maximum turns reached → Proper completion handling

---

## 🔄 Update Protocol

### **When to Update This File**
- Before implementing any UX changes
- After user feedback identifies UX issues
- When adding new features that affect user experience
- After testing reveals UX problems

### **How to Update**
1. Document the UX decision and rationale
2. Update relevant sections in this file
3. Test changes against all requirements
4. Update DEVELOPMENT_LOG.md with implementation details

---

**Last Updated**: 2025-08-04  
**Version**: 1.0 - Manual Advance System Implementation