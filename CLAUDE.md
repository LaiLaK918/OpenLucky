# Claude Memory - User Preferences and Requirements

## Data Display Standards

### AI Response Format
- **Field Names**: Use clear names like `instId (Instrument ID)` or `instId<br/>(Instrument ID)`
- **Empty Values**: Display as `N/A` or `-` for empty fields
- **Data Structure**: Use structured 4-column layout
- **HTML Tags**: Convert HTML tags like `<br/>` to Markdown format
- **Data Validation**: Validate data accuracy and completeness
- **Error Handling**: Handle 4xx errors gracefully in AI responses

### API Parameters
- **Parameter Names**: Use descriptive API parameter names
- **Parameter Format**: Follow standard parameter formatting
- **Documentation**: Use format `parameter = value - description`

## Python Development Standards

### Code Quality
- **Function Names**: Use descriptive function names with clear purpose
- **Code Style**: Follow PEP8 standards and maintain consistency
- **Documentation**: Include comprehensive docstrings

### Function Documentation
- **Docstring Format**: Use clear docstrings like `"""Generate AI-friendly MD report"""`
- **Type Hints**: Use proper type annotations
- **Return Types**: Specify return types like `Dict[str, Any]`

### Error Handling
- **Exception Handling**: Use proper try-catch blocks
- **Error Messages**: Provide clear and actionable error messages
- **API Errors**: Log API errors for debugging
- **Logging**: Use structured logging for API calls

### Code Organization
- **Import Style**: Use explicit imports
- **Module Structure**: Organize code into logical modules
- **Constants**: Define constants clearly
- **Utilities**: Avoid using `import *`

### Data Processing
- **Data Validation**: Validate all input data thoroughly
- **Format Standards**: Follow consistent data formatting
- **Empty Handling**: Handle empty data gracefully
- **JSON Processing**: Use proper JSON processing methods

## Project Specific Requirements

### OKX API Integration
- **Configuration**: Store API credentials in config.ini
- **Rate Limiting**: Respect API rate limits (1% safety margin)
- **Data Processing**: Process API response data with proper error handling
- **Documentation**: Reference API documentation in docs/ folder

### Report Generation
- **Format**: Generate reports in Markdown format
- **Content**: Include comprehensive analysis and insights
- **AI Integration**: Optimize for AI readability and processing
- **Data Sources**: Combine multiple data sources effectively