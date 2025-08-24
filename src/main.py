# main.py
# Core script for the Template Creator tool.

import sys
import os
import json
import shutil
import subprocess

# --- CONFIGURATION ---
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
CONFIG_PATH = os.path.join(BASE_DIR, 'config.json')
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

# --- SPECIAL FUNCTION HANDLERS ---

def handle_rename_folder(template_config, dest_dir):
    """Handles the 'rename_folder' post-action for one or more targets."""
    try:
        targets = template_config['action_args']['targets_to_rename']
        if not isinstance(targets, list):
            print("Action error: 'targets_to_rename' must be a list in config.json.")
            return

        print(f"\nThe '{template_config['name']}' template requires a project name.")
        new_name = input("Please enter the new project name: ")

        if not new_name.strip():
            print("Invalid name. Skipping rename.")
            return

        rename_map = {}
        for target in targets:
            for old, new in rename_map.items():
                target = target.replace(old, new, 1)
            
            original_path = os.path.join(dest_dir, target)
            if not os.path.exists(original_path):
                print(f"Warning: Expected folder '{target}' not found for renaming.")
                continue

            new_path = os.path.join(os.path.dirname(original_path), new_name)
            if os.path.exists(new_path):
                print(f"Error: A folder named '{new_name}' already exists. Skipping rename of '{target}'.")
                continue

            os.rename(original_path, new_path)
            print(f"Successfully renamed '{os.path.basename(target)}' to '{new_name}'.")
            
            base_target = target.split(os.path.sep)[0]
            if base_target not in rename_map:
                rename_map[base_target] = new_name

    except KeyError:
        print("Action error: 'action_args' for 'rename_folder' are misconfigured.")
    except Exception as e:
        print(f"An error occurred during renaming: {e}")

def handle_run_script(template_config, dest_dir):
    """Handles the 'run_script' post-action."""
    try:
        script_name = template_config['action_args']['script_name']
        script_path = os.path.join(dest_dir, script_name)

        if not os.path.exists(script_path):
            print(f"\nWarning: Expected script '{script_name}' not found.")
            return

        print(f"\nExecuting setup script: {script_name}...")
        subprocess.run([script_path], shell=True, check=True, cwd=dest_dir)
        print(f"Script '{script_name}' executed successfully.")

    except KeyError:
        print("Action error: 'action_args' for 'run_script' are misconfigured.")
    except Exception as e:
        print(f"An error occurred while running the script: {e}")

POST_ACTIONS = {
    "rename_folder": handle_rename_folder,
    "run_script": handle_run_script,
}

# --- CORE APPLICATION LOGIC ---

def load_config():
    """Loads the template configurations from config.json."""
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading or parsing config.json: {e}")
        return []

def discover_unconfigured_templates(configured_templates):
    """Finds templates in the directory that are not in the config file."""
    unconfigured = []
    configured_paths = {p.replace('\\', '/') for p in (t['path'] for t in configured_templates)}
    try:
        for item in os.listdir(TEMPLATES_DIR):
            item_path = os.path.join(TEMPLATES_DIR, item)
            if not os.path.isdir(item_path):
                continue

            is_handled = False
            if item in configured_paths:
                is_handled = True
            
            if not is_handled:
                dir_prefix = item + '/'
                for conf_path in configured_paths:
                    if conf_path.startswith(dir_prefix):
                        is_handled = True
                        break
            
            if not is_handled:
                unconfigured.append({
                    "name": item,
                    "shortcuts": [],
                    "path": item,
                    "is_unconfigured": True
                })
    except FileNotFoundError:
        pass
    return unconfigured

def display_templates(templates):
    """Displays a formatted list of available templates with color."""
    COLORS = {
        "teal": '\033[96m',
        "green": '\033[92m',
        "purple": '\033[95m',
        "yellow": '\033[93m',
        "default": '\033[0m'
    }
    width = 80
    print("+" + "-" * (width - 2) + "+")
    title = "Available Templates"
    print("|" + title.center(width - 2) + "|")
    print("+" + "-" * (width - 2) + "+")

    for i, t in enumerate(templates, 1):
        color_code = COLORS['default']
        if t.get('is_unconfigured'):
            content = f" [{i}] {t.get('name')} (Configure template in config.json)"
            color_code = COLORS['yellow']
        else:
            shortcuts = ", ".join(t.get('shortcuts', []))
            content = f" [{i}] {t.get('name', 'No Name')} ({shortcuts})"
            color_code = COLORS.get(t.get('color'), COLORS['default'])

        padded_content = content.ljust(width - 2)
        line = f"|{padded_content}|"
        print(color_code + line + COLORS['default'])

    print("+" + "-" * (width - 2) + "+")
    print("Select a template by number, name, or shortcut.")

def get_template_from_input(user_input, templates):
    """Finds a template based on user input."""
    user_input = user_input.lower().strip()
    if user_input.isdigit():
        try:
            index = int(user_input) - 1
            if 0 <= index < len(templates):
                return templates[index]
        except IndexError:
            return None
    for t in templates:
        if t['name'].lower() == user_input or user_input in [s.lower() for s in t['shortcuts']]:
            return t
    return None

def copy_dispatcher(template_config, dest_dir):
    """Dispatches to the correct copy function based on copy_mode."""
    copy_mode = template_config.get('copy_mode', 'directory_contents')
    source_path = os.path.join(TEMPLATES_DIR, template_config['path'])

    if not os.path.exists(source_path):
        print(f"Error: Template source path does not exist: {source_path}")
        return False

    try:
        if copy_mode == 'single_file':
            shutil.copy2(source_path, dest_dir)
            print(f"Successfully copied template file to '{dest_dir}'.")
        elif copy_mode == 'directory_contents':
            shutil.copytree(source_path, dest_dir, dirs_exist_ok=True)
            print(f"Successfully copied template contents to '{dest_dir}'.")
        else:
            print(f"Error: Unknown copy_mode '{copy_mode}'.")
            return False
        return True
    except Exception as e:
        print(f"Error copying template files: {e}")
        return False

def main():
    """Main function to run the template creator."""
    # This enables ANSI escape code support on Windows.
    os.system('')

    templates = load_config()
    unconfigured = discover_unconfigured_templates(templates)
    unconfigured.sort(key=lambda t: t['name'])
    all_templates = templates + unconfigured

    if not all_templates:
        print("No templates found. Add folders to the 'templates' directory.")
        return

    chosen_template = None
    args = sys.argv[1:]

    if args:
        choice = args[0]
        chosen_template = get_template_from_input(choice, all_templates)
        if not chosen_template:
            print(f"Template '{choice}' not found.")
            display_templates(all_templates)
            return
    else:
        display_templates(all_templates)
        try:
            choice = input("> ")
            chosen_template = get_template_from_input(choice, all_templates)
            if not chosen_template:
                print(f"Invalid selection. Please try again.")
                return
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled.")
            return

    destination = os.getcwd()
    print(f"\nCreating template '{chosen_template['name']}' in current directory...")

    if not copy_dispatcher(chosen_template, destination):
        return

    post_action_name = chosen_template.get('post_action')
    if post_action_name in POST_ACTIONS:
        action_function = POST_ACTIONS[post_action_name]
        action_function(chosen_template, destination)
    
    print("\nDone.")

if __name__ == "__main__":
    main()
