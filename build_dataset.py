"""
Green-Prompts-Optimizer: Dataset Builder
Generates training dataset of 127 prompt pairs for model training
"""

import json
from pathlib import Path

# Create data directory
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# ============================================================================
# COMPREHENSIVE TRAINING DATASET - 127 PROMPT PAIRS
# ============================================================================

training_data = [
    # Technical/Programming Prompts (20 pairs)
    {
        "original": "Can you please help me understand how I can write a Python function that will take a list of numbers as input and return the sum of all those numbers?",
        "optimized": "Write Python function to sum list of numbers"
    },
    {
        "original": "I need assistance with creating a JavaScript function that can check if a given string is a palindrome or not",
        "optimized": "Create JavaScript palindrome checker function"
    },
    {
        "original": "Could you explain to me in detail how recursion works in programming and provide some examples?",
        "optimized": "Explain recursion with examples"
    },
    {
        "original": "I'm trying to figure out how to connect my Python application to a MySQL database and perform CRUD operations",
        "optimized": "Connect Python to MySQL for CRUD operations"
    },
    {
        "original": "What would be the best way to implement error handling in my React application?",
        "optimized": "Implement React error handling"
    },
    {
        "original": "Can you help me debug this code? I keep getting a null pointer exception and I don't understand why",
        "optimized": "Debug null pointer exception"
    },
    {
        "original": "I need to learn about the differences between SQL and NoSQL databases and when to use each one",
        "optimized": "Compare SQL vs NoSQL databases"
    },
    {
        "original": "How do I optimize the performance of my website that seems to be loading very slowly?",
        "optimized": "Optimize slow website performance"
    },
    {
        "original": "Could you please show me how to implement authentication in a Node.js Express application?",
        "optimized": "Implement Node.js Express authentication"
    },
    {
        "original": "I'm having trouble understanding how promises and async/await work in JavaScript",
        "optimized": "Explain JavaScript promises and async/await"
    },
    {
        "original": "What are the best practices for writing clean and maintainable code in any programming language?",
        "optimized": "Best practices for clean code"
    },
    {
        "original": "Can you help me understand how to use Git for version control and collaborate with other developers?",
        "optimized": "Use Git for version control collaboration"
    },
    {
        "original": "I need to create a responsive navigation menu for my website that works on mobile devices",
        "optimized": "Create responsive mobile navigation menu"
    },
    {
        "original": "How can I improve the security of my web application to prevent common vulnerabilities?",
        "optimized": "Improve web application security"
    },
    {
        "original": "What's the difference between machine learning and deep learning and which one should I learn first?",
        "optimized": "Difference between ML and deep learning"
    },
    {
        "original": "I want to learn how to deploy my application to AWS but I'm not sure where to start",
        "optimized": "Deploy application to AWS"
    },
    {
        "original": "Can you explain to me how to use CSS Grid and Flexbox for creating modern layouts?",
        "optimized": "Use CSS Grid and Flexbox for layouts"
    },
    {
        "original": "I'm trying to understand how to implement a REST API using Python Flask framework",
        "optimized": "Implement REST API with Flask"
    },
    {
        "original": "What are the most important data structures and algorithms I should know for coding interviews?",
        "optimized": "Key data structures for coding interviews"
    },
    {
        "original": "How do I set up continuous integration and continuous deployment for my project?",
        "optimized": "Setup CI/CD pipeline"
    },
    
    # Academic/Research Prompts (20 pairs)
    {
        "original": "Can you please help me write a comprehensive literature review on climate change impacts on marine ecosystems?",
        "optimized": "Write climate change marine ecosystem literature review"
    },
    {
        "original": "I need assistance in understanding the complex relationship between economic growth and environmental sustainability",
        "optimized": "Explain economic growth vs environmental sustainability"
    },
    {
        "original": "Could you explain to me the fundamental principles of quantum mechanics in simple terms?",
        "optimized": "Explain quantum mechanics principles simply"
    },
    {
        "original": "I'm working on a research paper about artificial intelligence ethics and need help organizing my thoughts",
        "optimized": "Organize AI ethics research paper"
    },
    {
        "original": "What are the major theories in psychology that explain human behavior and decision making?",
        "optimized": "Major psychology theories on human behavior"
    },
    {
        "original": "Can you help me understand the causes and consequences of the Industrial Revolution?",
        "optimized": "Explain Industrial Revolution causes and effects"
    },
    {
        "original": "I need to write an analysis of Shakespeare's use of symbolism in Macbeth for my English class",
        "optimized": "Analyze symbolism in Macbeth"
    },
    {
        "original": "Could you please explain the process of photosynthesis and its importance to life on Earth?",
        "optimized": "Explain photosynthesis process and importance"
    },
    {
        "original": "I'm trying to understand the mathematical concepts behind calculus derivatives and integrals",
        "optimized": "Explain calculus derivatives and integrals"
    },
    {
        "original": "What were the main factors that led to World War II and what were its lasting effects?",
        "optimized": "Causes and effects of World War II"
    },
    {
        "original": "Can you help me understand the structure and function of DNA in biological systems?",
        "optimized": "Explain DNA structure and function"
    },
    {
        "original": "I need to learn about different economic systems like capitalism, socialism, and mixed economies",
        "optimized": "Compare economic systems"
    },
    {
        "original": "Could you explain the theory of evolution and the evidence that supports it?",
        "optimized": "Explain evolution theory and evidence"
    },
    {
        "original": "I'm studying for my chemistry exam and need help understanding chemical bonding and molecular structures",
        "optimized": "Explain chemical bonding and structures"
    },
    {
        "original": "What are the key principles of sustainable development and how can they be implemented?",
        "optimized": "Sustainable development principles and implementation"
    },
    {
        "original": "Can you help me analyze the impact of social media on modern communication and relationships?",
        "optimized": "Analyze social media impact on communication"
    },
    {
        "original": "I need to understand the differences between classical and modern art movements",
        "optimized": "Compare classical vs modern art movements"
    },
    {
        "original": "Could you explain the basic principles of microeconomics including supply and demand?",
        "optimized": "Explain microeconomics supply and demand"
    },
    {
        "original": "I'm writing a paper on renewable energy sources and their potential to replace fossil fuels",
        "optimized": "Analyze renewable energy vs fossil fuels"
    },
    {
        "original": "What are the main philosophical schools of thought and how do they differ from each other?",
        "optimized": "Compare main philosophical schools"
    },
    
    # Business/Professional Prompts (20 pairs)
    {
        "original": "I need help creating a comprehensive business plan for my startup company that will attract investors",
        "optimized": "Create investor-ready business plan"
    },
    {
        "original": "Can you please provide me with some strategies for effective marketing in the digital age?",
        "optimized": "Digital marketing strategies"
    },
    {
        "original": "I'm trying to understand how to improve employee engagement and productivity in my organization",
        "optimized": "Improve employee engagement and productivity"
    },
    {
        "original": "What are the best practices for conducting a successful job interview as an interviewer?",
        "optimized": "Best practices for conducting interviews"
    },
    {
        "original": "I need assistance in developing a strong personal brand for my professional career",
        "optimized": "Develop professional personal brand"
    },
    {
        "original": "Could you help me understand the principles of project management and how to apply them?",
        "optimized": "Explain project management principles"
    },
    {
        "original": "I'm looking for advice on how to negotiate a better salary during a job offer discussion",
        "optimized": "Negotiate better salary offer"
    },
    {
        "original": "What are effective strategies for managing work-life balance in a demanding career?",
        "optimized": "Manage work-life balance strategies"
    },
    {
        "original": "Can you provide guidance on how to build and maintain professional networks?",
        "optimized": "Build professional network"
    },
    {
        "original": "I need help writing a compelling cover letter for a job application in the tech industry",
        "optimized": "Write tech industry cover letter"
    },
    {
        "original": "What are the key metrics I should track to measure the success of my business?",
        "optimized": "Key business success metrics"
    },
    {
        "original": "How can I improve my public speaking skills for professional presentations?",
        "optimized": "Improve public speaking skills"
    },
    {
        "original": "I'm trying to understand financial statements and how to read a balance sheet and income statement",
        "optimized": "Read financial statements guide"
    },
    {
        "original": "What are the best practices for managing a remote team effectively?",
        "optimized": "Manage remote team effectively"
    },
    {
        "original": "Can you help me develop a content marketing strategy for my business?",
        "optimized": "Develop content marketing strategy"
    },
    {
        "original": "I need advice on how to handle difficult conversations with employees or colleagues",
        "optimized": "Handle difficult workplace conversations"
    },
    {
        "original": "What are the essential elements of a successful sales pitch?",
        "optimized": "Essential sales pitch elements"
    },
    {
        "original": "How can I improve my time management skills to be more productive at work?",
        "optimized": "Improve time management productivity"
    },
    {
        "original": "I'm looking for strategies to reduce operational costs in my business without sacrificing quality",
        "optimized": "Reduce operational costs maintain quality"
    },
    {
        "original": "Can you explain the basics of search engine optimization for improving website visibility?",
        "optimized": "SEO basics for website visibility"
    },
    
    # Creative/Writing Prompts (20 pairs)
    {
        "original": "I need help brainstorming ideas for a science fiction short story about time travel",
        "optimized": "Brainstorm time travel story ideas"
    },
    {
        "original": "Can you provide me with tips for improving my creative writing skills and developing my unique voice?",
        "optimized": "Improve creative writing skills"
    },
    {
        "original": "I'm trying to come up with a compelling plot for a mystery novel set in Victorian England",
        "optimized": "Create Victorian mystery novel plot"
    },
    {
        "original": "What are some effective techniques for writing dialogue that sounds natural and engaging?",
        "optimized": "Write natural engaging dialogue"
    },
    {
        "original": "I need assistance in developing complex and believable characters for my fantasy novel",
        "optimized": "Develop fantasy novel characters"
    },
    {
        "original": "Can you help me understand the structure of a three-act screenplay?",
        "optimized": "Explain three-act screenplay structure"
    },
    {
        "original": "I'm looking for inspiration to write poetry about nature and the changing seasons",
        "optimized": "Write nature seasons poetry"
    },
    {
        "original": "What are the key elements of effective storytelling that keep readers engaged?",
        "optimized": "Key storytelling engagement elements"
    },
    {
        "original": "I need help creating a detailed world for my science fiction universe",
        "optimized": "Build sci-fi universe world"
    },
    {
        "original": "Can you provide feedback on how to improve my blog writing style and make it more engaging?",
        "optimized": "Improve blog writing engagement"
    },
    {
        "original": "I'm trying to write a compelling opening paragraph for my novel that will hook readers",
        "optimized": "Write compelling novel opening"
    },
    {
        "original": "What are some creative writing exercises I can do to overcome writer's block?",
        "optimized": "Creative exercises overcome writer's block"
    },
    {
        "original": "I need help developing the villain in my story to make them more complex and interesting",
        "optimized": "Develop complex villain character"
    },
    {
        "original": "Can you explain the differences between showing and telling in creative writing?",
        "optimized": "Explain showing vs telling writing"
    },
    {
        "original": "I'm looking for ways to create tension and suspense in my thriller novel",
        "optimized": "Create thriller tension suspense"
    },
    {
        "original": "What are the best practices for writing a compelling memoir or personal narrative?",
        "optimized": "Write compelling memoir"
    },
    {
        "original": "I need assistance in crafting realistic and meaningful romantic relationships in my story",
        "optimized": "Craft realistic story romance"
    },
    {
        "original": "Can you help me understand how to use symbolism and metaphors effectively in my writing?",
        "optimized": "Use symbolism metaphors effectively"
    },
    {
        "original": "I'm trying to write song lyrics but I'm having trouble making them flow naturally",
        "optimized": "Write natural flowing lyrics"
    },
    {
        "original": "What are some techniques for writing effective descriptions that bring scenes to life?",
        "optimized": "Write vivid scene descriptions"
    },
    
    # General Knowledge/Lifestyle Prompts (20 pairs)
    {
        "original": "Can you please help me plan a healthy meal prep routine for the entire week?",
        "optimized": "Plan weekly meal prep routine"
    },
    {
        "original": "I need advice on how to start a regular exercise routine and stick with it long-term",
        "optimized": "Start sustainable exercise routine"
    },
    {
        "original": "What are some effective strategies for managing stress and anxiety in daily life?",
        "optimized": "Manage daily stress anxiety"
    },
    {
        "original": "I'm trying to learn a new language and need tips for effective language learning",
        "optimized": "Effective language learning tips"
    },
    {
        "original": "Can you provide guidance on how to create and maintain a budget for personal finances?",
        "optimized": "Create personal budget"
    },
    {
        "original": "I need help understanding how to invest money wisely for long-term financial growth",
        "optimized": "Invest for long-term growth"
    },
    {
        "original": "What are some good habits I can develop to improve my overall health and wellbeing?",
        "optimized": "Develop healthy habits"
    },
    {
        "original": "I'm looking for ideas to decorate my small apartment on a limited budget",
        "optimized": "Decorate small apartment budget-friendly"
    },
    {
        "original": "Can you help me plan an affordable vacation that's still fun and memorable?",
        "optimized": "Plan affordable fun vacation"
    },
    {
        "original": "I need advice on how to improve my sleep quality and establish a better sleep routine",
        "optimized": "Improve sleep quality routine"
    },
    {
        "original": "What are some ways to reduce my environmental impact and live more sustainably?",
        "optimized": "Live sustainably reduce impact"
    },
    {
        "original": "I'm trying to organize my home and get rid of unnecessary clutter",
        "optimized": "Organize home declutter"
    },
    {
        "original": "Can you provide tips for effective communication in personal relationships?",
        "optimized": "Improve relationship communication"
    },
    {
        "original": "I need help creating a morning routine that will set me up for a productive day",
        "optimized": "Create productive morning routine"
    },
    {
        "original": "What are some strategies for building self-confidence and self-esteem?",
        "optimized": "Build confidence self-esteem"
    },
    {
        "original": "I'm looking for ways to make new friends and expand my social circle as an adult",
        "optimized": "Make friends expand social circle"
    },
    {
        "original": "Can you help me understand how to practice mindfulness and meditation?",
        "optimized": "Practice mindfulness meditation"
    },
    {
        "original": "I need advice on how to set and achieve personal goals effectively",
        "optimized": "Set achieve personal goals"
    },
    {
        "original": "What are some tips for maintaining long-distance relationships with friends and family?",
        "optimized": "Maintain long-distance relationships"
    },
    {
        "original": "I'm trying to develop better critical thinking skills and make more informed decisions",
        "optimized": "Develop critical thinking skills"
    },
    
    # Technical Support/How-To Prompts (15 pairs)
    {
        "original": "My computer is running really slowly and I don't know what to do to fix it",
        "optimized": "Fix slow computer performance"
    },
    {
        "original": "I need help setting up a home WiFi network that's secure and reliable",
        "optimized": "Setup secure home WiFi"
    },
    {
        "original": "How can I protect my personal information and stay safe online from cyber threats?",
        "optimized": "Protect personal data online"
    },
    {
        "original": "I'm having trouble with my smartphone battery draining too quickly",
        "optimized": "Fix smartphone battery drain"
    },
    {
        "original": "Can you explain how to back up my important files and data safely?",
        "optimized": "Backup files data safely"
    },
    {
        "original": "I need to learn how to use Microsoft Excel for data analysis and spreadsheets",
        "optimized": "Learn Excel data analysis"
    },
    {
        "original": "What are the steps to recover deleted files from my computer or hard drive?",
        "optimized": "Recover deleted files"
    },
    {
        "original": "I'm trying to understand how to use cloud storage services effectively",
        "optimized": "Use cloud storage effectively"
    },
    {
        "original": "Can you help me troubleshoot why my printer isn't working properly?",
        "optimized": "Troubleshoot printer issues"
    },
    {
        "original": "I need to know how to create strong passwords and manage them securely",
        "optimized": "Create manage secure passwords"
    },
    {
        "original": "What are the best ways to speed up my internet connection at home?",
        "optimized": "Speed up internet connection"
    },
    {
        "original": "I'm having issues with my email account and can't send or receive messages",
        "optimized": "Fix email sending receiving"
    },
    {
        "original": "How do I transfer all my data from my old phone to my new phone?",
        "optimized": "Transfer data to new phone"
    },
    {
        "original": "I need help understanding how to use video conferencing software for meetings",
        "optimized": "Use video conferencing software"
    },
    {
        "original": "What should I do if I think my computer has been infected with malware or viruses?",
        "optimized": "Remove malware virus infection"
    },
    
    # Education/Learning Prompts (12 pairs)
    {
        "original": "I'm struggling to understand algebraic equations and need a clear explanation",
        "optimized": "Explain algebraic equations clearly"
    },
    {
        "original": "Can you help me develop better study habits for college exams?",
        "optimized": "Develop effective study habits"
    },
    {
        "original": "I need strategies for improving my reading comprehension and retention",
        "optimized": "Improve reading comprehension retention"
    },
    {
        "original": "What are some effective note-taking methods for lectures and classes?",
        "optimized": "Effective note-taking methods"
    },
    {
        "original": "I'm trying to learn how to write a proper research paper with citations",
        "optimized": "Write research paper with citations"
    },
    {
        "original": "Can you explain the scientific method and how to apply it to experiments?",
        "optimized": "Explain apply scientific method"
    },
    {
        "original": "I need help preparing for standardized tests like the SAT or ACT",
        "optimized": "Prepare for SAT ACT tests"
    },
    {
        "original": "What are some ways to improve my memory and recall for studying?",
        "optimized": "Improve memory recall studying"
    },
    {
        "original": "I'm looking for online resources to learn new skills and subjects independently",
        "optimized": "Find online learning resources"
    },
    {
        "original": "Can you help me understand how to analyze and interpret data from graphs and charts?",
        "optimized": "Analyze interpret graphs charts"
    },
    {
        "original": "I need advice on choosing a college major that aligns with my interests and career goals",
        "optimized": "Choose college major wisely"
    },
    {
        "original": "What are effective strategies for overcoming test anxiety and performing better on exams?",
        "optimized": "Overcome test anxiety"
    }
]

# ============================================================================
# SAVE DATASET TO FILE
# ============================================================================

def save_dataset():
    """Save the training dataset to JSON file"""
    
    # Verify we have exactly 127 pairs
    assert len(training_data) == 127, f"Expected 127 pairs, got {len(training_data)}"
    
    output_path = DATA_DIR / "training_dataset.json"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'dataset_info': {
                'name': 'Green-Prompts-Optimizer Training Dataset',
                'description': 'Dataset for training T5 model to optimize prompts for energy efficiency',
                'total_pairs': len(training_data),
                'created_by': 'Srinesh Toranala',
                'version': '1.0'
            },
            'data': training_data
        }, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Dataset saved successfully!")
    print(f"✓ Location: {output_path}")
    print(f"✓ Total prompt pairs: {len(training_data)}")
    
    # Calculate statistics
    original_lengths = [len(item['original']) for item in training_data]
    optimized_lengths = [len(item['optimized']) for item in training_data]
    
    print(f"\n=== Dataset Statistics ===")
    print(f"Original prompts:")
    print(f"  - Average length: {sum(original_lengths) / len(original_lengths):.1f} characters")
    print(f"  - Min length: {min(original_lengths)} characters")
    print(f"  - Max length: {max(original_lengths)} characters")
    print(f"\nOptimized prompts:")
    print(f"  - Average length: {sum(optimized_lengths) / len(optimized_lengths):.1f} characters")
    print(f"  - Min length: {min(optimized_lengths)} characters")
    print(f"  - Max length: {max(optimized_lengths)} characters")
    print(f"\nAverage reduction: {100 * (1 - sum(optimized_lengths) / sum(original_lengths)):.1f}%")

if __name__ == "__main__":
    save_dataset()
