# AI Job Search Agent
## Project Overview
The AI Job Search Agent is an autonomous and goal-driven system designed to automate the tedious process of searching for new job opportunities. Instead of manually checking various job boards, this intelligent agent leverages the power of large language models (LLMs) and specialized tools to find relevant job postings and deliver them directly to your inbox. This project serves as a practical demonstration of building a functional agentic AI application.

## Key Features
### Autonomous Job Searching: 
The agent operates on a scheduled basis, autonomously initiating job searches without requiring manual intervention.

## Intelligent Tool Use: 
### The agent is equipped with distinct tools for a two-step workflow:
A Job Search Tool that queries real-time job listings from the web
An Email Tool that sends a formatted summary of the findings to a specified email address.

## Daily Automation: 
The agent can be scheduled to run daily using system-level schedulers like Cron (macOS/Linux) or Task Scheduler (Windows), ensuring you receive the latest job postings every day.

## Secure Configuration:
Sensitive information, such as API keys and email credentials, is securely managed using a .env file, keeping it out of the public codebase.
