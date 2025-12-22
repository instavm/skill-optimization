"""
Azure OpenAI Configuration for DSPy

This module sets up DSPy to work with Azure OpenAI instead of regular OpenAI.
"""

import os
from openai import AzureOpenAI
import dspy


def configure_azure_dspy(
    api_key: str,
    api_base: str,
    deployment_name: str,
    api_version: str = "2025-01-01-preview",
    max_tokens: int = 1500
):
    """
    Configure DSPy to use Azure OpenAI.

    Args:
        api_key: Azure OpenAI API key
        api_base: Azure OpenAI endpoint
        deployment_name: Model deployment name
        api_version: API version
        max_tokens: Max tokens for completion
    """

    # Create Azure OpenAI client
    client = AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=api_base
    )

    # Configure DSPy with Azure OpenAI
    # DSPy uses a wrapper for Azure OpenAI
    lm = dspy.AzureOpenAI(
        api_base=api_base,
        api_key=api_key,
        api_version=api_version,
        deployment_id=deployment_name,
        model=deployment_name,
        max_tokens=max_tokens
    )

    dspy.settings.configure(lm=lm)

    return lm


def load_azure_config_from_env():
    """
    Load Azure OpenAI configuration from environment variables.

    Returns:
        Dictionary with Azure OpenAI configuration
    """
    return {
        "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
        "api_base": os.getenv("AZURE_OPENAI_ENDPOINT"),
        "deployment_name": os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        "api_version": os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
    }


def setup_azure_openai():
    """
    Set up Azure OpenAI from environment variables.

    Returns:
        Configured DSPy language model or None if config missing
    """
    config = load_azure_config_from_env()

    if not all([config["api_key"], config["api_base"], config["deployment_name"]]):
        print("❌ Azure OpenAI configuration incomplete")
        print("   Required environment variables:")
        print("   - AZURE_OPENAI_API_KEY")
        print("   - AZURE_OPENAI_ENDPOINT")
        print("   - AZURE_OPENAI_DEPLOYMENT")
        return None

    print(f"✅ Configuring DSPy with Azure OpenAI")
    print(f"   Endpoint: {config['api_base']}")
    print(f"   Deployment: {config['deployment_name']}")
    print(f"   API Version: {config['api_version']}")

    lm = configure_azure_dspy(**config)

    return lm
