from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route('/')
def index():
    """Serve the main demo page"""
    with open('index.html', 'r') as f:
        return f.read()

@app.route('/command', methods=['POST'])
def execute_command():
    """Execute a PyTerm command and return the result"""
    try:
        data = request.get_json()
        command = data.get('command', '')
        
        if not command:
            return jsonify({'error': 'No command provided'}), 400
        
        # For Vercel, we'll simulate PyTerm responses since we can't run subprocess
        # This creates a realistic demo experience
        responses = {
            'show me the files': {
                'output': 'app/  main.py  README.md  requirements.txt  tests/  vercel.json\n',
                'error': '',
                'return_code': 0
            },
            'create a folder called demo': {
                'output': 'Created directory: demo\n',
                'error': '',
                'return_code': 0
            },
            'what processes are running?': {
                'output': 'PID    Name                    CPU%    Memory%   Status\n1234   python.exe              2.5     1.2       running\n5678   chrome.exe              15.3    8.7       running\n',
                'error': '',
                'return_code': 0
            },
            'how much memory am I using?': {
                'output': 'Memory Usage: 45.2% (7.2 GB / 16 GB)\n',
                'error': '',
                'return_code': 0
            },
            'show me cpu usage': {
                'output': 'CPU Information\nCPU Cores: 8\nCurrent Frequency: 3187 MHz\nCPU Usage: 25.3%\n',
                'error': '',
                'return_code': 0
            },
            'ls': {
                'output': 'app/  main.py  README.md  requirements.txt  tests/  vercel.json\n',
                'error': '',
                'return_code': 0
            },
            'pwd': {
                'output': '/app\n',
                'error': '',
                'return_code': 0
            },
            'help': {
                'output': 'Available Commands:\n- ls: List files\n- cd: Change directory\n- pwd: Show current directory\n- mkdir: Create directory\n- Natural Language: "show me the files", "create a folder called test"\n',
                'error': '',
                'return_code': 0
            }
        }
        
        # Check for exact match first
        if command in responses:
            return jsonify(responses[command])
        
        # Check for partial matches (natural language)
        for key, response in responses.items():
            if command.lower() in key.lower() or key.lower() in command.lower():
                return jsonify(response)
        
        # Default response for unknown commands
        return jsonify({
            'output': f'Command not found: {command}\nType "help" for available commands.\n',
            'error': '',
            'return_code': 1
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/demo')
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
            'command': 'show me cpu usage',
            'description': 'Display CPU information',
            'traditional': 'cpu'
        },
        {
            'command': 'help',
            'description': 'Show available commands',
            'traditional': 'help'
        }
    ]
    
    return jsonify({'commands': demo_commands})

@app.route('/health')
def health_check():
    """Health check endpoint for Vercel"""
    return jsonify({'status': 'healthy', 'service': 'PyTerm API'})

# Vercel serverless function handler
def handler(request):
    return app(request.environ, lambda *args: None)
