"""Prompt definition models for GRIMOIRE runner."""

from dataclasses import dataclass


@dataclass
class LLMConfig:
    """LLM configuration for prompt execution."""

    provider: str | None = None
    model: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    system_prompt: str | None = None

    def validate(self) -> list[str]:
        """Validate the LLM configuration and return any errors."""
        errors = []

        # Temperature should be between 0 and 1 if specified
        if self.temperature is not None:
            if not 0.0 <= self.temperature <= 1.0:
                errors.append(
                    f"Temperature must be between 0.0 and 1.0, got {self.temperature}"
                )

        # Max tokens should be positive if specified
        if self.max_tokens is not None:
            if self.max_tokens <= 0:
                errors.append(f"Max tokens must be positive, got {self.max_tokens}")

        return errors


@dataclass
class PromptDefinition:
    """Prompt template definition for LLM content generation."""

    kind: str
    name: str
    prompt_template: str
    id: str | None = None
    description: str | None = None
    version: str = "1.0"
    llm: LLMConfig | None = None

    def __post_init__(self):
        """Initialize LLM config from dict if necessary."""
        if isinstance(self.llm, dict):
            self.llm = LLMConfig(**self.llm)

    def validate(self) -> list[str]:
        """Validate the prompt definition and return any errors."""
        errors = []

        # Validate required fields
        if self.kind != "prompt":
            errors.append(f"Prompt kind must be 'prompt', got '{self.kind}'")
        if not self.name:
            errors.append("Prompt name is required")
        if not self.prompt_template:
            errors.append("Prompt template is required")

        # Validate LLM config if present
        if self.llm:
            errors.extend(self.llm.validate())

        return errors
