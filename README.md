# Raspberry Pi Morse Code Trainer & Learning Study

  
*LED + Buzzer multi-modal Morse code training system with reaction time logging*

## 🎯 Project Overview

**Current Status**: Working prototype with participant-ready data logging  
**Built with**: Raspberry Pi, Python 3, GPIO Zero  
**Hardware**: Freenove Starter Kit (LED on GPIO17, Buzzer on GPIO18)  

**Core Features**:
- Full alphabet Morse code transmission (visual + audio)
- Real-time reaction time measurement 
- CSV performance logging
- Clean, modular Python architecture

## 📋 What We've Built (Complete ✅)

### Morse Trainer (`morse_trainer.py`)
```
1. Sends random letters via precise Morse timing (dot:dash = 1:3)
2. Multi-modal output: LED blinks + buzzer beeps 
3. Measures reaction time from Morse end → user guess
4. Logs to CSV: [letter, guess, correct, reaction_time]
5. Clean exit handling with hardware cleanup
```

**Demo Flow**:
```
LED/Buzzer: ... --- ... (SOS pattern)
Terminal:   "What letter was that?" 
User:       S 
Terminal:   "Correct! Score: 8/12, RT: 2.1s"
```

### Hardware Setup
```
LED:        GPIO17 → 220Ω resistor → LED anode → GND  
Buzzer:     GPIO18 → Active buzzer → GND  
(Motor removed - distracting)
```

## 🧪 Participant Study Plan (Next Phase ⏳)

### Study Design
```
Phase 1: Baseline (20 letters) → 24hr break → Phase 2: Follow-up (20 letters)
Metrics: Accuracy (%), Reaction Time (s), Learning Gain (%)
Target N: 15-25 participants (classmates, Discord, Reddit)
```

### Expected Outcomes
```
Baseline: ~50-60% accuracy, 3-5s RT
Follow-up: ~70-80% accuracy, 2-3s RT  
Expected gain: +15-25% accuracy, -25-35% RT
```

### Data Collection
```
Files generated: morse_[ID]_[session].csv
Columns: [session, participant, letter, guess, correct, reaction_time]
```

## 📊 Planned Analysis (`analyze_study.py`)

```bash
python3 analyze_study.py
```
**Will compute**:
```
- Overall accuracy & avg RT across all participants
- Per-session improvement (Session1 vs Session2)  
- Individual participant performance rankings
- Letter difficulty rankings (which letters are hardest?)
```

## 🤖 Planned ML Features (Future 🚀)

### 1. Adaptive Difficulty
```
if accuracy > 85%:   DOT_TIME = 0.12s (fast)
elif accuracy > 70%: DOT_TIME = 0.18s (medium)  
elif accuracy > 50%: DOT_TIME = 0.25s (slow)
else:                DOT_TIME = 0.35s (beginner)
```

### 2. Personalized Curriculum
```
Track per-user letter accuracy → prioritize weak letters
Weak letters get 3x selection probability vs mastered letters
```

### 3. Learning Curve Modeling
```
Fit exponential learning curves per participant
Predict time-to-proficiency (80%+ accuracy)
```



## 📁 Repository Structure

```
├── morse_trainer.py          # Main trainer (current working version)
├── analyze_study.py          # Data analysis (planned)
├── participant_instructions.md # Testing guide for participants  
├── hardware/                 # Wiring diagrams
├── data/                     # Generated CSVs (gitignored)
└── README.md                 # You're reading it!
```

## 🔧 Setup Instructions

```bash
# On Raspberry Pi
sudo apt update
sudo apt install python3-gpiozero python3-pip
pip3 install pandas matplotlib  # for analysis

# Wire hardware (see diagrams)
# Run: python3 morse_trainer.py
```

## 📈 Research Questions

1. **Does multi-modal training (visual+audio) improve retention vs single-modality?**
2. **What are population norms for Morse acquisition (accuracy/RT curves)?**
3. **Can adaptive speed selection improve learning efficiency by 15%+?**
4. **Are some letters systematically harder (cognitive/perceptual limits)?**

## 🤝 Contributions Welcome

1. Test as participant (5 mins x 2 sessions)
2. Add LCD display for score feedback
3. Implement adaptive speed (Week 2)
4. Build web dashboard for live stats
5. Port to ESP32 for battery-powered version

## 📄 License
MIT - Free to use/modify for research/education

***

**Status**: Production prototype → Research platform**  
**Next**: 15 participants this week → ML adaptation next month

*Built by biomedical engineering students for resume impact + human learning research*


