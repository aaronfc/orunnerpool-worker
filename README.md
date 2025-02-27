# ORunner Pool - Worker Client

> [!WARNING]
> This project is in a very early status. Consider it a _working✨_ proof of concept.

This is the worker component of the [ORunner Pool project](https://orunnerpool.com). It runs on contributor machines to serve Ollama models to the pool.

## Prerequisites

- Python 3.10 or higher
- [Ollama](https://github.com/ollama/ollama) installed and running on your machine
- At least one model loaded in Ollama
- An account on the Ollama Runner Pool with an API key (https://orunnerpool.com/index.php?page=register)

## Installation

1. Clone the repository or download the worker files:
   ```bash
   git clone https://github.com/aaronfc/orunnerpool-worker.git
   cd orunnerpool-worker
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create your configuration file:
   ```bash
   cp config.ini.example config.ini
   ```

4. Edit the `config.ini` file with your settings:
   ```ini
   [auth]
   # Your API key from the Ollama Runner Pool web interface
   api_key = your_api_key_here

   [pool]
   # URL of the pool API
   # If using Docker Compose for development, use http://localhost:8000
   # For production, use https://api.orunnerpool.com
   api_url = https://api.orunnerpool.com

   [worker]
   # Name of this worker (shown in the web interface)
   name = My Ollama Worker
   # Heartbeat interval in seconds
   heartbeat_interval = 30
   # Task polling interval in seconds
   poll_interval = 5

   [ollama]
   # URL of your local Ollama instance
   url = http://localhost:11434
   ```

## Usage

1. Make sure Ollama is running on your machine:
   ```bash
   ollama serve
   ```

2. Start the worker:
   ```bash
   python worker.py
   ```

   Or specify a custom config file location:
   ```bash
   python worker.py --config /path/to/your/config.ini
   ```

3. The worker will automatically:
   - Discover available models on your Ollama instance
   - Register with the pool
   - Send regular heartbeats
   - Poll for tasks and process them

## Logs

The worker logs to stdout by default. You can redirect the output to a file:

```bash
python worker.py > worker.log 2>&1
```

## Running as a Service

> [!WARNING]
> These steps are not tested yet.

### Systemd (Linux)

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/ollama-worker.service
```

Add the following content:

```
[Unit]
Description=Ollama Runner Pool Worker
After=network.target

[Service]
User=yourusername
WorkingDirectory=/path/to/worker
ExecStart=/usr/bin/python3 /path/to/worker/worker.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable ollama-worker
sudo systemctl start ollama-worker
```

### Launchd (macOS)

Create a plist file:

```bash
nano ~/Library/LaunchAgents/com.ollama.worker.plist
```

Add the following content:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.ollama.worker</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/worker/worker.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>WorkingDirectory</key>
    <string>/path/to/worker</string>
    <key>StandardOutPath</key>
    <string>/path/to/worker/worker.log</string>
    <key>StandardErrorPath</key>
    <string>/path/to/worker/worker.log</string>
</dict>
</plist>
```

Load the service:

```bash
launchctl load ~/Library/LaunchAgents/com.ollama.worker.plist
```

## Troubleshooting

### Worker fails to register

- Make sure Ollama is running and has at least one model loaded
- Check that your API key is correct
- Verify the pool API URL is accessible

### Worker can't connect to Ollama

- Ensure Ollama is running (`ollama serve`)
- Check the Ollama URL in your config file
- Verify there are no firewall rules blocking access to port 11434

### Worker doesn't receive tasks

- Check that your worker is registered successfully
- Verify that your models are correctly listed in the pool
- Make sure your worker's heartbeat is being received by the pool

## Releasing

- Build with `python -m build`.
- Publish to PyPI `twine upload dist/*`.


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 