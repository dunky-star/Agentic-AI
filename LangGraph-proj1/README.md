# Agentic AI Certification – Week 5

This repository contains code examples, reference scripts, and foundational components for **Week 5** of the Agentic AI Developer Program. This week marks the transition from traditional prompt pipelines to building **agent-based AI systems** using tools like **LangGraph**, **LangChain**, and **LangSmith**.

## What You'll Learn

Week 5 introduces the core building blocks of agentic systems and prepares you for more complex workflows in later modules. You’ll explore:

- The **workflow-to-agent spectrum** and when to use agentic architectures.
- The fundamentals of **LangGraph** and how to structure applications as stateful graphs.
- The role of **LangSmith** in debugging, tracing, and evaluating agent runs.
- Built-in and **custom tool development** for dynamic agent behavior.

## Repository Structure

```txt
rt-agentic-ai-cert-week5/
├── code/
│   ├── custom_tools.py                         # Custom tool implementations for Lesson 3b
│   ├── llm.py                                  # LLM utility wrapper
│   ├── paths.py                                # Standardized file path management
│   ├── prompt_builder.py                       # Modular prompt construction functions
│   ├── pyjokes_joke_bot.py                     # Lesson 2b: Run joke-bot using pyjokes
│   ├── llm_joke_bot.py                         # Lesson 2c: Run joke-bot using ai agents
│   ├── custom_tools.py                         # Lesson 4b: Run agent with custom tools
│   └── utils.py                                # Common utilities
├── config/
│   ├── config.yaml                             # Configuration file for tool registration or agent setup
│   └── prompt_config.yaml                      # Prompt configurations for agents
├── outputs/
│   └── graph.png                               # Example LangGraph visualization
├── .env.example                                # Sample environment variable file (e.g., Groq API key)
├── .gitignore
├── LICENSE
├── README.md                                   # You are here
└── requirements.txt                            # Required Python dependencies
```

---

## Lessons Covered So Far

### **Lesson 2b – Building Your First Graph in LangGraph**

- Introduces how to define nodes, edges, and a shared state object.
- Example: A minimal **non-LLM agent** using the `pyjokes` library to route actions.
- Main script: `pyjokes_joke_bot.py`

### **Lesson 2c – Introducing Agentic Behavior with a Writer-Critic Loop**

- Extend the previous joke bot to use LLMs for joke generation and evaluation
- Introduce agentic workflows: generation → reflection → refinement
- LangSmith is automatically enabled for traceability and debugging
- Categories include: dad developer, chuck norris developer, knock-knock, general
- 📄 Main script: `llm_joke_bot.py`

### **Lesson 4b – Building Custom Tools**

- Demonstrates how to define and register custom tools for agent use.
- Tool functions are defined in `custom_tools.py`.
- Main script: `run_wk5_l4b_custom_tools.py`

---

## Installation & Setup

1. **Clone the repository:**

   ```bash
   
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your environment variables:**

   Copy the `.env.example` to `.env` and update the values (e.g., Groq API key):

   ```bash
   cp .env.example .env
   ```

   You can get your API key from [Groq](https://console.groq.com/).

---

## License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

---

## Contact

**Yo hunters, Inc.**

- Email: contact at readytensor dot com
- Issues & Contributions: Open an issue or PR on this repo
- Website: [https://dunkystar.com](https://dunkystar.com)
