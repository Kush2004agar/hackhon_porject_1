import json

def handler(request):
    """Vercel serverless function handler for PyTerm API"""
    
    # Get the request method and path
    method = request.get('REQUEST_METHOD', 'GET')
    path = request.get('PATH_INFO', '/')
    
    # Handle CORS preflight
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'message': 'CORS preflight'})
        }
    
    # Handle POST requests to /command
    if method == 'POST' and path == '/command':
        try:
            # Parse request body
            body = request.get('body', '{}')
            if isinstance(body, str):
                data = json.loads(body)
            else:
                data = body
            
            command = data.get('command', '')
            
            if not command:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Content-Type': 'application/json'
                    },
                    'body': json.dumps({'error': 'No command provided'})
                }
            
            # Simulate PyTerm responses
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
                response_data = responses[command]
            else:
                # Check for partial matches (natural language)
                response_data = None
                for key, response in responses.items():
                    if command.lower() in key.lower() or key.lower() in command.lower():
                        response_data = response
                        break
                
                if not response_data:
                    response_data = {
                        'output': f'Command not found: {command}\nType "help" for available commands.\n',
                        'error': '',
                        'return_code': 1
                    }
            
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps(response_data)
            }
            
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'error': str(e)})
            }
    
    # Handle GET requests to /demo
    elif method == 'GET' and path == '/demo':
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
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'commands': demo_commands})
        }
    
    # Handle GET requests to /health
    elif method == 'GET' and path == '/health':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'status': 'healthy', 'service': 'PyTerm API'})
        }
    
    # Default response
    else:
        return {
            'statusCode': 404,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': 'Not found'})
        }