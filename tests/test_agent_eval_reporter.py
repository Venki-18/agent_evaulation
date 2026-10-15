import pytest
import json
import tempfile
from pathlib import Path
from Agent_Eval_Reporter import (
    AgentResult,
    INPUT_SOURCES,
    generate_experiment_results,
    calculate_overall_avg,
    calculate_model_averages,
    calculate_agent_success_metrics,
    calculate_costs,
    find_best_worst_models,
    find_best_worst_agents,
    export_to_json,
    export_to_csv,
    generate_summary_text,
    print_summary,
    save_summary,
    print_ascii_visualization,
)


class TestAgentResult:
    """Test AgentResult class."""

    def test_agent_result_init(self):
        """Test AgentResult initialization."""
        agent = AgentResult(
            agent_name="TestAgent",
            model="gpt-4",
            success_bool=True,
            score=0.95,
            cost=0.01,
            notes="Test note"
        )
        assert agent.agent_name == "TestAgent"
        assert agent.model == "gpt-4"
        assert agent.success_bool is True
        assert agent.score == 0.95
        assert agent.cost == 0.01
        assert agent.notes == "Test note"

    def test_create_test_results(self):
        """Test create_test_results generates valid result."""
        agent = AgentResult()
        result = agent.create_test_results(INPUT_SOURCES)

        # Check all required fields are present
        assert "model" in result
        assert "agent_name" in result
        assert "task" in result
        assert "success" in result
        assert "score" in result
        assert "notes" in result
        assert "costs_usd" in result

        # Check field types
        assert isinstance(result["model"], str)
        assert isinstance(result["agent_name"], str)
        assert isinstance(result["task"], str)
        assert isinstance(result["success"], bool)
        assert isinstance(result["score"], float)
        assert isinstance(result["notes"], str)
        assert isinstance(result["costs_usd"], float)

        # Check values are from input sources
        assert result["model"] in INPUT_SOURCES["models"]
        assert result["score"] >= 0.0 and result["score"] <= 1.0
        assert result["costs_usd"] in INPUT_SOURCES["costs_usd"]


class TestExperimentGeneration:
    """Test experiment results generation."""

    def test_generate_experiment_results(self):
        """Test generating multiple experiment results."""
        results = generate_experiment_results(5, INPUT_SOURCES)

        assert len(results) == 5
        assert all(isinstance(r, dict) for r in results)
        assert all("model" in r for r in results)
        assert all("agent_name" in r for r in results)
        assert all("score" in r for r in results)

    def test_generate_zero_results(self):
        """Test generating zero results."""
        results = generate_experiment_results(0, INPUT_SOURCES)
        assert len(results) == 0

    def test_generate_many_results(self):
        """Test generating many results."""
        results = generate_experiment_results(100, INPUT_SOURCES)
        assert len(results) == 100


class TestMetricsCalculation:
    """Test metrics calculation functions."""

    @pytest.fixture
    def sample_results(self):
        """Create sample results for testing."""
        return [
            {
                "model": "gpt-4",
                "agent_name": "Agent1",
                "success": True,
                "score": 0.9,
                "costs_usd": 0.01,
            },
            {
                "model": "gpt-4",
                "agent_name": "Agent2",
                "success": True,
                "score": 0.8,
                "costs_usd": 0.02,
            },
            {
                "model": "gpt-4-mini",
                "agent_name": "Agent1",
                "success": False,
                "score": 0.5,
                "costs_usd": 0.005,
            },
        ]

    def test_calculate_overall_avg(self, sample_results):
        """Test overall average calculation."""
        avg = calculate_overall_avg(sample_results)
        expected = round((0.9 + 0.8 + 0.5) / 3, 3)
        assert avg == expected

    def test_calculate_overall_avg_empty(self):
        """Test overall average with empty results."""
        avg = calculate_overall_avg([])
        assert avg is None

    def test_calculate_overall_avg_single(self):
        """Test overall average with single result."""
        results = [{"score": 0.75}]
        avg = calculate_overall_avg(results)
        assert avg == 0.75

    def test_calculate_model_averages(self, sample_results):
        """Test model average calculation."""
        model_avg = calculate_model_averages(sample_results)

        # gpt-4: (0.9 + 0.8) / 2 = 0.85
        # gpt-4-mini: 0.5 / 1 = 0.5
        assert "gpt-4" in model_avg
        assert "gpt-4-mini" in model_avg
        assert model_avg["gpt-4"] == round((0.9 + 0.8) / 2, 3)
        assert model_avg["gpt-4-mini"] == 0.5

    def test_calculate_model_averages_empty(self):
        """Test model averages with empty results."""
        model_avg = calculate_model_averages([])
        assert model_avg == {}

    def test_calculate_agent_success_metrics(self, sample_results):
        """Test agent success metrics calculation."""
        metrics = calculate_agent_success_metrics(sample_results)

        # Agent1: (True, False) = 1/2 = 0.5
        # Agent2: (True) = 1/1 = 1.0
        assert "Agent1" in metrics
        assert "Agent2" in metrics
        assert metrics["Agent1"] == 0.5
        assert metrics["Agent2"] == 1.0

    def test_calculate_agent_success_metrics_all_success(self):
        """Test agent success with all successful."""
        results = [
            {"agent_name": "A", "success": True},
            {"agent_name": "A", "success": True},
        ]
        metrics = calculate_agent_success_metrics(results)
        assert metrics["A"] == 1.0

    def test_calculate_agent_success_metrics_all_failure(self):
        """Test agent success with all failures."""
        results = [
            {"agent_name": "A", "success": False},
            {"agent_name": "A", "success": False},
        ]
        metrics = calculate_agent_success_metrics(results)
        assert metrics["A"] == 0.0

    def test_calculate_costs(self, sample_results):
        """Test cost calculations."""
        total_cost, model_wise_cost = calculate_costs(sample_results)

        # Total: 0.01 + 0.02 + 0.005 = 0.035
        # gpt-4: 0.01 + 0.02 = 0.03
        # gpt-4-mini: 0.005
        assert total_cost == round(0.01 + 0.02 + 0.005, 2)
        assert model_wise_cost["gpt-4"] == round(0.03, 3)
        assert model_wise_cost["gpt-4-mini"] == round(0.005, 3)

    def test_calculate_costs_empty(self):
        """Test cost calculation with empty results."""
        total_cost, model_wise_cost = calculate_costs([])
        assert total_cost == 0.0
        assert model_wise_cost == {}


class TestRanking:
    """Test best/worst model and agent functions."""

    @pytest.fixture
    def sample_model_avg(self):
        """Create sample model averages."""
        return {
            "gpt-4": 0.85,
            "gpt-4-mini": 0.60,
            "claude": 0.95,
        }

    @pytest.fixture
    def sample_results(self):
        """Create sample results for ranking."""
        return [
            {"agent_name": "Agent1", "score": 0.9},
            {"agent_name": "Agent2", "score": 0.5},
            {"agent_name": "Agent3", "score": 0.95},
        ]

    def test_find_best_worst_models(self, sample_model_avg):
        """Test finding best and worst models."""
        ranks = find_best_worst_models(sample_model_avg)

        assert ranks["best"] == "claude"
        assert ranks["best_score"] == 0.95
        assert ranks["worst"] == "gpt-4-mini"
        assert ranks["worst_score"] == 0.60

    def test_find_best_worst_models_empty(self):
        """Test with empty model averages."""
        ranks = find_best_worst_models({})
        assert ranks["best"] == ""
        assert ranks["worst"] == ""

    def test_find_best_worst_models_single(self):
        """Test with single model."""
        ranks = find_best_worst_models({"gpt-4": 0.75})
        assert ranks["best"] == "gpt-4"
        assert ranks["worst"] == "gpt-4"

    def test_find_best_worst_agents(self, sample_results):
        """Test finding best and worst agents."""
        ranks = find_best_worst_agents(sample_results)

        assert ranks["best_agent"] == "Agent3"
        assert ranks["best_agent_score"] == 0.95
        assert ranks["worst_agent"] == "Agent2"
        assert ranks["worst_agent_score"] == 0.5

    def test_find_best_worst_agents_empty(self):
        """Test with empty results."""
        ranks = find_best_worst_agents([])
        assert ranks["best_agent"] == ""
        assert ranks["worst_agent"] == ""

    def test_find_best_worst_agents_single(self):
        """Test with single agent result."""
        results = [{"agent_name": "Agent1", "score": 0.75}]
        ranks = find_best_worst_agents(results)
        assert ranks["best_agent"] == "Agent1"
        assert ranks["worst_agent"] == "Agent1"


class TestExportFunctions:
    """Test export functions."""

    @pytest.fixture
    def sample_results(self):
        """Create sample results for exporting."""
        return [
            {
                "model": "gpt-4",
                "agent_name": "Agent1",
                "task": "Task1",
                "success": True,
                "score": 0.9,
                "notes": "Good",
                "costs_usd": 0.01,
            },
            {
                "model": "gpt-4-mini",
                "agent_name": "Agent2",
                "task": "Task2",
                "success": False,
                "score": 0.5,
                "notes": "Bad",
                "costs_usd": 0.005,
            },
        ]

    def test_export_to_json(self, sample_results):
        """Test JSON export."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test_results.json"
            export_to_json(sample_results, str(filepath))

            assert filepath.exists()

            with open(filepath) as f:
                data = json.load(f)

            assert len(data) == 2
            assert data[0]["model"] == "gpt-4"
            assert data[1]["agent_name"] == "Agent2"

    def test_export_to_json_empty(self):
        """Test JSON export with empty results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test_results.json"
            export_to_json([], str(filepath))

            assert filepath.exists()
            with open(filepath) as f:
                data = json.load(f)
            assert data == []

    def test_export_to_csv(self, sample_results):
        """Test CSV export."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test_results.csv"
            export_to_csv(sample_results, str(filepath))

            assert filepath.exists()

            lines = filepath.read_text().strip().split('\n')

            # Should have header + 2 data rows
            assert len(lines) == 3
            assert "model" in lines[0]
            assert "gpt-4" in lines[1]

    def test_export_to_csv_empty(self):
        """Test CSV export with empty results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test_results.csv"
            export_to_csv([], str(filepath))

            # Empty results should not create a file
            assert not filepath.exists()

    def test_csv_row_count(self, sample_results):
        """Test that CSV has correct number of rows."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test_results.csv"
            export_to_csv(sample_results, str(filepath))

            lines = filepath.read_text().strip().split('\n')
            # Header + 2 data rows
            assert len(lines) == 3


class TestSummaryGeneration:
    """Test summary generation and display functions."""

    def test_generate_summary_text(self):
        """Test summary text generation."""
        results = [{"agent_name": "Agent1", "score": 0.8}]

        summary = generate_summary_text(
            results=results,
            overall_avg=0.8,
            model_avg={"gpt-4": 0.8},
            agent_succes_metric={"Agent1": 1.0},
            total_cost=0.01,
            model_wise_cost={"gpt-4": 0.01},
            model_ranks={"best": "gpt-4", "best_score": 0.8, "worst": "gpt-4", "worst_score": 0.8},
            agent_rank_stats={"best_agent": "Agent1", "best_agent_score": 0.8,
                            "worst_agent": "Agent1", "worst_agent_score": 0.8}
        )

        assert isinstance(summary, list)
        assert len(summary) > 0
        assert any("MODEL / AGENT SUMMARY" in line for line in summary)
        assert any("0.8" in line for line in summary)

    def test_save_summary(self):
        """Test saving summary to file."""
        summary = ["Line 1", "Line 2", "Line 3"]

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test_summary.txt"
            save_summary(summary, str(filepath))

            assert filepath.exists()
            content = filepath.read_text()

            for line in summary:
                assert line in content

    def test_print_summary(self, capsys):
        """Test printing summary to console."""
        summary = ["Test Line 1", "Test Line 2"]
        print_summary(summary)

        captured = capsys.readouterr()
        assert "Test Line 1" in captured.out
        assert "Test Line 2" in captured.out

    def test_print_ascii_visualization(self, capsys):
        """Test ASCII visualization printing."""
        results = [
            {"agent_name": "Agent1", "score": 0.9},
            {"agent_name": "Agent2", "score": 0.5},
        ]
        print_ascii_visualization(results)

        captured = capsys.readouterr()
        assert "Agent1" in captured.out
        assert "Agent2" in captured.out
        assert "█" in captured.out  # Check for bar characters


class TestInputSources:
    """Test INPUT_SOURCES fixture."""

    def test_input_sources_structure(self):
        """Test INPUT_SOURCES has correct structure."""
        assert "models" in INPUT_SOURCES
        assert "agent_tasks" in INPUT_SOURCES
        assert "outcomes" in INPUT_SOURCES
        assert "costs_usd" in INPUT_SOURCES

    def test_input_sources_models(self):
        """Test models in INPUT_SOURCES."""
        assert len(INPUT_SOURCES["models"]) > 0
        assert all(isinstance(m, str) for m in INPUT_SOURCES["models"])

    def test_input_sources_agent_tasks(self):
        """Test agent_tasks in INPUT_SOURCES."""
        assert len(INPUT_SOURCES["agent_tasks"]) > 0
        for task in INPUT_SOURCES["agent_tasks"]:
            assert "agent_name" in task
            assert "task" in task

    def test_input_sources_outcomes(self):
        """Test outcomes in INPUT_SOURCES."""
        assert len(INPUT_SOURCES["outcomes"]) > 0
        for outcome in INPUT_SOURCES["outcomes"]:
            assert "success" in outcome
            assert "score" in outcome
            assert "notes" in outcome
            assert isinstance(outcome["success"], bool)
            assert 0 <= outcome["score"] <= 1.0

    def test_input_sources_costs(self):
        """Test costs in INPUT_SOURCES."""
        assert len(INPUT_SOURCES["costs_usd"]) > 0
        assert all(isinstance(c, float) for c in INPUT_SOURCES["costs_usd"])
        assert all(c >= 0 for c in INPUT_SOURCES["costs_usd"])
