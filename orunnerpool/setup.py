#!/usr/bin/env python3
"""
ORunner Pool - Interactive Setup

This module provides interactive setup functionality for first-time users.
"""

import configparser
import os
import sys
import getpass
import socket
from pathlib import Path
import logging

logger = logging.getLogger('orunnerpool-setup')

DEFAULT_CONFIG = {
    'auth': {
        'api_key': ''
    },
    'pool': {
        'api_url': 'https://orunnerpool.com/api'
    },
    'worker': {
        'name': socket.gethostname(),
        'heartbeat_interval': '30',
        'poll_interval': '5'
    },
    'ollama': {
        'url': 'http://localhost:11434'
    }
}

CONFIG_PATHS = [
    os.path.expanduser('~/.config/orunnerpool/config.ini'),  # User config directory
    '/etc/orunnerpool/config.ini',  # System config directory
]

def get_config_path():
    """Get the path to use for the configuration file."""
    # First check if any existing config files exist
    for path in CONFIG_PATHS:
        if os.path.exists(path):
            return path
    
    # If no config exists, use the user config directory
    user_config_dir = os.path.expanduser('~/.config/orunnerpool')
    if not os.path.exists(user_config_dir):
        try:
            os.makedirs(user_config_dir)
        except OSError as e:
            logger.error(f"Error creating directory {user_config_dir}: {e}")
            raise
    
    return os.path.join(user_config_dir, 'config.ini')

def interactive_setup():
    """Run the interactive setup to create a configuration file."""
    print("\n" + "="*60)
    print("Welcome to ORunner Pool Worker Setup")
    print("="*60)
    print("\nThis wizard will help you set up your worker configuration.")
    print("You'll need an API key from https://orunnerpool.com to continue.")
    print("\nIf you don't have an API key yet, please visit:")
    print("https://orunnerpool.com/index.php?page=register")
    print("\nDefault values are shown in [brackets].")
    print("Press Enter to accept the default value.")
    
    config = configparser.ConfigParser()
    
    # Load default configuration
    for section, options in DEFAULT_CONFIG.items():
        if not config.has_section(section):
            config.add_section(section)
        for option, value in options.items():
            config.set(section, option, value)
    
    # Get API key
    api_key = ''
    while not api_key:
        api_key = input("\nEnter your API key from orunnerpool.com: ")
        if not api_key:
            print("API key is required to connect to the pool.")
    
    config.set('auth', 'api_key', api_key)
    
    # Worker name
    default_name = config.get('worker', 'name')
    worker_name = input(f"\nEnter a name for this worker [{default_name}]: ")
    if worker_name:
        config.set('worker', 'name', worker_name)
    
    # Ollama URL
    default_ollama_url = config.get('ollama', 'url')
    ollama_url = input(f"\nEnter the Ollama API URL [{default_ollama_url}]: ")
    if ollama_url:
        config.set('ollama', 'url', ollama_url)
    
    # Pool API URL
    default_pool_url = config.get('pool', 'api_url')
    pool_url = input(f"\nEnter the Pool API URL [{default_pool_url}]: ")
    if pool_url:
        config.set('pool', 'api_url', pool_url)
    
    # Advanced settings
    advanced = input("\nWould you like to configure advanced settings? (y/N): ").lower()
    if advanced == 'y':
        # Heartbeat interval
        default_heartbeat = config.get('worker', 'heartbeat_interval')
        heartbeat = input(f"\nEnter heartbeat interval in seconds [{default_heartbeat}]: ")
        if heartbeat:
            config.set('worker', 'heartbeat_interval', heartbeat)
        
        # Poll interval
        default_poll = config.get('worker', 'poll_interval')
        poll = input(f"\nEnter poll interval in seconds [{default_poll}]: ")
        if poll:
            config.set('worker', 'poll_interval', poll)
    
    # Save configuration
    config_path = get_config_path()
    
    # Ensure directory exists
    config_dir = os.path.dirname(config_path)
    if config_dir and not os.path.exists(config_dir):
        try:
            os.makedirs(config_dir)
        except OSError as e:
            print(f"Error creating directory {config_dir}: {e}")
            raise
    
    try:
        with open(config_path, 'w') as f:
            config.write(f)
        print(f"\nConfiguration saved to {config_path}")
        print("\nYou can now run 'orunnerpool' to start the worker.")
        return config_path
    except Exception as e:
        print(f"Error saving configuration: {e}")
        return None

def check_config_exists():
    """Check if a configuration file exists."""
    for path in CONFIG_PATHS:
        if os.path.exists(path):
            return path
    return None

if __name__ == "__main__":
    interactive_setup() 