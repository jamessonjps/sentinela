import json
import os
from datetime import datetime

class CheckpointManager:
    """
    Manages checkpoints to keep track of the last processed timestamps for different tasks.
    """
    def __init__(self, checkpoint_file='delta_checkpoints.json'):
        self.checkpoint_file = checkpoint_file
        self.checkpoints = self._load_checkpoints()

    def _load_checkpoints(self):
        if os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def get_last_run(self, task_name):
        """
        Returns the ISO formatted timestamp of the last run for a given task.
        Returns None if the task has never been run.
        """
        return self.checkpoints.get(task_name)

    def update_checkpoint(self, task_name, timestamp=None):
        """
        Updates the checkpoint for a task. If timestamp is not provided, uses current time.
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        self.checkpoints[task_name] = timestamp
        self._save_checkpoints()

    def _save_checkpoints(self):
        with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(self.checkpoints, f, indent=4)
