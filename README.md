# silexexplorerpy

A Python project created with pyscaf

## uv Integration

This project uses uv for dependency management and packaging. uv provides a modern and extremely fast way to manage Python dependencies and build packages.

### Features

- **Dependency Management**: uv manages project dependencies through `pyproject.toml`
- **Virtual Environment**: Automatically creates and manages a virtual environment
- **Build System**: Integrated build system for creating Python packages
- **Lock File**: Generates a `uv.lock` file for reproducible installations

### Common Commands

```bash
# Install dependencies
uv sync

# Add a new dependency
uv add package-name

# Add a development dependency
uv add --dev package-name

# Update dependencies
uv sync --upgrade

# Run a command within the virtual environment
uv run python script.py

# Activate the virtual environment
uv run shell
```

### Project Structure

The project follows a standard Python package structure:
- `pyproject.toml`: Project configuration and dependencies
- `uv.lock`: Locked dependencies for reproducible builds
- `src/`: Source code directory
- `tests/`: Test files directory

### Development

To start developing:
1. Ensure uv is installed
2. Run `uv sync` to install all dependencies
3. Use `uv run` to execute scripts in the environment
4. Start coding!

For more information, visit [uv's official documentation](https://docs.astral.sh/uv/).

## Ruff Integration

Ruff is an extremely fast Python linter and code formatter, written in Rust. It can replace Flake8, Black, isort, pyupgrade, and more, while being much faster than any individual tool.

### VSCode Default Configuration

The file `.vscode/default_settings.json` provides a recommended configuration for using Ruff in VSCode:

```json
{
    "[python]": {
      "editor.formatOnSave": true,
      "editor.codeActionsOnSave": {
        "source.fixAll": "explicit",
        "source.organizeImports": "explicit"
      },
      "editor.defaultFormatter": "charliermarsh.ruff"
    },
    "notebook.formatOnSave.enabled": true,
    "notebook.codeActionsOnSave": {
      "notebook.source.fixAll": "explicit",
      "notebook.source.organizeImports": "explicit"
    },
    "ruff.lineLength": 88
}
```

#### Explanation of each line:
- `editor.formatOnSave`: Enables automatic formatting on save for all files.
- `[python].editor.defaultFormatter`: Sets Ruff as the default formatter for Python files.
- `[python]editor.codeActionsOnSave.source.organizeImports`: Organizes Python imports automatically on save.
- `[python]editor.codeActionsOnSave.source.fixAll`: Applies all available code fixes (including linting) on save.
- `ruff.lineLength`: Line length for your python files

### Useful Ruff Commands

You can run the following commands commands directly in the shell

```bash
# Lint all Python files in the current directory
ruff check .

# Format all Python files in the current directory
ruff format .

# Automatically fix all auto-fixable problems
ruff check . --fix
```

For more information, see the [official Ruff VSCode extension documentation](https://github.com/astral-sh/ruff-vscode) and the [Ruff documentation](https://docs.astral.sh/ruff/). 

You can enable specific rules over a catalog of over 800+ rules, depending on your needs or framework of choice. Check it out at the [Ruff documentation](docs.astral.sh/ruff/rules/). 

## Documentation

This action uses [pdoc](https://pdoc.dev/) to generate and serve documentation for your Python project.

### Configuration

The documentation configuration is managed in your `pyproject.toml` file:

```toml
[tool.pyscaf.documentation]
output_path = "docs"

[tool.pyscaf.documentation.pdoc]
# pdoc arguments are automatically converted to CLI arguments
# Boolean values: true -> --flag, false -> --no-flag
# Lists: ["value1", "value2"] -> --flag value1 --flag value2
# Strings: "value" -> --flag value
```

### Scripts

Two scripts are available to manage documentation. Both scripts use the configuration defined in the `[tool.pyscaf.documentation.pdoc]`:

#### `gen-doc`

Generates static documentation files to the directory specified in `tool.pyscaf.documentation.output_path`.

```bash
uv run gen-doc
```

#### `serve-doc`

Starts a local documentation server for interactive browsing.

```bash
uv run serve-doc
```

### pdoc Arguments

All arguments in the `[tool.pyscaf.documentation.pdoc]` section are automatically converted to pdoc CLI arguments:

- Boolean values: `true` becomes `--flag`, `false` becomes `--no-flag`
- Lists: `["value1", "value2"]` becomes `--flag value1 --flag value2`
- Strings: `"value"` becomes `--flag value`

`output` argument is droped, as the behaviour to write instead of serve depends on the script use.

For example:
```toml
[tool.pyscaf.documentation.pdoc]
html = true
show_source = false
template_directory = "custom_templates"
external_links = ["https://example.com"]
```

Becomes:
```bash
pdoc --html --no-show-source --template-directory custom_templates --external-links https://example.com
``` 
## Git Integration

This project uses Git for version control, providing a robust system for tracking changes, collaborating, and managing code history.

### Features

- **Version Control**: Track changes and manage code history
- **Branching**: Create and manage feature branches
- **Collaboration**: Work with remote repositories
- **Git Hooks**: Automated scripts for repository events

### Common Commands

```bash
# Initialize repository
git init

# Clone repository
git clone <repository-url>

# Create and switch to new branch
git checkout -b feature-name

# Stage changes
git add .

# Commit changes
git commit -m "commit message"

# Push changes
git push origin branch-name

# Pull latest changes
git pull origin branch-name
```

### Project Structure

The project includes:
- `.git/`: Git repository data
- `.gitignore`: Specifies intentionally untracked files
- `.gitattributes`: Defines attributes for paths
- `hooks/`: Custom Git hooks (if present)

### Development Workflow

1. Create a new branch for features/fixes
2. Make changes and commit regularly
3. Push changes to remote repository
4. Create pull requests for code review
5. Merge approved changes to main branch

### Best Practices

- Write clear commit messages
- Keep commits focused and atomic
- Use meaningful branch names
- Regularly pull from main branch
- Review changes before committing

For more information, visit [Git's official documentation](https://git-scm.com/doc). 
## Semantic Release Configuration

This action configures [python-semantic-release](https://python-semantic-release.readthedocs.io/) for automated versioning, changelog generation, and package publishing.

### Overview

Semantic release automates the process of:
- **Version management**: Automatically bump version numbers based on commit messages
- **Changelog generation**: Create detailed changelogs from conventional commits
- **Package publishing**: Deploy to PyPI (TestPyPI automatically, Production PyPI manually)
- **GitHub releases**: Create GitHub releases with assets

### Prerequisites

- Git repository with versioning enabled
- GitHub repository (for workflows)
- Credential for the publisher repository
- PyPI credentials configured as GitHub secrets:
  - `TEST_PYPI_PASSWORD` for TestPyPI
  - `PYPI_PASSWORD` for Production PyPI

#### PyPI Token Setup

1. **TestPyPI** (https://test.pypi.org):
   - Go to Account Settings → API tokens
   - Create a new token with "Entire account" scope
   - Copy the token value

2. **Production PyPI** (https://pypi.org):
   - Go to Account Settings → API tokens
   - Create a new token with "Entire account" scope
   - Copy the token value

3. **Add to GitHub Secrets**:
   - Go to your repository → Settings → Secrets and variables → Actions
   - Add `TEST_PYPI_PASSWORD` with your TestPyPI token
   - Add `PYPI_PASSWORD` with your production PyPI token

### Features

#### Automatic Configuration
Configures `pyproject.toml` with some default semantic-release settings


#### GitHub Workflows (when git_host is "github")
- **Release workflow**: Automatically triggers on pushes to main branch
- **Manual deploy workflow**: Allows manual deployment to production PyPI

#### Commit Convention
Uses [Conventional Commits](https://www.conventionalcommits.org/) format:
- `feat:` - New features (minor version bump)
- `fix:` - Bug fixes (patch version bump)
- `BREAKING CHANGE:` - Breaking changes (major version bump)
- `docs:`, `style:`, `refactor:`, `test:`, `chore:` - No version bump



### Configuration

The action automatically configures:
```toml
[tool.semantic_release]
version_variables = ["src/your_project/__init__.py:__version__"]
upload_to_pypi = true
upload_to_release = true
branch = "main"

[tool.semantic_release.remote]
type = "github"  # or "gitlab"
```

### Usage

1. **Automatic releases**: Push conventional commits to main branch
2. **Manual deployment**: Use GitHub Actions "Manual Deploy to Production PyPI" workflow

### Resources

#### Official Documentation
- [python-semantic-release Documentation](https://python-semantic-release.readthedocs.io/)
- [Conventional Commits Specification](https://www.conventionalcommits.org/)

#### Related Tools
- [Commitizen](https://commitizen-tools.github.io/commitizen/) - Interactive commit creation
- [Semantic Release CLI](https://github.com/semantic-release/semantic-release) - JavaScript version
- [GitHub Actions for Python](https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python)

#### Best Practices
- [Keep a Changelog](https://keepachangelog.com/) - Changelog format guidelines
- [Semantic Versioning](https://semver.org/) - Version numbering specification
- [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/) - Git branching strategy

### Example Workflow

```bash
# Make changes
git add .
git commit -m "feat: add new feature"
git push origin main

# Automatic release happens on GitHub
# Package published to TestPyPI
# GitHub release created

# Manual deployment to Production PyPI via GitHub Actions
```
