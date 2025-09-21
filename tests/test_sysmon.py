"""
Tests for System Monitoring Commands

Tests cpu, mem, ps command implementations.
"""

import pytest
import psutil
from unittest.mock import patch, MagicMock
from app.commands.sysmon import (
    cmd_cpu, cmd_mem, cmd_ps, cmd_disk, cmd_uptime, cmd_net
)


class TestCpu:
    """Test cpu command."""
    
    def test_cpu_basic(self):
        """Test basic CPU command."""
        result = cmd_cpu([])
        assert "CPU Information" in result
        assert "CPU Cores" in result
        assert "Overall CPU Usage" in result
    
    def test_cpu_with_per_cpu(self):
        """Test CPU command with per-CPU option."""
        result = cmd_cpu(["-p"])
        assert "Per-CPU Usage" in result
    
    def test_cpu_with_interval(self):
        """Test CPU command with custom interval."""
        result = cmd_cpu(["-i", "0.5"])
        assert "CPU Information" in result
    
    def test_cpu_with_count(self):
        """Test CPU command with multiple updates."""
        result = cmd_cpu(["-c", "2"])
        assert "CPU Information" in result
    
    @patch('psutil.cpu_percent')
    def test_cpu_error_handling(self, mock_cpu_percent):
        """Test CPU command error handling."""
        mock_cpu_percent.side_effect = Exception("CPU error")
        result = cmd_cpu([])
        assert "Error getting CPU information" in result


class TestMem:
    """Test mem command."""
    
    def test_mem_basic(self):
        """Test basic memory command."""
        result = cmd_mem([])
        assert "Memory Information" in result
        assert "Virtual Memory" in result
        assert "Total:" in result
        assert "Used:" in result
        assert "Free:" in result
        assert "Usage:" in result
    
    def test_mem_with_swap(self):
        """Test memory command with swap information."""
        result = cmd_mem(["-s"])
        assert "Swap Information" in result
    
    def test_mem_with_detailed(self):
        """Test memory command with detailed breakdown."""
        result = cmd_mem(["-d"])
        assert "Detailed Breakdown" in result
        assert "Active:" in result
        assert "Inactive:" in result
    
    @patch('psutil.virtual_memory')
    def test_mem_error_handling(self, mock_virtual_memory):
        """Test memory command error handling."""
        mock_virtual_memory.side_effect = Exception("Memory error")
        result = cmd_mem([])
        assert "Error getting memory information" in result


class TestPs:
    """Test ps command."""
    
    def test_ps_basic(self):
        """Test basic process listing."""
        result = cmd_ps([])
        assert "Running Processes" in result
        assert "PID" in result
        assert "Name" in result
        assert "User" in result
    
    def test_ps_with_limit(self):
        """Test process listing with limit."""
        result = cmd_ps(["-n", "5"])
        assert "Running Processes" in result
    
    def test_ps_sort_by_cpu(self):
        """Test process listing sorted by CPU."""
        result = cmd_ps(["-s"])
        assert "Running Processes" in result
    
    def test_ps_sort_by_memory(self):
        """Test process listing sorted by memory."""
        result = cmd_ps(["-m"])
        assert "Running Processes" in result
    
    def test_ps_user_only(self):
        """Test process listing for user processes only."""
        result = cmd_ps(["-u"])
        assert "Running Processes" in result
    
    def test_ps_all_processes(self):
        """Test process listing for all processes."""
        result = cmd_ps(["-a"])
        assert "Running Processes" in result
    
    def test_ps_specific_pid(self):
        """Test process listing for specific PID."""
        # Get current process PID
        current_pid = psutil.Process().pid
        result = cmd_ps(["-p", str(current_pid)])
        assert "Running Processes" in result
    
    @patch('psutil.process_iter')
    def test_ps_error_handling(self, mock_process_iter):
        """Test process command error handling."""
        mock_process_iter.side_effect = Exception("Process error")
        result = cmd_ps([])
        assert "Error getting process information" in result


class TestDisk:
    """Test disk command."""
    
    def test_disk_basic(self):
        """Test basic disk command."""
        result = cmd_disk([])
        assert "Disk Information" in result
        assert "Overall Disk Usage" in result
        assert "Total:" in result
        assert "Used:" in result
        assert "Free:" in result
    
    def test_disk_with_all_filesystems(self):
        """Test disk command with all filesystems."""
        result = cmd_disk(["-a"])
        assert "Disk Information" in result
    
    def test_disk_human_readable(self):
        """Test disk command with human-readable format."""
        result = cmd_disk(["-h"])
        assert "Disk Information" in result
    
    @patch('psutil.disk_usage')
    def test_disk_error_handling(self, mock_disk_usage):
        """Test disk command error handling."""
        mock_disk_usage.side_effect = Exception("Disk error")
        result = cmd_disk([])
        assert "Error getting disk information" in result


class TestUptime:
    """Test uptime command."""
    
    def test_uptime_basic(self):
        """Test basic uptime command."""
        result = cmd_uptime([])
        assert "System Uptime" in result
        assert "Uptime:" in result
        assert "Boot Time:" in result
    
    @patch('psutil.boot_time')
    def test_uptime_error_handling(self, mock_boot_time):
        """Test uptime command error handling."""
        mock_boot_time.side_effect = Exception("Uptime error")
        result = cmd_uptime([])
        assert "Error getting uptime information" in result


class TestNet:
    """Test net command."""
    
    def test_net_basic(self):
        """Test basic network command."""
        result = cmd_net([])
        assert "Network Information" in result
        assert "Network Statistics" in result
    
    def test_net_with_interfaces(self):
        """Test network command with interfaces."""
        result = cmd_net(["-i"])
        assert "Network Information" in result
        assert "Network Interfaces" in result
    
    def test_net_with_statistics(self):
        """Test network command with statistics."""
        result = cmd_net(["-s"])
        assert "Network Statistics" in result
    
    @patch('psutil.net_io_counters')
    def test_net_error_handling(self, mock_net_io):
        """Test network command error handling."""
        mock_net_io.side_effect = Exception("Network error")
        result = cmd_net([])
        assert "Error getting network information" in result


class TestSystemMonitoringIntegration:
    """Integration tests for system monitoring commands."""
    
    def test_all_commands_return_strings(self):
        """Test that all system monitoring commands return strings."""
        commands = [cmd_cpu, cmd_mem, cmd_ps, cmd_disk, cmd_uptime, cmd_net]
        
        for cmd in commands:
            result = cmd([])
            assert isinstance(result, str)
            assert len(result) > 0
    
    def test_commands_handle_empty_args(self):
        """Test that commands handle empty arguments gracefully."""
        commands = [cmd_cpu, cmd_mem, cmd_ps, cmd_disk, cmd_uptime, cmd_net]
        
        for cmd in commands:
            result = cmd([])
            assert isinstance(result, str)
            assert len(result) > 0
    
    def test_commands_handle_invalid_args(self):
        """Test that commands handle invalid arguments gracefully."""
        # Test with invalid numeric arguments
        result = cmd_cpu(["-i", "invalid"])
        assert "Error" in result
        
        result = cmd_cpu(["-c", "invalid"])
        assert "Error" in result
        
        result = cmd_ps(["-n", "invalid"])
        assert "Error" in result
        
        result = cmd_ps(["-p", "invalid"])
        assert "Error" in result