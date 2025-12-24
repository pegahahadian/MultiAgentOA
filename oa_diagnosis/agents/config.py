import os

# Default configuration using OAI_CONFIG_LIST if available, or just gpt-4
# In a real scenario, you'd ensure the user has their keys set up.
config_list = [
    {
        "model": "gpt-3.5-turbo",
        "api_key": ""
    }
]

llm_config = {
    "config_list": config_list,
    "temperature": 0.2,
    "timeout": 120,
}
