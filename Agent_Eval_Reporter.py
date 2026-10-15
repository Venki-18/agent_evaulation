import random
import json
from pathlib import Path

class AgentResult:
    def __init__(self, agent_name=None, model=None, model_task=None,
                 success_bool=None, score=None, cost=None, notes=None):
        self.agent_name = agent_name
        self.model = model
        self.model_task = model_task
        self.success_bool = success_bool
        self.score = score
        self.cost = cost
        self.notes = notes

    def create_test_results(self, source: dict):
        """Generate a single random test result from input sources."""
        result_dict = {}
        models_lst = []
        name_task = []
        succes_score_note = []
        cost_lst = []

        for key, value in source.items():
            if key == 'outcomes':
                for item in value:
                    succes_score_note.append((item["success"], item["score"], item["notes"]))
            if key == 'agent_tasks':
                for item in value:
                    name_task.append((item["agent_name"], item["task"]))
            if key == 'models':
                for item in value:
                    models_lst.append(item)
            if key == 'costs_usd':
                for item in value:
                    cost_lst.append(item)

        rand_models_lst = [models_lst[random.randint(0, len(models_lst)-1)]]
        rand_name_task = [name_task[random.randint(0, len(name_task)-1)]]
        rand_succes_score_note = [succes_score_note[random.randint(0, len(succes_score_note)-1)]]
        rand_cost_lst = [cost_lst[random.randint(0, len(cost_lst)-1)]]

        result_dict["model"] = rand_models_lst[0]
        result_dict["agent_name"] = rand_name_task[0][0]
        result_dict["task"] = rand_name_task[0][1]
        result_dict["success"] = rand_succes_score_note[0][0]
        result_dict["score"] = rand_succes_score_note[0][1]
        result_dict["notes"] = rand_succes_score_note[0][2]
        result_dict["costs_usd"] = rand_cost_lst[0]
        return result_dict


# Test data fixtures
INPUT_SOURCES = {
    # Real API model IDs.
    "models": [
        "gpt-4.1",
        "gpt-4.1-mini",
    ],

    # Pick one entire agent/task entry so they stay related.
    "agent_tasks": [
        {
            "agent_name": "SummaryAgent",
            "task": "Summarize a support ticket in three sentences.",
        },
        {
            "agent_name": "SentimentAgent",
            "task": "Classify a customer review as positive, neutral, or negative.",
        },
        {
            "agent_name": "ExtractionAgent",
            "task": "Extract names and email addresses from a document.",
        },
        {
            "agent_name": "TranslationAgent",
            "task": "Translate an English paragraph into Spanish.",
        },
        {
            "agent_name": "CodeReviewAgent",
            "task": "Review a Python function for potential bugs.",
        },
        {
            "agent_name": "TestWriterAgent",
            "task": "Write unit tests for a Python function.",
        },
        {
            "agent_name": "SQLAgent",
            "task": "Generate a SQL query from a plain-language request.",
        },
        {
            "agent_name": "ClassificationAgent",
            "task": "Categorize a support ticket as billing, technical, or account.",
        },
        {
            "agent_name": "JSONAgent",
            "task": "Convert a product description into structured JSON.",
        },
        {
            "agent_name": "AnswerAgent",
            "task": "Answer a question using only a supplied reference document.",
        },
    ],

    # Synthetic outcome inputs, not measured model performance.
    "outcomes": [
        {
            "success": True,
            "score": 1.00,
            "notes": "Synthetic test outcome: all evaluation checks passed.",
        },
        {
            "success": True,
            "score": 0.95,
            "notes": "Synthetic test outcome: minor issues; acceptance checks passed.",
        },
        {
            "success": True,
            "score": 0.85,
            "notes": "Synthetic test outcome: acceptable output with some omissions.",
        },
        {
            "success": True,
            "score": 0.80,
            "notes": "Synthetic test outcome: met the acceptance threshold.",
        },
        {
            "success": False,
            "score": 0.75,
            "notes": "Synthetic test outcome: below the acceptance threshold.",
        },
        {
            "success": False,
            "score": 0.50,
            "notes": "Synthetic test outcome: partially correct output.",
        },
        {
            "success": False,
            "score": 0.25,
            "notes": "Synthetic test outcome: major errors in the output.",
        },
        {
            "success": False,
            "score": 0.00,
            "notes": "Synthetic test outcome: no usable output.",
        },
    ],

    # Synthetic per-run costs in USD.
    "costs_usd": [
        0.0001,
        0.0005,
        0.0010,
        0.0025,
        0.0050,
        0.0100,
        0.0250,
        0.0500,
    ],
}


def generate_experiment_results(num_results: int, input_sources: dict) -> list:
    """Generate synthetic experiment results."""
    agt = AgentResult()
    experiment_results = []
    for i in range(num_results):
        experiment_results.append(agt.create_test_results(input_sources))
    return experiment_results


def calculate_overall_avg(results: list) -> float:
    """Calculate overall average score."""
    if not results:
        return None
    sum_scores = sum(r["score"] for r in results)
    return round(sum_scores / len(results), 3)


def calculate_model_averages(results: list) -> dict:
    """Calculate average score per model."""
    model_avg = {}
    sum_scores = {}
    count = {}

    for result in results:
        model = result["model"]
        score = result["score"]

        if model not in sum_scores:
            sum_scores[model] = 0
            count[model] = 0

        sum_scores[model] += score
        count[model] += 1

    for model in sum_scores:
        model_avg[model] = round(sum_scores[model] / count[model], 3)

    return model_avg


def calculate_agent_success_metrics(results: list) -> dict:
    """Calculate success rate per agent."""
    agent_history = {}

    for result in results:
        agent = result["agent_name"]
        success = 1 if result["success"] else 0

        if agent not in agent_history:
            agent_history[agent] = []
        agent_history[agent].append(success)

    agent_succes_metric = {}
    for agent, suc_rate in agent_history.items():
        agent_succes_metric[agent] = sum(suc_rate) / len(suc_rate)

    return agent_succes_metric


def calculate_costs(results: list) -> tuple:
    """Calculate total and per-model costs."""
    total_cost = 0.0
    model_wise_cost = {}

    for result in results:
        total_cost += result["costs_usd"]
        model = result["model"]

        if model not in model_wise_cost:
            model_wise_cost[model] = 0.0
        model_wise_cost[model] += result["costs_usd"]

    return round(total_cost, 2), {k: round(v, 3) for k, v in model_wise_cost.items()}


def find_best_worst_models(model_avg: dict) -> dict:
    """Find best and worst performing models by average score."""
    if not model_avg:
        return {"best": "", "best_score": 0.0, "worst": "", "worst_score": 2.0}

    model_ranks = {"best": "", "best_score": 0.0, "worst": "", "worst_score": 2.0}

    for model, score in model_avg.items():
        if score < model_ranks["worst_score"]:
            model_ranks["worst_score"] = score
            model_ranks["worst"] = model
        if score > model_ranks["best_score"]:
            model_ranks["best_score"] = score
            model_ranks["best"] = model

    return model_ranks


def find_best_worst_agents(results: list) -> dict:
    """Find best and worst performing agents by individual score."""
    if not results:
        return {"best_agent": "", "best_agent_score": 0.0,
                "worst_agent": "", "worst_agent_score": 2.0}

    agent_rank_stats = {"best_agent": "", "best_agent_score": -1,
                        "worst_agent": "", "worst_agent_score": 2.0}

    for record in results:
        agent = record["agent_name"]
        score = record["score"]

        if score < agent_rank_stats["worst_agent_score"]:
            agent_rank_stats["worst_agent_score"] = score
            agent_rank_stats["worst_agent"] = agent

        if score > agent_rank_stats["best_agent_score"]:
            agent_rank_stats["best_agent_score"] = score
            agent_rank_stats["best_agent"] = agent

    return agent_rank_stats


def export_to_json(results: list, filepath: str = "experiment_results.json"):
    """Export results to JSON file."""
    p = Path(filepath)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(results, indent=4), encoding="utf-8")


def export_to_csv(results: list, filepath: str = "experiment_result.csv"):
    """Export results to CSV file."""
    if not results:
        return

    csv_file = Path(filepath)
    csv_file.parent.mkdir(parents=True, exist_ok=True)

    header = " | ".join(results[0].keys())
    csv_file.write_text(header + "\n")

    with open(csv_file, 'a') as f:
        for res in results:
            line = " | ".join(str(cell) for cell in res.values())
            f.write(line + "\n")


def generate_summary_text(results: list, overall_avg: float, model_avg: dict,
                         agent_succes_metric: dict, total_cost: float,
                         model_wise_cost: dict, model_ranks: dict,
                         agent_rank_stats: dict) -> list:
    """Generate summary text lines."""
    print_msg = [
        " ====**** " * 5,
        "          MODEL / AGENT SUMMARY         ",
        " ====**** " * 5,
        f"Overall average score: {overall_avg}",
        " -------- model average ----------",
    ]

    for k, v in model_avg.items():
        print_msg.append(f"{k}: {v}")

    print_msg.append(" --------- Agent success rate ----------")

    for k, v in agent_succes_metric.items():
        print_msg.append(f"{k}: {round(v * 100, 2)}%")

    print_msg.append(f"The total cost is: ${round(total_cost, 2)} USD")
    for model, cost in model_wise_cost.items():
        print_msg.append(f"For {model} the total cost is ${round(cost, 3)} USD")

    print_msg.append(
        f"Best model is {model_ranks['best']} with score {model_ranks['best_score']}. "
        f"Worst model is {model_ranks['worst']} with score {model_ranks['worst_score']}"
    )
    print_msg.append(
        f"Best Agent {model_ranks['best']} with score {agent_rank_stats['best_agent_score']}"
    )
    print_msg.append(
        f"Worst Agent {agent_rank_stats['worst_agent']} with score {agent_rank_stats['worst_agent_score']}"
    )

    return print_msg


def print_summary(print_msg: list):
    """Print summary to console."""
    for line in print_msg:
        print(line)


def save_summary(print_msg: list, filepath: str = "Summary.txt"):
    """Save summary to file."""
    p = Path(filepath)
    p.write_text("")
    with p.open("a") as f:
        for line in print_msg:
            f.write(line + "\n")


def print_ascii_visualization(results: list):
    """Print ASCII bar visualization of scores."""
    for line in results:
        bar = '█' * int(line['score'] * 10)
        print(f"{line['agent_name']:<50} {bar}")


def main(num_results: int = 15, input_sources: dict = None):
    """Main orchestration function."""
    if input_sources is None:
        input_sources = INPUT_SOURCES

    # Generate results
    experiment_results = generate_experiment_results(num_results, input_sources)

    # Export to files
    export_to_json(experiment_results)
    export_to_csv(experiment_results)

    # Calculate metrics
    overall_avg = calculate_overall_avg(experiment_results)
    model_avg = calculate_model_averages(experiment_results)
    agent_succes_metric = calculate_agent_success_metrics(experiment_results)
    total_cost, model_wise_cost = calculate_costs(experiment_results)
    model_ranks = find_best_worst_models(model_avg)
    agent_rank_stats = find_best_worst_agents(experiment_results)

    # Generate and display summary
    print_msg = generate_summary_text(
        experiment_results, overall_avg, model_avg, agent_succes_metric,
        total_cost, model_wise_cost, model_ranks, agent_rank_stats
    )

    print_summary(print_msg)
    save_summary(print_msg)

    # ASCII visualization
    print_ascii_visualization(experiment_results)

    return {
        "results": experiment_results,
        "overall_avg": overall_avg,
        "model_avg": model_avg,
        "agent_succes_metric": agent_succes_metric,
        "total_cost": total_cost,
        "model_wise_cost": model_wise_cost,
        "model_ranks": model_ranks,
        "agent_rank_stats": agent_rank_stats,
    }


if __name__ == "__main__":
    main()
