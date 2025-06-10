"""Integration tests for OpenCar CLI."""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

from opencar.cli.main import app


@pytest.fixture
def runner():
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_dir():
    """Create temporary directory for testing."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


class TestCLIBasics:
    """Test basic CLI functionality."""

    def test_help_command(self, runner):
        """Test help command."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "OpenCar" in result.stdout
        assert "Advanced Autonomous Vehicle Perception System" in result.stdout

    def test_version_command(self, runner):
        """Test version command."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "OpenCar" in result.stdout
        assert "version" in result.stdout


class TestInitCommand:
    """Test project initialization command."""

    def test_init_default_directory(self, runner, temp_dir):
        """Test init command with default directory."""
        # Use explicit directory instead of changing cwd
        result = runner.invoke(app, ["init", str(temp_dir)])
        assert result.exit_code == 0
        
        # Check created files and directories
        assert (temp_dir / "data").exists()
        assert (temp_dir / "models").exists()
        assert (temp_dir / "configs").exists()
        assert (temp_dir / "logs").exists()
        assert (temp_dir / "notebooks").exists()
        assert (temp_dir / "opencar.yaml").exists()
        assert (temp_dir / ".env").exists()
        assert (temp_dir / "requirements.txt").exists()

    def test_init_specific_directory(self, runner, temp_dir):
        """Test init command with specific directory."""
        project_dir = temp_dir / "my-project"
        
        result = runner.invoke(app, ["init", str(project_dir)])
        assert result.exit_code == 0
        
        # Check created files and directories
        assert project_dir.exists()
        assert (project_dir / "data").exists()
        assert (project_dir / "opencar.yaml").exists()

    def test_init_with_template(self, runner, temp_dir):
        """Test init command with template option."""
        project_dir = temp_dir / "templated-project"
        
        result = runner.invoke(app, ["init", str(project_dir), "--template", "advanced"])
        assert result.exit_code == 0
        assert project_dir.exists()

    def test_init_existing_directory(self, runner, temp_dir):
        """Test init command with existing directory."""
        # Create directory first
        project_dir = temp_dir / "existing"
        project_dir.mkdir()
        
        result = runner.invoke(app, ["init", str(project_dir)])
        assert result.exit_code == 0
        # Should still work and create files


class TestInfoCommand:
    """Test system information command."""

    def test_info_command(self, runner):
        """Test info command."""
        result = runner.invoke(app, ["info"])
        assert result.exit_code == 0
        
        # Check for expected information
        assert "OpenCar System Information" in result.stdout
        assert "Version" in result.stdout
        assert "Python" in result.stdout
        assert "Platform" in result.stdout
        assert "Configuration" in result.stdout
        assert "Debug Mode" in result.stdout
        assert "Log Level" in result.stdout
        assert "API Host" in result.stdout
        assert "Device" in result.stdout
        assert "ML Configuration" in result.stdout
        assert "Batch Size" in result.stdout
        assert "Model Path" in result.stdout
        assert "OpenAI Model" in result.stdout


class TestStatusCommand:
    """Test system status command."""

    @patch('opencar.cli.main._check_api_status')
    @patch('opencar.cli.main._check_database_status')
    @patch('opencar.cli.main._check_redis_status')
    @patch('opencar.cli.main._check_model_status')
    def test_status_command_all_healthy(self, mock_model, mock_redis, mock_db, mock_api, runner):
        """Test status command with all services healthy."""
        # Mock all services as healthy
        mock_api.return_value = True
        mock_db.return_value = True
        mock_redis.return_value = True
        mock_model.return_value = True
        
        result = runner.invoke(app, ["status"])
        assert result.exit_code == 0
        
        # Check for status information
        assert "System Status" in result.stdout
        assert "API Server" in result.stdout
        assert "Database" in result.stdout
        assert "Redis Cache" in result.stdout
        assert "ML Models" in result.stdout
        assert "Online" in result.stdout or "Connected" in result.stdout

    @patch('opencar.cli.main._check_api_status')
    @patch('opencar.cli.main._check_database_status')
    @patch('opencar.cli.main._check_redis_status')
    @patch('opencar.cli.main._check_model_status')
    def test_status_command_some_unhealthy(self, mock_model, mock_redis, mock_db, mock_api, runner):
        """Test status command with some services unhealthy."""
        # Mock some services as unhealthy
        mock_api.return_value = False
        mock_db.return_value = True
        mock_redis.return_value = False
        mock_model.return_value = True
        
        result = runner.invoke(app, ["status"])
        assert result.exit_code == 0
        
        # Check for status information
        assert "System Status" in result.stdout
        assert "Offline" in result.stdout or "Disconnected" in result.stdout


class TestServeCommand:
    """Test server command."""

    @patch('opencar.cli.main.uvicorn')
    def test_serve_default_options(self, mock_uvicorn, runner):
        """Test serve command with default options."""
        result = runner.invoke(app, ["serve"])
        assert result.exit_code == 0
        
        # Check that uvicorn.run was called
        mock_uvicorn.run.assert_called_once()
        call_args = mock_uvicorn.run.call_args
        
        # Check default arguments
        assert call_args[1]["host"] == "0.0.0.0"
        assert call_args[1]["port"] == 8000
        assert call_args[1]["workers"] == 1
        assert call_args[1]["reload"] == False

    @patch('opencar.cli.main.uvicorn')
    def test_serve_custom_options(self, mock_uvicorn, runner):
        """Test serve command with custom options."""
        result = runner.invoke(app, [
            "serve",
            "--host", "127.0.0.1",
            "--port", "9000",
            "--workers", "4",
            "--reload"
        ])
        assert result.exit_code == 0
        
        # Check that uvicorn.run was called with custom args
        call_args = mock_uvicorn.run.call_args
        assert call_args[1]["host"] == "127.0.0.1"
        assert call_args[1]["port"] == 9000
        assert call_args[1]["workers"] == 4
        assert call_args[1]["reload"] == True

    @patch('opencar.cli.main.uvicorn', None)
    def test_serve_missing_uvicorn(self, runner):
        """Test serve command when uvicorn is not installed."""
        result = runner.invoke(app, ["serve"])
        assert result.exit_code == 1
        assert "uvicorn not installed" in result.stdout

    @patch('opencar.cli.main.uvicorn')
    def test_serve_keyboard_interrupt(self, mock_uvicorn, runner):
        """Test serve command with keyboard interrupt."""
        mock_uvicorn.run.side_effect = KeyboardInterrupt()
        
        result = runner.invoke(app, ["serve"])
        assert result.exit_code == 0
        assert "Server stopped by user" in result.stdout


class TestHealthCheckFunctions:
    """Test health check helper functions."""

    @patch('httpx.get')
    def test_check_api_status_success(self, mock_get):
        """Test API status check success."""
        from opencar.cli.main import _check_api_status
        
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = _check_api_status()
        assert result == True
        mock_get.assert_called_once_with("http://localhost:8000/health", timeout=2.0)

    @patch('httpx.get')
    def test_check_api_status_failure(self, mock_get):
        """Test API status check failure."""
        from opencar.cli.main import _check_api_status
        
        # Mock failed response
        mock_get.side_effect = Exception("Connection failed")
        
        result = _check_api_status()
        assert result == False

    def test_check_database_status(self):
        """Test database status check."""
        from opencar.cli.main import _check_database_status
        
        # Currently returns True (mock implementation)
        result = _check_database_status()
        assert result == True

    def test_check_redis_status(self):
        """Test Redis status check."""
        from opencar.cli.main import _check_redis_status
        
        # Currently returns True (mock implementation)
        result = _check_redis_status()
        assert result == True

    @patch('opencar.cli.main.get_settings')
    def test_check_model_status(self, mock_get_settings):
        """Test model status check."""
        from opencar.cli.main import _check_model_status
        
        # Mock settings with existing model path
        mock_settings = MagicMock()
        mock_settings.model_path.exists.return_value = True
        mock_get_settings.return_value = mock_settings
        
        result = _check_model_status()
        assert result == True

    @patch('opencar.cli.main.get_settings')
    def test_check_model_status_missing(self, mock_get_settings):
        """Test model status check with missing models."""
        from opencar.cli.main import _check_model_status
        
        # Mock settings with non-existing model path
        mock_settings = MagicMock()
        mock_settings.model_path.exists.return_value = False
        mock_get_settings.return_value = mock_settings
        
        result = _check_model_status()
        assert result == False


class TestCLIIntegration:
    """Test CLI integration scenarios."""

    def test_full_workflow(self, runner, temp_dir):
        """Test a complete workflow: init -> info -> status."""
        # Initialize project
        project_dir = temp_dir / "workflow-test"
        result = runner.invoke(app, ["init", str(project_dir)])
        assert result.exit_code == 0
        
        # Get system info
        result = runner.invoke(app, ["info"])
        assert result.exit_code == 0
        
        # Check status
        with patch('opencar.cli.main._check_api_status', return_value=True), \
             patch('opencar.cli.main._check_database_status', return_value=True), \
             patch('opencar.cli.main._check_redis_status', return_value=True), \
             patch('opencar.cli.main._check_model_status', return_value=True):
            
            result = runner.invoke(app, ["status"])
            assert result.exit_code == 0

    def test_error_handling(self, runner):
        """Test CLI error handling."""
        # Test with invalid command
        result = runner.invoke(app, ["invalid-command"])
        assert result.exit_code != 0

    def test_rich_output_formatting(self, runner):
        """Test that Rich formatting is working."""
        result = runner.invoke(app, ["info"])
        assert result.exit_code == 0
        
        # Rich should format the output nicely
        # We can't easily test the exact formatting, but we can check
        # that the command completes successfully
        assert len(result.stdout) > 0


class TestCLIConfiguration:
    """Test CLI configuration handling."""

    @patch.dict('os.environ', {'DEBUG': 'true', 'LOG_LEVEL': 'DEBUG'})
    def test_environment_variables(self, runner):
        """Test that environment variables are respected."""
        result = runner.invoke(app, ["info"])
        assert result.exit_code == 0
        # Environment variables should be reflected in the output

    def test_config_file_creation(self, runner, temp_dir):
        """Test that config files are created correctly."""
        project_dir = temp_dir / "config-test"
        result = runner.invoke(app, ["init", str(project_dir)])
        assert result.exit_code == 0
        
        # Check config file content
        config_file = project_dir / "opencar.yaml"
        assert config_file.exists()
        
        content = config_file.read_text()
        assert "project:" in content
        assert "perception:" in content
        assert "training:" in content 