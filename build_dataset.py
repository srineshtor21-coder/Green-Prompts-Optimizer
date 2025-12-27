"""
GreenPrompts Dataset Builder
Creates training data pairs of verbose and optimized prompts
"""

import json
import os

# Training dataset with verbose -> optimized prompt pairs
TRAINING_DATA = [
    {
        "verbose": "Can you please explain to me what black holes are and how they work in space?",
        "optimized": "Explain black holes and their mechanics"
    },
    {
        "verbose": "Could you help me understand how photosynthesis works in plants?",
        "optimized": "Explain photosynthesis process"
    },
    {
        "verbose": "I need you to tell me about the solar system and all the planets in it",
        "optimized": "Describe solar system planets"
    },
    {
        "verbose": "Please explain to me what quantum computing is and how it differs from regular computing",
        "optimized": "Quantum vs classical computing"
    },
    {
        "verbose": "Can you help me understand what blockchain technology is and how it works?",
        "optimized": "Explain blockchain technology"
    },
    {
        "verbose": "I need help writing a Python program that can sort a list of numbers using bubble sort",
        "optimized": "Write Python bubble sort program"
    },
    {
        "verbose": "Could you please show me how to create a function in JavaScript that reverses a string?",
        "optimized": "JavaScript string reversal function"
    },
    {
        "verbose": "I want you to help me write code in Python to read a CSV file and display its contents",
        "optimized": "Python CSV reader code"
    },
    {
        "verbose": "Can you please help me write a SQL query that selects all users from a database table?",
        "optimized": "SQL query select all users"
    },
    {
        "verbose": "I need help creating a React component that displays a list of items with buttons",
        "optimized": "React list component with buttons"
    },
    {
        "verbose": "I want to learn about the difference between machine learning and deep learning",
        "optimized": "Machine learning vs deep learning"
    },
    {
        "verbose": "Can you please explain to me what neural networks are and how they work?",
        "optimized": "Explain neural networks"
    },
    {
        "verbose": "I need to understand what supervised learning is in machine learning",
        "optimized": "Define supervised learning"
    },
    {
        "verbose": "Could you tell me about the various types of machine learning algorithms that exist?",
        "optimized": "Types of ML algorithms"
    },
    {
        "verbose": "Please help me understand what overfitting means in machine learning models",
        "optimized": "Explain ML overfitting"
    },
    {
        "verbose": "Please tell me how I can improve the performance of my React application",
        "optimized": "Optimize React app performance"
    },
    {
        "verbose": "I want to know how to make my website responsive for mobile devices",
        "optimized": "Create responsive mobile website"
    },
    {
        "verbose": "Can you explain to me what RESTful APIs are and how they work?",
        "optimized": "Explain RESTful APIs"
    },
    {
        "verbose": "I need help understanding how to use CSS Grid for layout design",
        "optimized": "CSS Grid layout tutorial"
    },
    {
        "verbose": "Could you please show me how to implement authentication in a Node.js application?",
        "optimized": "Node.js authentication implementation"
    }
]

# Add 100+ more examples for better training
ADDITIONAL_DATA = [
    {"verbose": "I want to learn about how to perform data visualization using Python libraries", "optimized": "Python data visualization guide"},
    {"verbose": "Can you help me understand what data cleaning is and why it's important?", "optimized": "Explain data cleaning importance"},
    {"verbose": "Please explain to me the difference between correlation and causation in statistics", "optimized": "Correlation vs causation"},
    {"verbose": "I need to know how to handle missing data in my dataset", "optimized": "Handle missing dataset values"},
    {"verbose": "Could you tell me about the best practices for feature engineering in machine learning?", "optimized": "Feature engineering best practices"},
    {"verbose": "I need help creating a business plan for my new startup company", "optimized": "Create startup business plan"},
    {"verbose": "Can you please give me some tips on how to be more productive at work?", "optimized": "Productivity tips for work"},
    {"verbose": "I want to know about effective strategies for time management", "optimized": "Time management strategies"},
    {"verbose": "Please help me understand what a SWOT analysis is and how to use it", "optimized": "Explain SWOT analysis"},
    {"verbose": "Could you tell me about the different types of business models that exist?", "optimized": "Types of business models"},
]

# Combine datasets
TRAINING_DATA.extend(ADDITIONAL_DATA)


def save_dataset(filename="prompt_dataset.json"):
    """Save the dataset to a JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(TRAINING_DATA, f, indent=2, ensure_ascii=False)
    print(f"✅ Dataset saved to {filename}")
    print(f"📊 Total training pairs: {len(TRAINING_DATA)}")


if __name__ == "__main__":
    print("\n🌱 GreenPrompts Dataset Builder")
    print("="*60)
    save_dataset()
    print("="*60)
