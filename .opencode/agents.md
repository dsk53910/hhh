# AI Agent Configuration and Usage Patterns

## Agent Capabilities

### Primary Agent (OpenCode)
- **Primary Functions**: Code generation, architecture planning, documentation
- **Strengths**: 
  - Full-stack development (Python, Telegram bots, databases)
  - System design and architecture
  - Best practices implementation
  - Code review and optimization
- **Limitations**: 
  - Cannot execute code directly (requires bash tool)
  - Cannot browse files without specific tools
  - Must follow strict security guidelines

### Specialized Agents
- **General Agent**: Complex multi-step tasks, parallel operations
- **Explore Agent**: Fast codebase exploration, pattern finding
- **Code Search Agent**: API documentation, programming patterns

## Usage Patterns for HHH Project

### 1. Planning Phase (Current)
```
User: "I want to build X"
Agent: 
- Research existing solutions
- Create comprehensive plan
- Ask clarifying questions
- Document architecture decisions
```

### 2. Implementation Phase
```
User: "Implement feature X"
Agent:
- Read existing code to understand patterns
- Generate code following project conventions
- Implement with proper error handling
- Add logging and monitoring
```

### 3. Database Development
```
Agent Workflow:
1. Design schema with Pydantic models
2. Create SQLAlchemy models
3. Generate Alembic migrations
4. Write test data fixtures
```

### 4. Telegram Bot Development
```
Agent Pattern:
1. Use aiogram best practices
2. Implement async handlers
3. Add inline keyboards
4. Include middleware for auth/logging
```

## Project-Specific Instructions

### Code Style Guidelines
- Follow PEP 8 strictly
- Use type hints everywhere
- Async/await for all I/O operations
- Comprehensive docstrings
- Logging with structured format

### Security Requirements
- Never hardcode secrets
- Validate all user inputs
- Use environment variables for configuration
- Implement rate limiting
- Add audit logging

### HH.ru Integration Rules
- Respect rate limits (max 100 requests/hour)
- Use proper User-Agent headers
- Implement retry logic with exponential backoff
- Cache responses to reduce API calls
- Handle anti-bot measures gracefully

### Database Patterns
- Use SQLAlchemy 2.0 async patterns
- Always use connection pooling
- Implement proper transaction handling
- Add database indexes for performance
- Use Alembic for all schema changes

## Testing Strategy
- Unit tests for all business logic
- Integration tests for external APIs
- End-to-end tests for critical user flows
- Mock external services in tests
- Target 90%+ code coverage

## Configuration Management
- Use Pydantic for validation
- Support environment variable overrides
- Separate development/production configs
- Document all configuration options
- Use YAML for human-readable configs

## Monitoring and Observability
- Structured logging with correlation IDs
- Metrics collection (response times, error rates)
- Health check endpoints
- Performance monitoring
- Error tracking and alerting

## Agent Collaboration Rules

### When to Use Multiple Agents
- Complex refactoring across multiple files
- Performance optimization requiring deep analysis
- Security audits and vulnerability scanning
- Large-scale code generation

### Handoff Patterns
1. **Explore Agent**: Find files and patterns
2. **Code Search**: Get API documentation and examples  
3. **Primary Agent**: Implement based on research

### Review Workflow
1. Agent generates code
2. Human reviews for business logic
3. Agent runs tests and linting
4. Human approves deployment

## Version Control Best Practices
- Atomic commits with clear messages
- Feature branches for development
- Pull requests for all changes
- Automated tests on PR
- Semantic versioning

## Documentation Requirements
- README with setup instructions
- API documentation
- Configuration examples
- Deployment guides
- Troubleshooting sections

## Performance Guidelines
- Async operations for all I/O
- Database query optimization
- Caching strategies
- Memory usage monitoring
- Response time targets (<200ms for bot commands)

## Error Handling Patterns
- Graceful degradation
- User-friendly error messages
- Comprehensive logging
- Retry mechanisms
- Fallback strategies