# Contributing to Advanced Tape Restorer

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## 🎯 Ways to Contribute

### 1. Bug Reports
- Use GitHub Issues with "bug" label
- Include detailed reproduction steps
- Attach logs and error messages
- Specify system configuration

### 2. Feature Requests
- Use GitHub Issues with "enhancement" label
- Describe the use case and expected behavior
- Explain why the feature would be valuable

### 3. Code Contributions
- Fork the repository
- Create a feature branch
- Write clean, documented code
- Test your changes thoroughly
- Submit a pull request

### 4. Documentation
- Improve README or guides
- Add code examples
- Fix typos or clarify instructions
- Translate documentation

## 🚀 Getting Started

### Development Setup

```powershell
# Fork and clone the repository
git clone https://github.com/yourusername/Advanced-Tape-Restorer.git
cd Advanced-Tape-Restorer

# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Install development tools
pip install pytest pylint black isort

# Run tests to verify setup
python main.py --test
```

### Project Structure

```
core/           # Video processing engine
capture/        # Hardware capture
gui/            # PySide6 interface
ai_models/      # AI model management
docs/           # Documentation
```

## 📝 Coding Standards

### Python Style

- **PEP 8** formatting (use `black` for auto-formatting)
- **Type hints** for function parameters and returns
- **Docstrings** for all public functions (Google style)
- **Maximum line length**: 100 characters

Example:
```python
def process_video(
    input_file: str,
    output_file: str,
    options: dict,
    progress_callback: Callable[[float, str], None] = None
) -> bool:
    """
    Process video with restoration filters.
    
    Args:
        input_file: Path to input video
        output_file: Path to output video
        options: Processing options dictionary
        progress_callback: Optional callback for progress updates
        
    Returns:
        True if processing succeeded, False otherwise
        
    Raises:
        FileNotFoundError: If input file doesn't exist
        RuntimeError: If processing fails
    """
    # Implementation here
    pass
```

### Commit Messages

Use conventional commits format:

```
type(scope): subject

body (optional)

footer (optional)
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style (formatting, no logic change)
- `refactor`: Code restructuring
- `perf`: Performance improvements
- `test`: Adding/updating tests
- `chore`: Build, dependencies, etc.

**Examples:**
```
feat(ai): Add SwinIR upscaling support

Implements SwinIR 2x/4x upscaling with ONNX acceleration.
Includes model downloader and VapourSynth integration.

Closes #123
```

```
fix(checkpoint): Fix parameter name in disk space check

Changed buffer_gb to min_free_gb to match function signature.

Fixes #456
```

## 🔧 Making Changes

### Before Starting

1. **Check existing issues** - Someone may already be working on it
2. **Create an issue** - Discuss your approach before major changes
3. **Branch naming**: `feature/description` or `fix/description`

### Development Workflow

```powershell
# Create feature branch
git checkout -b feature/my-feature

# Make changes
# ... edit files ...

# Format code
black .
isort .

# Run tests
python main.py --test

# Test GUI manually
python main.py

# Commit changes
git add .
git commit -m "feat(scope): description"

# Push to your fork
git push origin feature/my-feature

# Create pull request on GitHub
```

### Testing

- **Unit tests**: Test individual functions
- **Integration tests**: Test module interactions
- **Manual testing**: Run the GUI and verify behavior
- **Edge cases**: Test error handling and boundary conditions

### Pull Request Checklist

Before submitting:

- [ ] Code follows project style guidelines
- [ ] All tests pass (`python main.py --test`)
- [ ] GUI launches without errors (`python main.py`)
- [ ] No new warnings or errors in console
- [ ] Docstrings added for new functions
- [ ] Type hints included
- [ ] Commit messages follow convention
- [ ] PR description explains changes clearly
- [ ] References related issues (e.g., "Closes #123")

## 🐛 Reporting Bugs

### Bug Report Template

```markdown
**System Information:**
- OS: Windows 10/11
- Python version: 3.x
- FFmpeg version: x.x
- VapourSynth version: Rxx
- Advanced Tape Restorer version: v4.x

**Description:**
Clear description of the bug

**Steps to Reproduce:**
1. Launch application
2. Load video file: example.avi
3. Enable GFPGAN
4. Click Start Processing
5. Error occurs at 50% progress

**Expected Behavior:**
Should process video to completion

**Actual Behavior:**
Crashes with error message: "..."

**Logs:**
```
[paste relevant log output here]
```

**Screenshots:**
[if applicable]

**Additional Context:**
Video format: AVI, 720x480, 29.97fps, HuffYUV
```

## 💡 Suggesting Features

### Feature Request Template

```markdown
**Problem/Use Case:**
Describe the problem you're trying to solve

**Proposed Solution:**
Describe your proposed feature

**Alternatives Considered:**
Other approaches you've thought about

**Benefits:**
- Who would benefit?
- How often would it be used?
- What value does it add?

**Implementation Ideas:**
(Optional) Technical suggestions for implementation
```

## 🏗️ Architecture Guidelines

### Adding New AI Models

1. Add model entry to `ai_models/models/registry.yaml`
2. Create engine file in `ai_models/engines/your_model.py`
3. Implement `apply_your_model()` in `core/ai_bridge.py`
4. Add VapourSynth integration in `core/vapoursynth_engine.py`
5. Add GUI controls in `gui/main_window.py`
6. Update documentation

### Adding New Filters

1. Add filter function to `core/vapoursynth_engine.py`
2. Add GUI controls to `gui/main_window.py`
3. Update `restoration_presets.json` with defaults
4. Add settings persistence in `gui/settings_manager.py`
5. Document in README

### Modifying Core Processing

Changes to `core/` modules should:
- Maintain backward compatibility with existing settings
- Use callbacks for progress reporting
- Handle errors gracefully
- Include logging for debugging

## 📚 Documentation

### Code Documentation

- **Module docstrings**: Purpose and overview
- **Class docstrings**: Responsibilities and usage
- **Function docstrings**: Parameters, returns, raises
- **Inline comments**: Explain complex logic (not obvious code)

### User Documentation

- Update README.md for user-facing features
- Add to docs/ folder for detailed guides
- Include code examples
- Add screenshots for GUI changes

## ⚖️ Licensing

By contributing to Advanced Tape Restorer, you agree that your contributions will be licensed under the MIT License.

**Important:**
- Do not include copyrighted material without permission
- Respect AI model licenses (some restrict commercial use)
- Credit original authors when adapting code

## 🤝 Code of Conduct

### Our Standards

- **Be respectful** - Treat everyone with respect
- **Be constructive** - Provide helpful feedback
- **Be patient** - Remember contributors are volunteers
- **Be inclusive** - Welcome newcomers
- **Be collaborative** - Work together toward common goals

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Trolling, insulting/derogatory comments
- Public or private harassment
- Publishing others' private information
- Other conduct inappropriate in a professional setting

## 📞 Getting Help

- **GitHub Discussions**: Ask questions, share ideas
- **GitHub Issues**: Bug reports, feature requests
- **Documentation**: Check docs/ folder and README
- **Code comments**: Many functions have detailed docstrings

## 🙏 Recognition

Contributors will be recognized in:
- GitHub Contributors page
- CHANGELOG.md for significant contributions
- README.md Acknowledgments section

Thank you for contributing to Advanced Tape Restorer! 🎉
