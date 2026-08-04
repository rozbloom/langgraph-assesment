# LangGraph Assessment

Submission repo for the Final Assessment: a LangGraph debugging exercise (Assignment 1)
and a stock market analysis agent built from scratch (Assignment 2).

## Structure

```
langgraph-assessment/
├── .gitignore
├── README.md
├── assignment_1/
│   ├── weather_agent_debug.ipynb   # Notebook documenting bugs found + fixes
│   └── weather_agent/              # Provided (buggy) codebase, fixed in place
│       ├── main.py
│       ├── graph.py
│       ├── requirements.txt
│       └── components/
└── assignment_2/
    ├── stock_agent_demo.ipynb      # Notebook demonstrating the agent end-to-end
    └── stock_agent/                # Agent built from scratch
        ├── main.py
        ├── graph.py
        ├── requirements.txt
        └── components/
```

## Setup

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install jupyter
pip install -r assignment_1/weather_agent/requirements.txt
pip install -r assignment_2/stock_agent/requirements.txt
```

## Assignment 1 — Weather Agent Debugging

See `assignment_1/weather_agent_debug.ipynb` for the full list of bugs identified,
the fixes applied, and test scenarios demonstrating the working agent.

## Assignment 2 — Stock Market Analysis Agent

See `assignment_2/stock_agent_demo.ipynb` for the agent design, technical indicator
calculations (SMA-10, SMA-20, RSI-14), recommendation logic, and a live demo run.
