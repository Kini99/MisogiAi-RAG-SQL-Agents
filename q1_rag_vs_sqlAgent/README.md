# E-commerce Customer Support System: RAG vs SQL Agent Comparison

This project provides a comprehensive comparison between Retrieval-Augmented Generation (RAG) and SQL Agent approaches for enabling natural language queries on an e-commerce customer support system.

## Project Overview

The system analyzes two different approaches for allowing customer support teams to query customer data using natural language:

1. **RAG (Retrieval-Augmented Generation)**: Uses vector embeddings and semantic search to retrieve relevant information
2. **SQL Agent**: Uses LLM to generate and execute SQL queries directly on the database

## Database Schema

The system works with a PostgreSQL database containing 5 main tables:
- `customers`: Customer information and profiles
- `orders`: Order details and status
- `products`: Product catalog and inventory
- `reviews`: Customer reviews and ratings
- `support_tickets`: Support ticket tracking

## Project Structure

```
├── requirements.txt              # Python dependencies
├── README.md                    # This file
├── config/                      # Configuration files
│   ├── database.py             # Database connection and schema
│   └── settings.py             # Application settings
├── models/                      # Database models
│   └── schema.py               # SQLAlchemy models
├── systems/                     # Core system implementations
│   ├── rag_system.py           # RAG implementation
│   ├── sql_agent_system.py     # SQL Agent implementation
│   └── base_system.py          # Base system interface
├── evaluation/                  # Performance evaluation
│   ├── benchmark.py            # Benchmarking framework
│   ├── test_queries.py         # Sample test queries
│   └── metrics.py              # Performance metrics
├── demo/                       # Demo applications
│   ├── web_app.py             # FastAPI web interface
│   └── cli_app.py             # Command-line interface
├── data/                       # Sample data and scripts
│   ├── sample_data.py         # Data generation scripts
│   └── setup_database.py      # Database setup
└── reports/                    # Generated reports
    ├── technical_comparison.md # Technical analysis
    └── performance_results.md  # Benchmark results
```

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your database and API credentials
   ```
4. Set up the database:
   ```bash
   python data/setup_database.py
   ```

## Usage

### Running the Benchmark
```bash
python evaluation/benchmark.py
```

### Web Demo
```bash
python demo/web_app.py
```

### CLI Demo
```bash
python demo/cli_app.py
```

## Key Features

- **Comprehensive Comparison**: Detailed analysis of both approaches
- **Performance Benchmarking**: Response time, accuracy, and resource usage metrics
- **Sample Implementations**: Working code for both RAG and SQL Agent systems
- **Interactive Demos**: Web and CLI interfaces for testing
- **Detailed Reports**: Technical analysis and recommendations

## Requirements

- Python 3.11+
- PostgreSQL 12+
- OpenAI API key (for LLM functionality)
- 8GB+ RAM (for vector operations)

## License

MIT License 