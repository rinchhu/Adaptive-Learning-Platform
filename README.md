# Adaptive Learning Platform

A modern, rule-based educational desktop application built with **Python**, **Tkinter**, and **JSON**. Developed in direct alignment with **United Nations Sustainable Development Goal 4 (SDG 4): Quality Education**.

---

## 1. Project Overview

The **Adaptive Learning Platform** is an educational desktop application designed to provide personalized, self-paced learning. It adapts content and quiz difficulty according to a student's individual performance on a topic-by-topic basis.

### Core Philosophy:
- **Rule-Based Personalization:** Deterministic, transparent adaptation rules ensure fair, predictable milestones without black-box machine learning algorithms.
- **Offline & Equitable Access:** Runs 100% locally using Python's built-in standard library and JSON file storage—no external cloud APIs, GPUs, or internet connectivity required.
- **UN SDG 4 (Quality Education):** Emphasizes inclusive, self-paced learning, immediate formative feedback, and targeted gap remediation.

---

## 2. Key Features

1. **Modern Educational Dashboard:**
   - Real-time statistics: Total topics available, topics completed, total quizzes attempted, average quiz score, and overall learning progress percentage.
   - **"Continue Learning"** quick-action card to resume the student's latest active topic.
   - Rule engine guidance banner recommending the next optimal study target.

2. **Subject & Topic Management:**
   - Browse subjects (e.g., *Python Basics*) and topics.
   - **Live Topic Search Filter:** Instantly filter topics by typing keywords in the search bar.
   - Status Filter Tabs: Filter by **All Topics**, **Completed**, or **Pending**.
   - Topic status pills (`Not Started`, `In Progress`, `Completed`, `Mastered`, `Needs Revision`).

3. **Interactive Learning Module:**
   - Comprehensive concept introduction, detailed explanations, and key takeaways.
   - **Interactive Python Code Playground:** An editable code editor allowing students to test and run Python code snippets directly inside the desktop app with live terminal output!
   - **"Mark as Completed"** toggle to track manual completion.

4. **Advanced Adaptive Quiz Engine:**
   - 3 difficulty levels: **Easy**, **Medium**, and **Hard**.
   - **Randomized Question Selector:** Pulls randomized 5-question subsets from a 75-question multi-level bank.
   - **Instant Question Feedback:** Choosing an answer immediately reveals whether it was correct or incorrect, highlights the right choice, and displays an explanation.
   - **"💡 Show Hint"** button on every question for guided self-discovery.
   - **"☆ Bookmark Question"** button allowing students to save tricky questions for later review.
   - Comprehensive results screen with rule-based promotion analysis, retry quiz button, and missed questions practice.

5. **Topic-Specific Rule-Based Adaptive Learning Engine:**
   - **$\ge 80\%$ (High Performance):** Promotes topic difficulty (Easy $\rightarrow$ Medium $\rightarrow$ Hard) and marks topic as *Mastered*.
   - **$50\% - 79\%$ (Moderate Performance):** Maintains difficulty level to consolidate understanding.
   - **$< 50\%$ (Low Performance):** Adjusts difficulty level downward (Hard $\rightarrow$ Medium $\rightarrow$ Easy) and recommends reviewing lesson materials.
   - **Targeted Gap Remediation:** Adapts on a topic-by-topic basis so that struggling in one topic (e.g. *Functions*) does not lower difficulty in topics already mastered (e.g. *Variables*).

6. **Dedicated Bookmarks Center:**
   - Access saved questions anytime from the sidebar.
   - Displays question text, options, highlighted correct answers, and conceptual explanations.
   - Option to remove bookmarks once mastered.

7. **Functional Achievements & Rewards Badges:**
   - Functional milestone badges that unlock automatically based on real progress:
     - 🎯 *First Step* (Completed first quiz)
     - 🏆 *Dedicated Learner* (Attempted 5 quizzes)
     - 🐍 *Python Novice* (Completed 1 topic)
     - 🌟 *Flawless Score* (Scored 100% on any quiz)
     - 📚 *Curriculum Explorer* (Completed 3 topics)
     - 🎓 *Python Master* (Mastered all 5 topics)
     - ⭐ *Curious Mind* (Bookmarked first question)

8. **Learning Progress & Analytics:**
   - Student diagnostic insights: Highlights **Strongest Topic** vs **Focus Area (Needs Improvement)**.
   - **Canvas-Drawn Score Comparison Bar Chart:** Native Tkinter Canvas visualization comparing highest scores against an 80% mastery guideline.
   - Full quiz attempt history log.
   - **"📄 Export Progress Report (.txt)"** button for printable academic report cards.

9. **Multi-Student Profile Isolation:**
   - Supports multiple students on the same computer with independent progress records stored in `progress.json`.

10. **UN SDG 4: Quality Education Section:**
    - Dedicated section detailing how the platform supports inclusive, equitable, and accessible education.

---

## 3. Technology Stack

- **Programming Language:** Python 3 (standard library)
- **GUI Toolkit:** Tkinter (built-in)
- **Data Persistence:** JSON (`lessons.json`, `questions.json`, `progress.json`)
- **External Dependencies:** **None** (zero pip packages required)

---

## 4. Project Directory Structure

```text
adaptive_learning_platform/
│
├── main.py              # Main desktop application, sidebar controller & engine
├── lessons.json         # Structured subjects, topics, explanations & code examples
├── questions.json       # 75-question multi-level bank (Easy/Medium/Hard) with hints
├── progress.json        # Isolated multi-student persistent database
└── README.md            # Comprehensive project documentation
```

---

## 5. How to Run the Application

### Prerequisites
Make sure **Python 3.8+** is installed on your computer.

### Execution Steps
1. Open your terminal or Command Prompt.
2. Navigate to the project directory:
   ```cmd
   cd adaptive_learning_platform
   ```
3. Run the application:
   ```cmd
   python main.py
   ```

*(Alternatively, run directly from anywhere: `python C:\Users\rites\adaptive_learning_platform\main.py`)*
