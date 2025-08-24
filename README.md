# Template Creator
This tool allows you to create new project structures from predefined templates.

<img width="983" height="331" alt="image" src="https://github.com/user-attachments/assets/e26943a2-066b-44d4-be78-876d94f34038" />


## Setup

1.  Place the `template.bat` file in a directory that is included in your system's [PATH environment variable](https://www.eukhost.com/kb/how-to-add-to-the-path-on-windows-10-and-windows-11/).
2.  Customize and add your template folders into the `templates/` directory.
3.  Update the `config.json` file to register your templates.
4.  Use the `/docs/TemplateCreation.md` as context for creating new templates. Feed this to a language model to instruct them how the templates can be made.

## Usage

### CMD GUI
Run `template` in any directory and it will display a list of entries to select
<img width="975" height="243" alt="image" src="https://github.com/user-attachments/assets/821e6534-1730-4ac3-9f67-7bc47e037b10" />


### Direct Mode
You can also run the `template` command directly with one of your  defined shortcuts, and it will run the template creation process immediately

Example:

```
template venv
```

This would copy the venv_create.bat to the folder, and launch it, initializing a python virtual environment setup.
