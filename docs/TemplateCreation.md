# How to Create and Add New Templates

This document provides instructions for developers and LLMs on how to add new templates to the Template Creator tool.

## Introduction

The tool is driven by two key components:
1.  **The `/templates` directory:** This folder contains the raw source files and folders for each template.
2.  **The `config.json` file:** This file acts as a registry, telling the script what templates are available and how they should behave. For most templates, editing this file provides more advanced customization.

---

## The Simplest Method: Auto-Detection

For simple templates that only need to copy a folder structure, you **do not** need to edit `config.json`.

1.  **Create a folder** inside the `/templates` directory (e.g., `/templates/my_new_template`).
2.  **Add your files** and folders inside it.

That's it. The next time you run the tool, `my_new_template` will automatically appear in the list, colored yellow. It will be selectable by its folder name.

This is the recommended method for creating simple, copy-only templates.

---

## Advanced Configuration via `config.json`

To add shortcuts, colors, descriptions, or special post-creation actions, you need to add an entry for your template to `config.json`.

### Step 1: Create the Template Source

This is the same as the simple method. Create a folder in the `/templates` directory.

### Step 2: Register and Customize in `config.json`

Open the `config.json` file and add a new JSON object to the list. Here are all the available keys:

- `name` (string, required): The full, user-friendly name of the template.
- `shortcuts` (list of strings, required): A list of short aliases.
- `path` (string, required): The name of the template folder in `/templates` or the direct path to a single file (e.g., `my_template` or `venv/script.bat`).
- `description` (string, optional): A brief explanation of what the template does.
- `color` (string, optional): The color for the template in the list. Available options: `"teal"`, `"green"`, `"purple"`.
- `copy_mode` (string, optional): How to copy. Defaults to `directory_contents`.
    - `directory_contents`: Copies the entire contents of the folder in `path`.
    - `single_file`: Copies only the single file specified in `path`.
- `post_action` (string, optional): A special function to run *after* copying. Must match a key in `src/main.py`.
- `action_args` (object, optional): Specific arguments needed by the `post_action` function.

## Configuration Examples

### Example 1: Simple Template with Customization

This template just copies a folder, but we want to add a description, shortcuts, and a color.

**Source:** `/templates/merging/...`

**Config:**
```json
{
  "name": "Merging Template",
  "shortcuts": ["merging", "merge", "mrg"],
  "description": "Copies merging template files into the current folder.",
  "path": "merging",
  "color": "purple"
}
```

### Example 2: Template with a Post-Action Script

This template copies a single file and then executes it.

**Source:** `/templates/venv/venv_create.bat`

**Config:**
```json
{
  "name": "Python Virtual Environment",
  "shortcuts": ["venv", "v"],
  "description": "Copies the venv creation script and runs it.",
  "path": "venv/venv_create.bat",
  "copy_mode": "single_file",
  "post_action": "run_script",
  "color": "teal",
  "action_args": {
    "script_name": "venv_create.bat"
  }
}
```

### Example 3: Complex Template with Renaming

This template copies a directory and then performs multiple, nested renames based on user input.

**Source:** `/templates/code/Project/Project/...`

**Config:**
```json
{
  "name": "Python Code",
  "shortcuts": ["code", "c"],
  "description": "Creates a project structure and renames nested project folders.",
  "path": "code",
  "post_action": "rename_folder",
  "color": "teal",
  "action_args": {
    "targets_to_rename": ["Project", "Project/Project"]
  }
}
```

## For Developers: Adding New Post-Actions

To create a new type of post-action:
1.  Open `src/main.py`.
2.  Create a new function that accepts `(template_config, dest_dir)` as arguments (e.g., `handle_my_new_action`).
3.  Add your function to the `POST_ACTIONS` dictionary at the top of the script, mapping a string name to your function.
    ```python
    POST_ACTIONS = {
        "rename_folder": handle_rename_folder,
        "run_script": handle_run_script,
        "my_new_action": handle_my_new_action
    }
    ```
4.  You can now use `"post_action": "my_new_action"` in `config.json`.