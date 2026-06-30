import jinja2
import logging

logger = logging.getLogger(__name__)

class PromptManager:
    """
    Loads and renders Jinja2 prompt templates from the file system.
    """
    def __init__(self, prompts_dir: str = "app/prompts"):
        self.prompts_dir = prompts_dir
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.prompts_dir),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True
        )

    def render(self, template_name: str, context: dict) -> str:
        """
        Renders a specific prompt template with the provided context dictionary.
        """
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except jinja2.TemplateNotFound:
            logger.error(f"Prompt template '{template_name}' not found in {self.prompts_dir}.")
            raise ValueError(f"Prompt template '{template_name}' not found.")
        except Exception as e:
            logger.error(f"Error rendering prompt template '{template_name}': {e}")
            raise
