import json
import os
from html_processor.utils.logger import log_info

def load_config(config_path):
    log_info(f"Loading configuration from: {config_path}")
    with open(config_path, 'r') as file:
        config = json.load(file)

    required_keys = ['input_dir', 'output_dir', 'overwrite_output']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config key: {key}")

    config.setdefault('generate_report_plot', False)
    if 'analysis_options' in config and not isinstance(config['analysis_options'], dict):
        raise ValueError("analysis_options must be a dictionary")

    return config