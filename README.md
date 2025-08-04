# 🥊 Battle of Wits

**Battle of Wits** is an open-source tool where two AI agents engage in structured, multi-turn debates with real-time voice output.

Pick a topic, define each debater's position, and watch as AI agents argue intelligently with full audio narration. Perfect for exploring complex topics from multiple perspectives.

---

## ✨ Features

- 🗣️ **Real-time voice debates** using OpenAI TTS with different voices per debater
- 🔄 **Structured multi-turn format** with opening statements, rebuttals, and closing arguments  
- 🎭 **Smart context-aware AI** that stays in character and builds on previous arguments
- 📄 **Live transcript** showing the complete debate as it unfolds
- ⚙️ **Configurable parameters** including turn limits, speech speed, and AI models

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key

### Installation

```bash
git clone https://github.com/MaximeLas/battle-of-wits.git
cd battle-of-wits
pip install -r requirements.txt
```

### Setup
1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

2. Add your OpenAI API key to `.env`:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

3. Test the setup:
   ```bash
   python test_setup.py
   ```

4. Launch the application:
   ```bash
   streamlit run main.py
   ```

### Usage
1. Enter your debate topic (e.g., "Artificial Intelligence will benefit humanity")
2. Define Position A and Position B 
3. Adjust settings like number of turns and voices
4. Click "🚀 Start Debate" and listen!

---

## 🧩 Debate Formats

| Format       | Description                                    |
|--------------|------------------------------------------------|
| Formal       | Opening → Rebuttal → Counter → Closing         |
| Casual Chat  | Conversational exchange with light structure   |
| Rapid Fire   | Short character-limited arguments              |
| Roleplay     | Character-driven (e.g. Plato vs Aristotle)     |

---

## 🧠 Example

**Topic**: Should AI be regulated by the government?  
**Pro**: AI poses existential risks and requires oversight.  
**Con**: Regulation will stifle innovation and entrench monopolies.

---

## 🤝 Contributing

Open to ideas, feedback, and future contributions. More features and formats coming soon!

---

## 🪪 License

MIT
