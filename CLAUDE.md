# AI Code Helper Project

## Project Overview
This is an AI-powered Python CLI tool that reviews, explains, 
and improves Python code using the Groq API and LLaMA AI model.

## Project Structure
- main.py - Main CLI tool with review, explain, improve commands
- test_code.py - Sample Python file for testing
- .env - API keys (never commit this file!)

## Key Commands
- python main.py review <filename> - Review code for bugs
- python main.py explain <filename> - Explain what code does
- python main.py improve <filename> - Suggest improvements

## Important Files
The main logic is in @main.py
Test with @test_code.py

## Coding Style
- Use snake_case for all variable names
- Use f-strings for string formatting
- Keep functions small and focused
- Only comment complex code

## API
- Uses Groq API with LLaMA 3.3 70B model
- API key stored in .env file as GROQ_API_KEY
- Never hardcode API keys in code