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

Install the worker using pipx:

```bash
pipx install orunnerpool
```

To upgrade to the latest version:

```bash
pipx upgrade orunnerpool
```

## Configuration

The worker uses a configuration file located at:
- `~/.config/orunnerpool/config.ini` (user-specific configuration)
- `/etc/orunnerpool/config.ini` (system-wide configuration)

When you run the worker for the first time, an interactive setup will guide you through creating your configuration file. You'll need your API key from the ORunner Pool website.

### OpenRouter (Experimental)

> [!WARNING]
> This is an experimental feature to workaround the fact that at the moment there are very few workers running.

To use the worker in OpenRouter proxy mode, add the following section to your config.ini file:

```ini
[openrouter]
# Comma-separated list of supported models
models = google/gemini-2.0-pro-exp-02-05:free
```

You can specify multiple models by separating them with commas.

You will need to setup the `OPENROUTER_API_KEY` environment variable:
```bash
export OPENROUTER_API_KEY=your_openrouter_api_key
```

Then run `orunnerpool --openrouter`.

## Usage

1. Make sure Ollama is running on your machine:
   ```bash
   ollama serve
   ```

2. Start the worker:
   ```bash
   orunnerpool
   ```

3. The worker will automatically:
   - Discover available models on your Ollama instance
   - Register with the pool
   - Send regular heartbeats
   - Poll for tasks and process them

## Logs

The worker logs to stdout by default. You can redirect the output to a file:

```bash
orunnerpool > worker.log 2>&1
```

## Running as a Service

> [!WARNING]
> These steps are not tested yet.

### Systemd (Linux)

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/orunnerpool.service
```

Add the following content:

```
[Unit]
Description=ORunner Pool Worker
After=network.target

[Service]
User=yourusername
ExecStart=/usr/bin/orunnerpool
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable orunnerpool
sudo systemctl start orunnerpool
```

### Launchd (macOS)

Create a plist file:

```bash
nano ~/Library/LaunchAgents/com.orunnerpool.worker.plist
```

Add the following content:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.orunnerpool.worker</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/orunnerpool</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>~/Library/Logs/orunnerpool.log</string>
    <key>StandardErrorPath</key>
    <string>~/Library/Logs/orunnerpool.log</string>
</dict>
</plist>
```

Load the service:

```bash
launchctl load ~/Library/LaunchAgents/com.orunnerpool.worker.plist
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

You can use the provided release script to automate the version update, build, and upload process:

```bash
python -m build
twine upload --skip-existing dist/*
```

The script will:
1. Update the version in both pyproject.toml and orunnerpool/__init__.py based on semantic versioning
2. Build the package
3. Prompt you to upload to PyPI

Alternatively, you can manually:
- Build with `python -m build`
- Publish to PyPI with `twine upload dist/*`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 