#!/usr/bin/env python3
"""
ORunner Pool - CLI Entry Point
"""

import sys
import argparse
from orunnerpool.worker import main as worker_main

def cli_main():
    """CLI entry point for the orunnerpool package."""
    parser = argparse.ArgumentParser(description='ORunner Pool Worker')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Start command (default)
    start_parser = subparsers.add_parser('start', help='Start the worker')
    start_parser.add_argument('--config', '-c', help='Path to configuration file')
    start_parser.add_argument('--openrouter', action='store_true', help='Run in OpenRouter proxy mode')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Run interactive setup')
    
    # Version command
    version_parser = subparsers.add_parser('version', help='Show version information')
    
    args = parser.parse_args()
    
    if args.command == 'setup':
        try:
            from orunnerpool.setup import interactive_setup
            interactive_setup()
        except ImportError:
            print("Setup module not found. Please install the package correctly.")
            sys.exit(1)
    elif args.command == 'version':
        from orunnerpool import __version__
        print(f"ORunner Pool Worker v{__version__}")
    else:  # start or no command
        # Pass any arguments to the worker main function
        sys.argv = [sys.argv[0]]  # Reset argv
        if args.command == 'start':
            if args.config:
                sys.argv.extend(['--config', args.config])
            if args.openrouter:
                sys.argv.append('--openrouter')
        worker_main()

if __name__ == "__main__":
    cli_main() 