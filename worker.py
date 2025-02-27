#!/usr/bin/env python3
"""
Ollama Runner Pool - Worker Client

This script runs on contributor machines to serve Ollama models to the pool.
"""

import argparse
import configparser
import json
import logging
import os
import requests
import subprocess
import sys
import time
from typing import Dict, List, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('ollama-worker')

class OllamaWorker:
    """Worker client for the Ollama Runner Pool."""

    def __init__(self, config_path: str):
        """Initialize the worker with the given configuration."""
        self.config = self._load_config(config_path)
        self.api_key = self.config.get('auth', 'api_key')
        self.pool_api_url = self.config.get('pool', 'api_url')
        self.worker_name = self.config.get('worker', 'name')
        self.ollama_url = self.config.get('ollama', 'url', fallback='http://localhost:11434')
        self.heartbeat_interval = int(self.config.get('worker', 'heartbeat_interval', fallback='30'))
        self.poll_interval = int(self.config.get('worker', 'poll_interval', fallback='5'))
        self.worker_id = None
        self.available_models = []

    def _load_config(self, config_path: str) -> configparser.ConfigParser:
        """Load configuration from the specified file."""
        if not os.path.exists(config_path):
            logger.error(f"Configuration file not found: {config_path}")
            sys.exit(1)

        config = configparser.ConfigParser()
        config.read(config_path)
        return config

    def _get_headers(self) -> Dict[str, str]:
        """Get the HTTP headers for API requests."""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def discover_models(self) -> List[Dict[str, str]]:
        """Discover available Ollama models on this machine."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags")
            if response.status_code == 200:
                models_data = response.json().get('models', [])
                return [{'name': model['name']} for model in models_data]
            else:
                logger.error(f"Failed to get models from Ollama: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error discovering models: {e}")
            return []

    def register(self) -> bool:
        """Register this worker with the pool."""
        self.available_models = self.discover_models()
        if not self.available_models:
            logger.error("No models available. Make sure Ollama is running and has models.")
            return False

        try:
            payload = {
                'name': self.worker_name,
                'models': self.available_models
            }
            response = requests.post(
                f"{self.pool_api_url}/workers/register",
                headers=self._get_headers(),
                json=payload
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'data' in data:
                    self.worker_id = data['data'].get('worker_id')
                    logger.info(f"Worker registered successfully with ID: {self.worker_id}")
                    return True
                else:
                    logger.error(f"Invalid response format: {data}")
                    return False
            else:
                logger.error(f"Failed to register worker: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error registering worker: {e}")
            return False

    def send_heartbeat(self) -> bool:
        """Send a heartbeat to the pool to indicate this worker is still alive."""
        if not self.worker_id:
            logger.error("Worker not registered yet")
            return False

        try:
            payload = {
                'worker_id': self.worker_id,
                'status': 'online'
            }
            response = requests.post(
                f"{self.pool_api_url}/workers/heartbeat",
                headers=self._get_headers(),
                json=payload
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    logger.debug("Heartbeat sent successfully")
                    return True
                else:
                    logger.error(f"Invalid response format: {data}")
                    return False
            else:
                logger.error(f"Failed to send heartbeat: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error sending heartbeat: {e}")
            return False

    def get_pending_tasks(self) -> List[Dict]:
        """Get pending tasks assigned to this worker."""
        if not self.worker_id:
            logger.error("Worker not registered yet")
            return []

        try:
            response = requests.get(
                f"{self.pool_api_url}/workers/tasks",
                headers=self._get_headers(),
                params={'worker_id': self.worker_id}
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'data' in data and 'tasks' in data['data']:
                    tasks = data['data']['tasks']
                    if tasks:
                        logger.info(f"Received {len(tasks)} pending tasks")
                    return tasks
                else:
                    logger.error(f"Invalid response format: {data}")
                    return []
            else:
                logger.error(f"Failed to get tasks: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            logger.error(f"Error getting tasks: {e}")
            return []

    def process_task(self, task: Dict) -> bool:
        """Process a single task by calling Ollama."""
        task_id = task.get('id')
        model = task.get('model_name')
        prompt = task.get('prompt')

        logger.info(f"Processing task {task_id} with model {model}")

        try:
            # Call Ollama API
            payload = {
                'model': model,
                'prompt': prompt,
                'stream': False
            }
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload
            )

            if response.status_code == 200:
                result = response.json()
                # Submit the result back to the pool
                completion_payload = {
                    'worker_id': self.worker_id,
                    'response': result.get('response', ''),
                    'task_id': task_id
                }
                completion_response = requests.post(
                    f"{self.pool_api_url}/tasks/{task_id}/complete",
                    headers=self._get_headers(),
                    json=completion_payload
                )

                if completion_response.status_code == 200:
                    completion_data = completion_response.json()
                    if completion_data.get('success'):
                        logger.info(f"Task {task_id} completed successfully")
                        return True
                    else:
                        logger.error(f"Invalid response format: {completion_data}")
                        return False
                else:
                    logger.error(f"Failed to submit task result: {completion_response.status_code} - {completion_response.text}")
                    return False
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error processing task {task_id}: {e}")
            return False

    def run(self):
        """Main worker loop."""
        if not self.register():
            logger.error("Failed to register worker. Exiting.")
            return

        last_heartbeat = 0

        while True:
            # Send heartbeat if needed
            current_time = time.time()
            if current_time - last_heartbeat >= self.heartbeat_interval:
                logger.info("Sending heartbeat")
                if self.send_heartbeat():
                    last_heartbeat = current_time

            # Check for pending tasks
            logger.info("Getting pending tasks")
            tasks = self.get_pending_tasks()
            for task in tasks:
                self.process_task(task)

            # Sleep before next poll
            time.sleep(self.poll_interval)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Ollama Runner Pool Worker')
    parser.add_argument('--config', '-c', default='config.ini', help='Path to configuration file')
    args = parser.parse_args()

    worker = OllamaWorker(args.config)
    worker.run()

if __name__ == '__main__':
    main()
