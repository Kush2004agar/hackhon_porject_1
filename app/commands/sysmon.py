"""
System Monitoring Commands Module

Implements system monitoring operations: cpu, mem, ps
Uses psutil for cross-platform system information.
"""

import os
import time
from typing import List, Optional, Dict, Any
import psutil
from ..config import get_error_message
from ..utils import (
    PyTermError, colorize, format_size, format_percentage, 
    format_table, truncate_text
)


def cmd_cpu(args: List[str]) -> str:
    """
    Display CPU usage information.
    
    Usage: cpu [options]
    Options:
        -i <seconds>    Update interval (default: 1 second)
        -c <count>      Number of updates (default: 1)
        -p              Show per-CPU usage
    """
    interval = 1
    count = 1
    per_cpu = False
    
    # Parse arguments
    i = 0
    while i < len(args):
        if args[i] == '-i' and i + 1 < len(args):
            try:
                interval = float(args[i + 1])
                i += 2
            except ValueError:
                return "Error: Invalid interval value"
        elif args[i] == '-c' and i + 1 < len(args):
            try:
                count = int(args[i + 1])
                i += 2
            except ValueError:
                return "Error: Invalid count value"
        elif args[i] == '-p':
            per_cpu = True
            i += 1
        else:
            i += 1
    
    try:
        results = []
        
        for update in range(count):
            if update > 0:
                time.sleep(interval)
            
            # Get CPU information
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Format output
            if update == 0:
                results.append(f"{colorize('CPU Information', 'bold')}")
                results.append(f"CPU Cores: {colorize(str(cpu_count), 'cyan')}")
                if cpu_freq:
                    results.append(f"Current Frequency: {colorize(f'{cpu_freq.current:.0f} MHz', 'cyan')}")
                    results.append(f"Min Frequency: {colorize(f'{cpu_freq.min:.0f} MHz', 'cyan')}")
                    results.append(f"Max Frequency: {colorize(f'{cpu_freq.max:.0f} MHz', 'cyan')}")
                results.append("")
            
            # Overall CPU usage
            cpu_color = "red" if cpu_percent > 80 else "yellow" if cpu_percent > 60 else "green"
            results.append(f"Overall CPU Usage: {colorize(f'{cpu_percent:.1f}%', cpu_color)}")
            
            # Per-CPU usage
            if per_cpu:
                per_cpu_percent = psutil.cpu_percent(percpu=True, interval=0.1)
                results.append("Per-CPU Usage:")
                for i, cpu_pct in enumerate(per_cpu_percent):
                    cpu_color = "red" if cpu_pct > 80 else "yellow" if cpu_pct > 60 else "green"
                    results.append(f"  CPU {i:2d}: {colorize(f'{cpu_pct:5.1f}%', cpu_color)}")
            
            # CPU times
            cpu_times = psutil.cpu_times()
            results.append(f"User Time: {colorize(f'{cpu_times.user:.1f}s', 'blue')}")
            results.append(f"System Time: {colorize(f'{cpu_times.system:.1f}s', 'blue')}")
            results.append(f"Idle Time: {colorize(f'{cpu_times.idle:.1f}s', 'blue')}")
            
            if count > 1 and update < count - 1:
                results.append("")
        
        return "\n".join(results)
        
    except Exception as e:
        return f"Error getting CPU information: {e}"


def cmd_mem(args: List[str]) -> str:
    """
    Display memory usage information.
    
    Usage: mem [options]
    Options:
        -s    Show swap information
        -d    Show detailed memory breakdown
    """
    show_swap = False
    detailed = False
    
    # Parse arguments
    for arg in args:
        if arg == '-s':
            show_swap = True
        elif arg == '-d':
            detailed = True
    
    try:
        results = []
        
        # Get memory information
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        results.append(f"{colorize('Memory Information', 'bold')}")
        results.append("")
        
        # Virtual memory
        results.append(f"{colorize('Virtual Memory:', 'yellow')}")
        results.append(f"Total: {colorize(format_size(memory.total), 'cyan')}")
        results.append(f"Available: {colorize(format_size(memory.available), 'green')}")
        results.append(f"Used: {colorize(format_size(memory.used), 'red')}")
        results.append(f"Free: {colorize(format_size(memory.free), 'green')}")
        
        # Usage percentage with color coding
        usage_color = "red" if memory.percent > 80 else "yellow" if memory.percent > 60 else "green"
        results.append(f"Usage: {colorize(f'{memory.percent:.1f}%', usage_color)}")
        
        # Memory bar visualization
        bar_length = 50
        used_length = int((memory.percent / 100) * bar_length)
        bar = "█" * used_length + "░" * (bar_length - used_length)
        results.append(f"Visual: [{colorize(bar, usage_color)}]")
        
        if detailed:
            results.append("")
            results.append(f"{colorize('Detailed Breakdown:', 'yellow')}")
            results.append(f"Active: {colorize(format_size(memory.active), 'blue')}")
            results.append(f"Inactive: {colorize(format_size(memory.inactive), 'blue')}")
            results.append(f"Buffers: {colorize(format_size(memory.buffers), 'blue')}")
            results.append(f"Cached: {colorize(format_size(memory.cached), 'blue')}")
            results.append(f"Shared: {colorize(format_size(memory.shared), 'blue')}")
        
        # Swap information
        if show_swap:
            results.append("")
            results.append(f"{colorize('Swap Information:', 'yellow')}")
            results.append(f"Total: {colorize(format_size(swap.total), 'cyan')}")
            results.append(f"Used: {colorize(format_size(swap.used), 'red')}")
            results.append(f"Free: {colorize(format_size(swap.free), 'green')}")
            
            swap_color = "red" if swap.percent > 80 else "yellow" if swap.percent > 60 else "green"
            results.append(f"Usage: {colorize(f'{swap.percent:.1f}%', swap_color)}")
            
            if swap.sin > 0 or swap.sout > 0:
                results.append(f"Swap In: {colorize(format_size(swap.sin), 'blue')}")
                results.append(f"Swap Out: {colorize(format_size(swap.sout), 'blue')}")
        
        return "\n".join(results)
        
    except Exception as e:
        return f"Error getting memory information: {e}"


def cmd_ps(args: List[str]) -> str:
    """
    Display running processes.
    
    Usage: ps [options]
    Options:
        -a    Show all processes (including system)
        -u    Show user processes only
        -p <pid>    Show specific process by PID
        -n <num>    Limit number of processes (default: 20)
        -s    Sort by CPU usage
        -m    Sort by memory usage
    """
    show_all = False
    user_only = False
    specific_pid = None
    limit = 20
    sort_by = "cpu"  # cpu, memory, pid
    
    # Parse arguments
    i = 0
    while i < len(args):
        if args[i] == '-a':
            show_all = True
            i += 1
        elif args[i] == '-u':
            user_only = True
            i += 1
        elif args[i] == '-p' and i + 1 < len(args):
            try:
                specific_pid = int(args[i + 1])
                i += 2
            except ValueError:
                return "Error: Invalid PID"
        elif args[i] == '-n' and i + 1 < len(args):
            try:
                limit = int(args[i + 1])
                i += 2
            except ValueError:
                return "Error: Invalid number"
        elif args[i] == '-s':
            sort_by = "cpu"
            i += 1
        elif args[i] == '-m':
            sort_by = "memory"
            i += 1
        else:
            i += 1
    
    try:
        results = []
        processes = []
        
        # Get current user
        current_user = psutil.Process().username()
        
        # Collect process information
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'status', 'create_time']):
            try:
                proc_info = proc.info
                
                # Filter by user if requested
                if user_only and proc_info['username'] != current_user:
                    continue
                
                # Filter system processes if not showing all
                if not show_all and proc_info['username'] in ['SYSTEM', 'root', 'daemon']:
                    continue
                
                # Filter by specific PID
                if specific_pid and proc_info['pid'] != specific_pid:
                    continue
                
                processes.append(proc_info)
                
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        if not processes:
            return "No processes found matching criteria."
        
        # Sort processes
        if sort_by == "cpu":
            processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
        elif sort_by == "memory":
            processes.sort(key=lambda x: x['memory_percent'] or 0, reverse=True)
        else:
            processes.sort(key=lambda x: x['pid'])
        
        # Limit results
        processes = processes[:limit]
        
        # Format output
        results.append(f"{colorize('Running Processes', 'bold')}")
        results.append(f"Showing {len(processes)} processes")
        results.append("")
        
        # Table headers
        headers = ["PID", "Name", "User", "CPU%", "Memory%", "Status"]
        table_data = []
        
        for proc in processes:
            pid = str(proc['pid'])
            name = truncate_text(proc['name'], 20)
            user = truncate_text(proc['username'] or 'N/A', 12)
            cpu_pct = f"{proc['cpu_percent']:.1f}" if proc['cpu_percent'] else "0.0"
            mem_pct = f"{proc['memory_percent']:.1f}" if proc['memory_percent'] else "0.0"
            status = proc['status'] or 'N/A'
            
            table_data.append([pid, name, user, cpu_pct, mem_pct, status])
        
        results.append(format_table(table_data, headers))
        
        return "\n".join(results)
        
    except Exception as e:
        return f"Error getting process information: {e}"


def cmd_disk(args: List[str]) -> str:
    """
    Display disk usage information.
    
    Usage: disk [options]
    Options:
        -a    Show all mounted filesystems
        -h    Show in human-readable format
    """
    show_all = False
    human_readable = True
    
    # Parse arguments
    for arg in args:
        if arg == '-a':
            show_all = True
        elif arg == '-h':
            human_readable = True
    
    try:
        results = []
        
        # Get disk usage
        disk_usage = psutil.disk_usage('/')
        disk_io = psutil.disk_io_counters()
        partitions = psutil.disk_partitions()
        
        results.append(f"{colorize('Disk Information', 'bold')}")
        results.append("")
        
        # Overall disk usage
        results.append(f"{colorize('Overall Disk Usage:', 'yellow')}")
        if human_readable:
            results.append(f"Total: {colorize(format_size(disk_usage.total), 'cyan')}")
            results.append(f"Used: {colorize(format_size(disk_usage.used), 'red')}")
            results.append(f"Free: {colorize(format_size(disk_usage.free), 'green')}")
        else:
            results.append(f"Total: {colorize(str(disk_usage.total), 'cyan')} bytes")
            results.append(f"Used: {colorize(str(disk_usage.used), 'red')} bytes")
            results.append(f"Free: {colorize(str(disk_usage.free), 'green')} bytes")
        
        # Usage percentage
        usage_color = "red" if disk_usage.percent > 80 else "yellow" if disk_usage.percent > 60 else "green"
        results.append(f"Usage: {colorize(f'{disk_usage.percent:.1f}%', usage_color)}")
        
        # Disk I/O statistics
        if disk_io:
            results.append("")
            results.append(f"{colorize('Disk I/O Statistics:', 'yellow')}")
            if human_readable:
                results.append(f"Read: {colorize(format_size(disk_io.read_bytes), 'blue')}")
                results.append(f"Written: {colorize(format_size(disk_io.write_bytes), 'blue')}")
            else:
                results.append(f"Read: {colorize(str(disk_io.read_bytes), 'blue')} bytes")
                results.append(f"Written: {colorize(str(disk_io.write_bytes), 'blue')} bytes")
            results.append(f"Read Count: {colorize(str(disk_io.read_count), 'blue')}")
            results.append(f"Write Count: {colorize(str(disk_io.write_count), 'blue')}")
        
        # Partition information
        if show_all and partitions:
            results.append("")
            results.append(f"{colorize('Mounted Filesystems:', 'yellow')}")
            
            table_data = []
            for partition in partitions:
                try:
                    partition_usage = psutil.disk_usage(partition.mountpoint)
                    device = partition.device
                    mountpoint = partition.mountpoint
                    fstype = partition.fstype
                    
                    if human_readable:
                        total = format_size(partition_usage.total)
                        used = format_size(partition_usage.used)
                        free = format_size(partition_usage.free)
                    else:
                        total = str(partition_usage.total)
                        used = str(partition_usage.used)
                        free = str(partition_usage.free)
                    
                    usage_pct = f"{partition_usage.percent:.1f}%"
                    
                    table_data.append([device, mountpoint, fstype, total, used, free, usage_pct])
                    
                except PermissionError:
                    continue
            
            if table_data:
                headers = ["Device", "Mountpoint", "Type", "Total", "Used", "Free", "Usage%"]
                results.append(format_table(table_data, headers))
        
        return "\n".join(results)
        
    except Exception as e:
        return f"Error getting disk information: {e}"


def cmd_uptime(args: List[str]) -> str:
    """
    Display system uptime information.
    
    Usage: uptime
    """
    try:
        results = []
        
        # Get boot time and current time
        boot_time = psutil.boot_time()
        current_time = time.time()
        uptime_seconds = current_time - boot_time
        
        # Calculate uptime components
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        seconds = int(uptime_seconds % 60)
        
        # Get load average (Unix-like systems)
        try:
            load_avg = os.getloadavg()
            load_avg_str = f"{load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}"
        except AttributeError:
            load_avg_str = "N/A (Windows)"
        
        # Get number of users
        try:
            users = len(psutil.users())
        except:
            users = "N/A"
        
        results.append(f"{colorize('System Uptime', 'bold')}")
        results.append("")
        
        # Uptime
        uptime_parts = []
        if days > 0:
            uptime_parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours > 0:
            uptime_parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes > 0:
            uptime_parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        if seconds > 0 and not uptime_parts:
            uptime_parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
        
        uptime_str = ", ".join(uptime_parts) if uptime_parts else "Less than 1 second"
        results.append(f"Uptime: {colorize(uptime_str, 'green')}")
        
        # Boot time
        boot_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(boot_time))
        results.append(f"Boot Time: {colorize(boot_time_str, 'cyan')}")
        
        # Load average
        results.append(f"Load Average: {colorize(load_avg_str, 'yellow')}")
        
        # Users
        results.append(f"Users: {colorize(str(users), 'blue')}")
        
        return "\n".join(results)
        
    except Exception as e:
        return f"Error getting uptime information: {e}"


def cmd_net(args: List[str]) -> str:
    """
    Display network information.
    
    Usage: net [options]
    Options:
        -i    Show network interfaces
        -s    Show network statistics
    """
    show_interfaces = False
    show_stats = False
    
    # Parse arguments
    for arg in args:
        if arg == '-i':
            show_interfaces = True
        elif arg == '-s':
            show_stats = True
    
    # Default to showing stats if no options specified
    if not show_interfaces and not show_stats:
        show_stats = True
    
    try:
        results = []
        
        results.append(f"{colorize('Network Information', 'bold')}")
        results.append("")
        
        # Network statistics
        if show_stats:
            net_io = psutil.net_io_counters()
            net_connections = psutil.net_connections()
            
            results.append(f"{colorize('Network Statistics:', 'yellow')}")
            results.append(f"Bytes Sent: {colorize(format_size(net_io.bytes_sent), 'green')}")
            results.append(f"Bytes Received: {colorize(format_size(net_io.bytes_recv), 'green')}")
            results.append(f"Packets Sent: {colorize(str(net_io.packets_sent), 'blue')}")
            results.append(f"Packets Received: {colorize(str(net_io.packets_recv), 'blue')}")
            results.append(f"Active Connections: {colorize(str(len(net_connections)), 'cyan')}")
            results.append("")
        
        # Network interfaces
        if show_interfaces:
            net_if_addrs = psutil.net_if_addrs()
            net_if_stats = psutil.net_if_stats()
            
            results.append(f"{colorize('Network Interfaces:', 'yellow')}")
            
            table_data = []
            for interface, addresses in net_if_addrs.items():
                stats = net_if_stats.get(interface)
                
                # Get primary address
                primary_addr = "N/A"
                for addr in addresses:
                    if addr.family == 2:  # IPv4
                        primary_addr = addr.address
                        break
                
                # Interface status
                if stats:
                    is_up = "UP" if stats.isup else "DOWN"
                    speed = f"{stats.speed} Mbps" if stats.speed > 0 else "N/A"
                else:
                    is_up = "N/A"
                    speed = "N/A"
                
                table_data.append([interface, primary_addr, is_up, speed])
            
            if table_data:
                headers = ["Interface", "Address", "Status", "Speed"]
                results.append(format_table(table_data, headers))
        
        return "\n".join(results)
        
    except Exception as e:
        return f"Error getting network information: {e}"
