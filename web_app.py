#!/usr/bin/env python3
"""
PyTerm Web Interface
A simple web wrapper for PyTerm to demonstrate functionality online
"""

from flask import Flask, render_template, request, jsonify
import subprocess
import os
import tempfile
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/command', methods=['POST'])
def execute_command():
    """Execute a PyTerm command and return the result"""
    try:
        data = request.get_json()
        command = data.get('command', '')
        
        if not command:
            return jsonify({'error': 'No command provided'}), 400
        
        # Create a temporary file to capture output
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
            f.write(command + '\nexit\n')
            temp_file = f.name
        
        try:
            # Run PyTerm with the command
            result = subprocess.run(
                ['python', 'main.py'],
                input=f'{command}\nexit\n',
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return jsonify({
                'output': result.stdout,
                'error': result.stderr,
                'return_code': result.returncode
            })
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file):
                os.unlink(temp_file)
                
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Command timed out'}), 408
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/demo')
def demo_commands():
    """Return demo commands for the web interface"""
    demo_commands = [
        {
            'command': 'show me the files',
            'description': 'List directory contents using natural language',
            'traditional': 'ls'
        },
        {
            'command': 'create a folder called demo',
            'description': 'Create a directory using natural language',
            'traditional': 'mkdir demo'
        },
        {
            'command': 'what processes are running?',
            'description': 'Show running processes',
            'traditional': 'ps'
        },
        {
            'command': 'how much memory am I using?',
            'description': 'Display memory usage',
            'traditional': 'mem'
        },
        {
            'command': 'show me CPU usage',
            'description': 'Display CPU information',
            'traditional': 'cpu'
        }
    ]
    
    return jsonify({'commands': demo_commands})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
