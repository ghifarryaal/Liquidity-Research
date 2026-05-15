# Contributing to LiquidityResearch

Thank you for your interest in contributing to LiquidityResearch! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/Liquidity-Research.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes
6. Commit with clear messages: `git commit -m "feat: add new feature"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Open a Pull Request

## 📝 Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

## 🧪 Testing

### Frontend
```bash
cd frontend
npm run test
npm run lint
```

### Backend
```bash
cd backend
pytest tests/
python -m pylint app/
```

## 📋 Pull Request Guidelines

- Keep PRs focused on a single feature or fix
- Include tests for new features
- Update documentation as needed
- Ensure all tests pass
- Follow existing code style

## 🐛 Reporting Bugs

When reporting bugs, please include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable
- Environment details (OS, browser, versions)

## 💡 Feature Requests

We welcome feature requests! Please:
- Check if the feature already exists
- Clearly describe the use case
- Explain why it would be valuable
- Consider implementation complexity

## 📖 Code Style

### Frontend (JavaScript/React)
- Use functional components with hooks
- Follow ESLint configuration
- Use meaningful variable names
- Add JSDoc comments for complex functions

### Backend (Python)
- Follow PEP 8 style guide
- Use type hints
- Add docstrings to functions
- Keep functions focused and small

## 🤝 Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Help others learn and grow

## 📞 Questions?

Feel free to open an issue for any questions or clarifications.

Thank you for contributing! 🎉
