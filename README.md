# AI Agent Test Results & Evaluation Pipeline

A lightweight, pure Python framework for generating synthetic test datasets, running mock evaluations on multi-agent systems, and calculating performance metrics across different AI models.

## 🚀 Overview

This repository runs a simulation of AI agent executions using configurable input sources (such as model identifiers, predefined tasks, outcomes, and costs). It compiles random experiment runs, serializes the data into JSON and pipe-delimited CSV formats, computes comprehensive performance aggregates, and outputs a formatted console summary and ASCII visualization.

## 📂 Project Structure

- `experiment_results.json`: Full structured log of all generated agent test runs.
- `experiment_result.csv`: Pipe-delimited flat file version of the experiment results.
- `Summary.txt`: Saved text file containing aggregated performance metrics, model averages, and rankings.
- Main Script (`agent_test.py` - *your code*): Contains the `AgentResult` class, data fixtures, statistical aggregations, and visual bar charts.

## 📊 Key Features

1. **Synthetic Data Generation:** Combines models, agent tasks, outcomes, and cost metrics dynamically via `AgentResult.create_test_results()`.
2. **Multi-Format Export:** Automatically saves results into structured JSON and custom CSV flat files.
3. **Statistical Aggregation:**
   - Overall average scores.
   - Model-wise average performance ratings.
   - Success rate metrics per individual agent.
   - Total and model-specific cost tracking.
   - Automated identification of best and worst-performing models and agents.
4. **Console Visualization:** Generates quick-glance ASCII progress bar charts based on agent scores directly in the terminal.

## 🛠️ Requirements & Setup

- Python 3.x
- Standard libraries used: `random`, `json`, `pathlib` (no external dependencies required!).

### Running the Script

Execute the script from your terminal:

```bash
python Agent_Eval_Reporter.py
```

## 📝 Output Examples

### Model Averages
The pipeline evaluates and groups performance per model ID, calculating mean scores to rank the most efficient architectures.

### Success Rate per Agent
Tracks how often each specialized agent (e.g., `SummaryAgent`, `SQLAgent`, `CodeReviewAgent`) clears the success threshold ($score \ge 0.80$).

---
*Maintained as part of our automated AI testing and evaluation workflow.*
