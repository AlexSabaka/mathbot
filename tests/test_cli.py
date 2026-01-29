"""Tests for CLI commands."""

import pytest
import json
from click.testing import CliRunner
from src.cli import cli


class TestGenerateCommand:
    """Test the generate command."""

    def test_generate_basic(self):
        """Test basic generation works."""
        runner = CliRunner()
        result = runner.invoke(cli, ['generate', '-s', '42'])
        assert result.exit_code == 0
        assert 'Problem:' in result.output or '{' in result.output

    def test_generate_json_output(self):
        """Test JSON output format."""
        runner = CliRunner()
        result = runner.invoke(cli, ['generate', '-s', '42', '-o', 'json'])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert 'test_id' in data
        assert 'problem' in data
        assert 'task_params' in data

    def test_generate_text_output(self):
        """Test text output format."""
        runner = CliRunner()
        result = runner.invoke(cli, ['generate', '-s', '42', '-o', 'text'])
        assert result.exit_code == 0
        assert 'Please solve this problem' in result.output

    def test_generate_to_file(self):
        """Test generating to file."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ['generate', '-s', '42', '-o', 'json', '--file', 'test.json'])
            assert result.exit_code == 0
            assert 'saved to test.json' in result.output

            # Verify file was created
            with open('test.json') as f:
                data = json.load(f)
                assert 'test_id' in data

    def test_generate_with_all_params(self):
        """Test generation with all parameters specified."""
        runner = CliRunner()
        result = runner.invoke(cli, [
            'generate',
            '-c', '2',
            '-g', 'middle',
            '-t', 'arithmetic',
            '-f', 'sequential_purchase',
            '-n', '3',
            '-s', '42',
            '-o', 'json'
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data['task_params']['complexity'] == 2
        assert data['task_params']['grade'] == 'middle'

    def test_generate_reproducibility(self):
        """Test that same seed produces same problem."""
        runner = CliRunner()

        result1 = runner.invoke(cli, ['generate', '-s', '12345', '-o', 'json'])
        assert result1.exit_code == 0
        problem1 = json.loads(result1.output)

        result2 = runner.invoke(cli, ['generate', '-s', '12345', '-o', 'json'])
        assert result2.exit_code == 0
        problem2 = json.loads(result2.output)

        assert problem1['test_id'] == problem2['test_id']
        assert problem1['problem'] == problem2['problem']

    def test_generate_no_show_answer(self):
        """Test hiding answer in output."""
        runner = CliRunner()
        result = runner.invoke(cli, ['generate', '-s', '42', '-o', 'json', '--no-show-answer'])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert 'expected_answer' not in data['task_params']
        assert 'operations' not in data['task_params']

    def test_generate_invalid_complexity(self):
        """Test error handling for invalid complexity."""
        runner = CliRunner()
        result = runner.invoke(cli, ['generate', '-c', '5'])
        assert result.exit_code != 0


class TestBatchCommand:
    """Test the batch command."""

    def test_batch_generation(self):
        """Test generating multiple problems."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ['batch', '5', '--file', 'batch.json'])
            assert result.exit_code == 0
            assert 'Generated 5 problems' in result.output

            # Verify file was created and has 5 problems
            with open('batch.json') as f:
                data = json.load(f)
                assert len(data) == 5
                assert all('test_id' in p for p in data)

    def test_batch_jsonl_output(self):
        """Test JSONL output format."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ['batch', '3', '--file', 'batch.jsonl', '-o', 'jsonl'])
            assert result.exit_code == 0

            # Verify JSONL format
            with open('batch.jsonl') as f:
                lines = f.readlines()
                assert len(lines) == 3
                for line in lines:
                    problem = json.loads(line)
                    assert 'test_id' in problem

    def test_batch_with_constraints(self):
        """Test batch generation with specific parameters."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(cli, [
                'batch', '10',
                '-c', '2',
                '-g', 'middle',
                '-t', 'arithmetic',
                '--file', 'constrained.json'
            ])
            assert result.exit_code == 0

            with open('constrained.json') as f:
                data = json.load(f)
                assert len(data) == 10
                for problem in data:
                    assert problem['task_params']['complexity'] == 2
                    assert problem['task_params']['grade'] == 'middle'

    def test_batch_avoid_duplicates(self):
        """Test that avoid_duplicates produces different problems."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ['batch', '10', '--file', 'batch.json', '--avoid-duplicates'])
            assert result.exit_code == 0

            with open('batch.json') as f:
                data = json.load(f)
                test_ids = [p['test_id'] for p in data]
                # Should have mostly unique IDs
                assert len(set(test_ids)) >= 7  # At least 70% unique

    def test_batch_missing_file(self):
        """Test error when file parameter is missing."""
        runner = CliRunner()
        result = runner.invoke(cli, ['batch', '5'])
        assert result.exit_code != 0


class TestListCommand:
    """Test the list command."""

    def test_list_all(self):
        """Test listing all options."""
        runner = CliRunner()
        result = runner.invoke(cli, ['list'])
        assert result.exit_code == 0
        assert 'Math Topics:' in result.output
        assert 'Problem Families:' in result.output
        assert 'Grade Levels:' in result.output
        assert 'Complexity Levels:' in result.output

    def test_list_topics(self):
        """Test listing just topics."""
        runner = CliRunner()
        result = runner.invoke(cli, ['list', 'topics'])
        assert result.exit_code == 0
        assert 'arithmetic' in result.output
        assert 'percentages' in result.output

    def test_list_families(self):
        """Test listing just families."""
        runner = CliRunner()
        result = runner.invoke(cli, ['list', 'families'])
        assert result.exit_code == 0
        assert 'sequential_purchase' in result.output
        assert 'rate_time' in result.output

    def test_list_grades(self):
        """Test listing just grades."""
        runner = CliRunner()
        result = runner.invoke(cli, ['list', 'grades'])
        assert result.exit_code == 0
        assert 'elementary' in result.output
        assert 'middle' in result.output
        assert 'high' in result.output

    def test_list_verbose(self):
        """Test verbose mode with descriptions."""
        runner = CliRunner()
        result = runner.invoke(cli, ['list', 'topics', '-v'])
        assert result.exit_code == 0
        # Should include descriptions
        assert 'Basic arithmetic' in result.output or 'operations' in result.output


class TestInfoCommand:
    """Test the info command."""

    def test_info_topic(self):
        """Test showing info about a topic."""
        runner = CliRunner()
        result = runner.invoke(cli, ['info', 'arithmetic'])
        assert result.exit_code == 0
        assert 'arithmetic' in result.output
        assert 'Topic:' in result.output

    def test_info_family(self):
        """Test showing info about a family."""
        runner = CliRunner()
        result = runner.invoke(cli, ['info', 'sequential_purchase'])
        assert result.exit_code == 0
        assert 'sequential_purchase' in result.output
        assert 'Problem Family:' in result.output

    def test_info_invalid_name(self):
        """Test error for invalid topic/family name."""
        runner = CliRunner()
        result = runner.invoke(cli, ['info', 'invalid_name'])
        assert result.exit_code == 0  # Command runs but shows error
        assert 'Error' in result.output or 'not a valid' in result.output


class TestCLIHelp:
    """Test help messages."""

    def test_main_help(self):
        """Test main help message."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'Math Problem Generator' in result.output
        assert 'generate' in result.output
        assert 'batch' in result.output
        assert 'list' in result.output

    def test_generate_help(self):
        """Test generate command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ['generate', '--help'])
        assert result.exit_code == 0
        assert 'complexity' in result.output
        assert 'grade' in result.output
        assert 'seed' in result.output

    def test_batch_help(self):
        """Test batch command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ['batch', '--help'])
        assert result.exit_code == 0
        assert 'COUNT' in result.output
        assert 'file' in result.output

    def test_version(self):
        """Test version flag."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert '0.1.0' in result.output
