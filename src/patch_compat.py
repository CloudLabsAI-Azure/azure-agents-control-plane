# Compatibility patch for agent-framework-azure-ai 1.0.0b260107
# with azure-ai-projects 2.0.0b4 (class names were renamed)
import azure.ai.projects.models as models

_aliases = {
    "PromptAgentDefinitionText": "PromptAgentDefinitionTextOptions",
    "ResponseTextFormatConfigurationJsonObject": "TextResponseFormatConfigurationResponseFormatJsonObject",
    "ResponseTextFormatConfigurationJsonSchema": "TextResponseFormatJsonSchema",
    "ResponseTextFormatConfigurationText": "TextResponseFormatConfigurationResponseFormatText",
}

# Write aliases into the module's __init__.py so they're available at import time
init_file = models.__file__
lines = []
for old_name, new_name in _aliases.items():
    if not hasattr(models, old_name) and hasattr(models, new_name):
        lines.append(f"{old_name} = {new_name}")

if lines:
    with open(init_file, "a") as f:
        f.write("\n# Compatibility aliases added by patch_compat.py\n")
        for line in lines:
            f.write(line + "\n")
    print(f"Patched {init_file} with {len(lines)} aliases")
else:
    print("No patching needed")
