# Data processing with insecure deserialization
import pickle
import yaml
import json

class UserSession:
    def __init__(self, user_id, role):
        self.user_id = user_id
        self.role = role

def load_session(session_cookie):
    """Load user session from cookie."""
    # Insecure deserialization
    session_data = pickle.loads(session_cookie)
    return session_data

def load_config(config_file):
    """Load configuration from YAML."""
    with open(config_file) as f:
        # Unsafe YAML loading
        config = yaml.load(f)
    return config

def process_user_data(data_string):
    """Process user-provided data."""
    # Using eval on user input
    result = eval(data_string)
    return result

def execute_template(template, context):
    """Execute template with user data."""
    # SSTI vulnerability
    from jinja2 import Template
    t = Template(template)
    return t.render(**context)
