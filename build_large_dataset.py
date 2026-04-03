"""
GreenPromptsOptimizer: Large Dataset Builder
Generates 10,000+ prompt optimization pairs across diverse categories.
Run this locally, then upload the resulting model to Hugging Face.

Usage:
    python build_large_dataset.py
Output:
    data/training_dataset_10k.json
"""

import json
import random
import re
from pathlib import Path

random.seed(42)
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)


# ===========================================================================
# CORE HAND-CRAFTED PAIRS (expanded from original 127)
# ===========================================================================

BASE_PAIRS = [
    # --- PROGRAMMING / TECHNICAL ---
    ("Can you please help me understand how I can write a Python function that will take a list of numbers as input and return the sum of all those numbers?", "Write Python function to sum list of numbers"),
    ("I need assistance with creating a JavaScript function that can check if a given string is a palindrome or not", "Create JavaScript palindrome checker"),
    ("Could you explain to me in detail how recursion works in programming and provide some examples?", "Explain recursion with code examples"),
    ("I'm trying to figure out how to connect my Python application to a MySQL database and perform CRUD operations", "Connect Python to MySQL for CRUD"),
    ("What would be the best way to implement error handling in my React application?", "Implement React error handling"),
    ("Can you help me debug this code? I keep getting a null pointer exception and I don't understand why", "Debug null pointer exception"),
    ("I need to learn about the differences between SQL and NoSQL databases and when to use each one", "Compare SQL vs NoSQL databases"),
    ("How do I optimize the performance of my website that seems to be loading very slowly?", "Optimize slow website performance"),
    ("Could you please show me how to implement authentication in a Node.js Express application?", "Implement Node.js Express authentication"),
    ("I'm having trouble understanding how promises and async/await work in JavaScript", "Explain JavaScript promises and async/await"),
    ("What are the best practices for writing clean and maintainable code in any programming language?", "Best practices for clean maintainable code"),
    ("Can you help me understand how to use Git for version control and collaborate with other developers?", "Use Git for team version control"),
    ("I need to create a responsive navigation menu for my website that works on mobile devices", "Create responsive mobile navigation menu"),
    ("How can I improve the security of my web application to prevent common vulnerabilities?", "Improve web application security"),
    ("What's the difference between machine learning and deep learning and which one should I learn first?", "Compare ML vs deep learning"),
    ("I want to learn how to deploy my application to AWS but I'm not sure where to start", "Deploy application to AWS"),
    ("Can you explain to me how to use CSS Grid and Flexbox for creating modern layouts?", "Use CSS Grid and Flexbox"),
    ("I'm trying to understand how to implement a REST API using Python Flask framework", "Implement REST API with Flask"),
    ("What are the most important data structures and algorithms I should know for coding interviews?", "Key data structures for coding interviews"),
    ("How do I set up continuous integration and continuous deployment for my project?", "Set up CI/CD pipeline"),
    ("I need to write a Python script that reads a CSV file and outputs a summary of the data", "Write Python script to summarize CSV"),
    ("Can you show me how to implement binary search in Python?", "Implement binary search in Python"),
    ("I want to understand how hash maps work internally", "Explain hash map internals"),
    ("How do I reverse a linked list in place?", "Reverse linked list in place"),
    ("Can you explain the time and space complexity of quicksort?", "Explain quicksort complexity"),
    ("I need to implement a queue using two stacks", "Implement queue using two stacks"),
    ("How do I handle file I/O in Python safely?", "Handle Python file I/O safely"),
    ("Can you show me how to write unit tests in Python using pytest?", "Write Python unit tests with pytest"),
    ("I want to learn how Docker containers work and how to use them", "Learn Docker containers"),
    ("How do I make an HTTP request in Python?", "Make HTTP request in Python"),
    ("Can you explain what a closure is in JavaScript?", "Explain JavaScript closures"),
    ("I need to sort a dictionary by value in Python", "Sort Python dictionary by value"),
    ("How do I use list comprehensions effectively in Python?", "Use Python list comprehensions"),
    ("Can you explain the difference between == and === in JavaScript?", "Explain == vs === JavaScript"),
    ("I want to understand how React hooks work", "Explain React hooks"),
    ("How do I implement memoization in Python?", "Implement Python memoization"),
    ("Can you show me how to use regular expressions in Python?", "Use Python regular expressions"),
    ("I need to parse JSON data in JavaScript", "Parse JSON in JavaScript"),
    ("How do I create a class with inheritance in Python?", "Create Python class with inheritance"),
    ("Can you explain what REST vs GraphQL differences are?", "Compare REST vs GraphQL"),
    ("I want to learn how to use pandas for data analysis", "Learn pandas data analysis"),
    ("How do I profile Python code for performance issues?", "Profile Python code performance"),
    ("Can you explain what microservices architecture is?", "Explain microservices architecture"),
    ("I need to implement rate limiting in my API", "Implement API rate limiting"),
    ("How do I use environment variables in Node.js?", "Use Node.js environment variables"),
    ("Can you show me how to write a Makefile?", "Write a Makefile"),
    ("I want to understand Kubernetes basics", "Explain Kubernetes basics"),
    ("How do I set up a PostgreSQL database with Docker?", "Set up PostgreSQL with Docker"),
    ("Can you explain how OAuth2 works?", "Explain OAuth2 flow"),
    ("I need to implement a debounce function in JavaScript", "Implement JavaScript debounce"),

    # --- SCIENCE / ACADEMIC ---
    ("Can you please help me write a comprehensive literature review on climate change impacts on marine ecosystems?", "Write climate change marine ecosystem literature review"),
    ("I need assistance in understanding the complex relationship between economic growth and environmental sustainability", "Explain economic growth vs environmental sustainability"),
    ("Could you explain to me the fundamental principles of quantum mechanics in simple terms?", "Explain quantum mechanics simply"),
    ("I'm working on a research paper about artificial intelligence ethics and need help organizing my thoughts", "Organize AI ethics research paper"),
    ("What are the major theories in psychology that explain human behavior and decision making?", "Major psychology theories on behavior"),
    ("Can you help me understand the causes and consequences of the Industrial Revolution?", "Explain Industrial Revolution causes and effects"),
    ("I need to write an analysis of Shakespeare's use of symbolism in Macbeth for my English class", "Analyze symbolism in Macbeth"),
    ("Could you please explain the process of photosynthesis and its importance to life on Earth?", "Explain photosynthesis and its importance"),
    ("I'm trying to understand the mathematical concepts behind calculus derivatives and integrals", "Explain calculus derivatives and integrals"),
    ("What were the main factors that led to World War II and what were its lasting effects?", "Causes and effects of World War II"),
    ("Can you help me understand the structure and function of DNA in biological systems?", "Explain DNA structure and function"),
    ("I need to learn about different economic systems like capitalism, socialism, and mixed economies", "Compare economic systems"),
    ("Could you explain the theory of evolution and the evidence that supports it?", "Explain evolution theory and evidence"),
    ("I'm studying for my chemistry exam and need help understanding chemical bonding and molecular structures", "Explain chemical bonding and structures"),
    ("What are the key principles of sustainable development and how can they be implemented?", "Sustainable development principles"),
    ("Can you help me analyze the impact of social media on modern communication and relationships?", "Analyze social media communication impact"),
    ("I need to understand the differences between classical and modern art movements", "Compare classical vs modern art"),
    ("Could you explain the basic principles of microeconomics including supply and demand?", "Explain microeconomics supply and demand"),
    ("I'm writing a paper on renewable energy sources and their potential to replace fossil fuels", "Analyze renewable energy vs fossil fuels"),
    ("What are the main philosophical schools of thought and how do they differ from each other?", "Compare philosophical schools of thought"),
    ("Can you explain how the human immune system works?", "Explain human immune system"),
    ("I want to understand general relativity in simple terms", "Explain general relativity simply"),
    ("How does CRISPR gene editing work?", "Explain CRISPR gene editing"),
    ("What causes the northern lights?", "Explain northern lights cause"),
    ("How does nuclear fusion differ from fission?", "Compare nuclear fusion vs fission"),
    ("Explain the greenhouse effect and global warming", "Explain greenhouse effect"),
    ("What is the Doppler effect and how is it used?", "Explain Doppler effect"),
    ("How do vaccines train the immune system?", "Explain vaccine immune training"),
    ("What is entropy in thermodynamics?", "Explain thermodynamic entropy"),
    ("How does the human brain store memories?", "Explain brain memory storage"),

    # --- BUSINESS / PROFESSIONAL ---
    ("I need help creating a comprehensive business plan for my startup company that will attract investors", "Create investor-ready startup business plan"),
    ("Can you please provide me with some strategies for effective marketing in the digital age?", "Digital marketing strategies"),
    ("I'm trying to understand how to improve employee engagement and productivity in my organization", "Improve employee engagement and productivity"),
    ("What are the best practices for conducting a successful job interview as an interviewer?", "Best practices for interviewing candidates"),
    ("I need assistance in developing a strong personal brand for my professional career", "Build professional personal brand"),
    ("Could you help me understand the principles of project management and how to apply them?", "Explain project management principles"),
    ("I'm looking for advice on how to negotiate a better salary during a job offer discussion", "Negotiate better salary"),
    ("What are effective strategies for managing work-life balance in a demanding career?", "Manage work-life balance"),
    ("Can you provide guidance on how to build and maintain professional networks?", "Build professional networks"),
    ("I need help writing a compelling cover letter for a job application in the tech industry", "Write tech cover letter"),
    ("What are the key metrics I should track to measure the success of my business?", "Key business success metrics"),
    ("How can I improve my public speaking skills for professional presentations?", "Improve public speaking"),
    ("I'm trying to understand financial statements and how to read a balance sheet and income statement", "Read financial statements"),
    ("What are the best practices for managing a remote team effectively?", "Manage remote team"),
    ("Can you help me develop a content marketing strategy for my business?", "Develop content marketing strategy"),
    ("I need advice on how to handle difficult conversations with employees or colleagues", "Handle difficult workplace conversations"),
    ("What are the essential elements of a successful sales pitch?", "Essential sales pitch elements"),
    ("How can I improve my time management skills to be more productive at work?", "Improve time management"),
    ("I'm looking for strategies to reduce operational costs in my business without sacrificing quality", "Reduce operational costs"),
    ("Can you explain the basics of search engine optimization for improving website visibility?", "SEO basics"),
    ("What is the difference between B2B and B2C marketing?", "Compare B2B vs B2C marketing"),
    ("How do I calculate customer lifetime value?", "Calculate customer lifetime value"),
    ("What is a SWOT analysis and how do I do one?", "Explain SWOT analysis"),
    ("How do I create an effective onboarding process for new employees?", "Create employee onboarding process"),
    ("What is agile methodology and how does it work?", "Explain agile methodology"),
    ("How do I write an effective executive summary?", "Write executive summary"),
    ("What metrics should a SaaS company track?", "Key SaaS company metrics"),
    ("How do I conduct a competitive analysis?", "Conduct competitive analysis"),
    ("What is product-market fit and how do I find it?", "Explain product-market fit"),
    ("How do I create a go-to-market strategy?", "Create go-to-market strategy"),

    # --- CREATIVE WRITING ---
    ("I need help brainstorming ideas for a science fiction short story about time travel", "Brainstorm sci-fi time travel story ideas"),
    ("Can you provide me with tips for improving my creative writing skills and developing my unique voice?", "Improve creative writing voice"),
    ("I'm trying to come up with a compelling plot for a mystery novel set in Victorian England", "Create Victorian mystery novel plot"),
    ("What are some effective techniques for writing dialogue that sounds natural and engaging?", "Write natural dialogue techniques"),
    ("I need assistance in developing complex and believable characters for my fantasy novel", "Develop fantasy novel characters"),
    ("Can you help me understand the structure of a three-act screenplay?", "Explain three-act screenplay structure"),
    ("I'm looking for inspiration to write poetry about nature and the changing seasons", "Write nature poetry inspiration"),
    ("What are the key elements of effective storytelling that keep readers engaged?", "Key storytelling elements"),
    ("I need help creating a detailed world for my science fiction universe", "Build sci-fi world"),
    ("Can you provide feedback on how to improve my blog writing style and make it more engaging?", "Improve blog writing engagement"),
    ("I'm trying to write a compelling opening paragraph for my novel that will hook readers", "Write compelling novel opening"),
    ("What are some creative writing exercises I can do to overcome writer's block?", "Overcome writer's block exercises"),
    ("I need help developing the villain in my story to make them more complex and interesting", "Develop complex villain character"),
    ("Can you explain the differences between showing and telling in creative writing?", "Explain show vs tell in writing"),
    ("I'm looking for ways to create tension and suspense in my thriller novel", "Create thriller tension and suspense"),
    ("What are the best practices for writing a compelling memoir or personal narrative?", "Write compelling memoir"),
    ("I need assistance in crafting realistic and meaningful romantic relationships in my story", "Craft realistic romance in story"),
    ("Can you help me understand how to use symbolism and metaphors effectively in my writing?", "Use symbolism and metaphors in writing"),
    ("I'm trying to write song lyrics but I'm having trouble making them flow naturally", "Write natural song lyrics"),
    ("What are some techniques for writing effective descriptions that bring scenes to life?", "Write vivid scene descriptions"),

    # --- HEALTH / LIFESTYLE ---
    ("Can you please help me plan a healthy meal prep routine for the entire week?", "Plan weekly healthy meal prep"),
    ("I need advice on how to start a regular exercise routine and stick with it long-term", "Start sustainable exercise routine"),
    ("What are some effective strategies for managing stress and anxiety in daily life?", "Manage daily stress and anxiety"),
    ("I'm trying to learn a new language and need tips for effective language learning", "Tips for learning a new language"),
    ("Can you provide guidance on how to create and maintain a budget for personal finances?", "Create personal finance budget"),
    ("I need help understanding how to invest money wisely for long-term financial growth", "Invest for long-term growth"),
    ("What are some good habits I can develop to improve my overall health and wellbeing?", "Develop healthy habits"),
    ("I'm looking for ideas to decorate my small apartment on a limited budget", "Decorate small apartment cheaply"),
    ("Can you help me plan an affordable vacation that's still fun and memorable?", "Plan affordable memorable vacation"),
    ("I need advice on how to improve my sleep quality and establish a better sleep routine", "Improve sleep quality"),
    ("What are some ways to reduce my environmental impact and live more sustainably?", "Live sustainably"),
    ("I'm trying to organize my home and get rid of unnecessary clutter", "Organize home and declutter"),
    ("Can you provide tips for effective communication in personal relationships?", "Improve relationship communication"),
    ("I need help creating a morning routine that will set me up for a productive day", "Create productive morning routine"),
    ("What are some strategies for building self-confidence and self-esteem?", "Build self-confidence"),
    ("I'm looking for ways to make new friends and expand my social circle as an adult", "Make friends as adult"),
    ("Can you help me understand how to practice mindfulness and meditation?", "Practice mindfulness and meditation"),
    ("I need advice on how to set and achieve personal goals effectively", "Set and achieve personal goals"),
    ("What are some tips for maintaining long-distance relationships with friends and family?", "Maintain long-distance relationships"),
    ("I'm trying to develop better critical thinking skills and make more informed decisions", "Develop critical thinking skills"),
]


# ===========================================================================
# FILLER PHRASE TEMPLATES FOR VARIATION ENGINE
# ===========================================================================

OPENERS = [
    "Can you please help me ", "Could you please explain ", "I would like to know ",
    "I need help with ", "I'm trying to understand ", "I want to learn about ",
    "Can you show me how to ", "I need assistance with ", "I'm wondering about ",
    "Could you provide guidance on ", "I'm having trouble with ", "I need to know ",
    "Could you walk me through ", "I'd appreciate help with ", "Can you clarify ",
    "I've been trying to figure out ", "I'm struggling to understand ",
    "Would you be able to explain ", "I need clarification on ", "Please help me understand ",
    "I'm curious about ", "I'm not sure how to ", "Can you give me advice on ",
    "I want to understand ", "I've been wondering about ", "Can you tell me about ",
]

CLOSERS = [
    " in detail", " with examples", " step by step", " as simply as possible",
    " for a beginner", " thoroughly", " with clear explanations",
    " and give me a comprehensive answer", " and provide some examples",
    " for my project", " for my research", " I'm completely new to this",
    " so I can understand it better", " that would be very helpful",
    "", "", "", "",  # empty endings for variety
]

MIDDLE_FILLERS = [
    "I'm not really sure about this but ", "I've heard about it but ",
    "I know a little about this but need more detail on ",
    "I've done some research but I still don't fully understand ",
    "", "", "", "", "", "",
]


# ===========================================================================
# TOPIC BANK - hundreds of (verbose_topic, concise_form) pairs
# ===========================================================================

TOPIC_PAIRS = [
    # Python
    ("write a function to find the factorial of a number using recursion", "Python recursive factorial"),
    ("implement a binary tree and traverse it in order", "Implement binary tree inorder traversal"),
    ("create a decorator that logs function execution time", "Python timing decorator"),
    ("build a simple web scraper using BeautifulSoup", "Web scraper with BeautifulSoup"),
    ("implement a linked list from scratch", "Implement linked list Python"),
    ("write a generator function that yields Fibonacci numbers", "Python Fibonacci generator"),
    ("use multiprocessing to speed up CPU-bound tasks", "Python multiprocessing CPU tasks"),
    ("create a context manager using the contextlib module", "Python contextlib context manager"),
    ("implement a LRU cache without using functools", "Implement LRU cache Python"),
    ("write a custom exception class hierarchy", "Python custom exception classes"),
    ("use dataclasses to model a business entity", "Python dataclasses example"),
    ("implement the observer pattern in Python", "Python observer pattern"),
    ("write async functions using asyncio", "Python asyncio async functions"),
    ("create a command line argument parser", "Python argparse CLI"),
    ("implement merge sort and explain its complexity", "Merge sort implementation Python"),
    ("build a simple REST client using the requests library", "Python REST client with requests"),
    ("write a script that monitors a directory for file changes", "Python directory file watcher"),
    ("implement a trie data structure", "Implement trie Python"),
    ("use SQLAlchemy ORM for database operations", "SQLAlchemy ORM operations"),
    ("write a type-annotated function with generics", "Python typed generic function"),

    # JavaScript / Web
    ("implement infinite scroll in a web page", "Implement infinite scroll"),
    ("create a custom React hook for fetching data", "React custom data fetching hook"),
    ("build a drag and drop interface with vanilla JS", "Vanilla JS drag and drop"),
    ("implement a virtual DOM from scratch", "Build virtual DOM"),
    ("create a service worker for offline caching", "Service worker offline cache"),
    ("write a TypeScript generic utility type", "TypeScript generic utility type"),
    ("implement lazy loading for images", "Implement image lazy loading"),
    ("build a real-time chat with WebSockets", "Real-time chat with WebSockets"),
    ("create a custom CSS animation library", "Build CSS animation library"),
    ("implement state management without Redux", "State management without Redux"),
    ("write a JavaScript proxy for validation", "JavaScript proxy validation"),
    ("build a PWA with offline support", "Build progressive web app"),
    ("implement authentication with JWT tokens", "JWT authentication implementation"),
    ("create a responsive grid system from scratch", "Build CSS grid system"),
    ("write a JavaScript module bundler concept", "Explain module bundler"),

    # Databases
    ("optimize a slow SQL query with indexes", "Optimize SQL query with indexes"),
    ("design a database schema for an e-commerce site", "E-commerce database schema"),
    ("implement database transactions with rollback", "Database transactions rollback"),
    ("write complex SQL joins with multiple tables", "Complex SQL multi-table joins"),
    ("implement full-text search in PostgreSQL", "PostgreSQL full-text search"),
    ("set up database replication for high availability", "Database replication setup"),
    ("partition a large database table for performance", "Database table partitioning"),
    ("implement a Redis caching layer", "Redis caching layer"),
    ("design a time-series database schema", "Time-series database design"),
    ("normalize a database to third normal form", "Database third normal form"),

    # Cloud / DevOps
    ("set up Kubernetes with horizontal pod autoscaling", "Kubernetes autoscaling setup"),
    ("create a Terraform configuration for AWS infrastructure", "Terraform AWS infrastructure"),
    ("implement a blue-green deployment strategy", "Blue-green deployment strategy"),
    ("configure Nginx as a reverse proxy with SSL", "Nginx reverse proxy with SSL"),
    ("set up centralized logging with the ELK stack", "ELK stack centralized logging"),
    ("implement infrastructure as code with Ansible", "Ansible infrastructure as code"),
    ("create a GitHub Actions CI pipeline", "GitHub Actions CI pipeline"),
    ("monitor application performance with Prometheus and Grafana", "Prometheus Grafana monitoring"),
    ("set up a serverless function on AWS Lambda", "AWS Lambda serverless function"),
    ("implement chaos engineering for resilience testing", "Chaos engineering resilience"),

    # Machine Learning / AI
    ("build a neural network from scratch using NumPy", "Neural network from scratch NumPy"),
    ("fine-tune a pre-trained BERT model for classification", "Fine-tune BERT classifier"),
    ("implement k-means clustering", "Implement k-means clustering"),
    ("explain the attention mechanism in transformers", "Explain transformer attention"),
    ("implement gradient descent from scratch", "Gradient descent from scratch"),
    ("evaluate a machine learning model properly", "Evaluate ML model correctly"),
    ("handle imbalanced datasets in classification", "Handle imbalanced dataset"),
    ("implement cross-validation correctly", "Implement cross-validation"),
    ("use feature engineering for tabular data", "Feature engineering tabular data"),
    ("deploy a machine learning model to production", "Deploy ML model to production"),
    ("implement reinforcement learning with Q-learning", "Q-learning reinforcement learning"),
    ("build a recommendation system using collaborative filtering", "Collaborative filtering recommender"),
    ("use transfer learning for image classification", "Transfer learning image classification"),
    ("explain SHAP values for model explainability", "Explain SHAP model explainability"),
    ("implement early stopping in model training", "Implement early stopping"),

    # Science
    ("explain how black holes form and what happens inside them", "How black holes form"),
    ("describe the process of stellar nucleosynthesis", "Explain stellar nucleosynthesis"),
    ("explain how mRNA vaccines work", "Explain mRNA vaccine mechanism"),
    ("describe the carbon cycle and human impact", "Carbon cycle and human impact"),
    ("explain how tectonic plates cause earthquakes", "Tectonic plates and earthquakes"),
    ("describe the process of nuclear fission in reactors", "Nuclear fission in reactors"),
    ("explain how the kidneys filter blood", "Kidney blood filtration"),
    ("describe how neurons transmit signals", "Neuron signal transmission"),
    ("explain the water cycle in detail", "Water cycle explanation"),
    ("describe how solar panels generate electricity", "Solar panel electricity generation"),
    ("explain the difference between viruses and bacteria", "Virus vs bacteria differences"),
    ("describe how antibiotics work and resistance develops", "Antibiotic mechanism and resistance"),
    ("explain how radio waves carry information", "Radio wave information transmission"),
    ("describe plate tectonics and continental drift", "Plate tectonics continental drift"),
    ("explain how the liver metabolizes alcohol", "Liver alcohol metabolism"),
    ("describe the stages of cell division", "Cell division stages"),
    ("explain how GPS satellites determine location", "GPS satellite location"),
    ("describe how the digestive system works", "Digestive system process"),
    ("explain climate feedback loops", "Climate feedback loops"),
    ("describe how stars fuse hydrogen into helium", "Stellar hydrogen fusion"),

    # History
    ("explain the causes of the French Revolution", "French Revolution causes"),
    ("describe the impact of the printing press on society", "Printing press societal impact"),
    ("explain how the Roman Empire fell", "Fall of Roman Empire causes"),
    ("describe the significance of the Magna Carta", "Magna Carta significance"),
    ("explain the causes of World War I", "World War I causes"),
    ("describe the Cold War and its major events", "Cold War overview"),
    ("explain the impact of the transatlantic slave trade", "Transatlantic slave trade impact"),
    ("describe the causes and effects of the Great Depression", "Great Depression causes and effects"),
    ("explain how the Renaissance changed Europe", "Renaissance impact on Europe"),
    ("describe the key events of the Civil Rights Movement", "Civil Rights Movement key events"),

    # Mathematics
    ("explain the concept of limits in calculus", "Calculus limits explained"),
    ("derive the quadratic formula from first principles", "Derive quadratic formula"),
    ("explain what eigenvalues and eigenvectors represent", "Eigenvalues eigenvectors explained"),
    ("prove that the square root of 2 is irrational", "Prove root 2 irrational"),
    ("explain Bayes theorem with examples", "Bayes theorem with examples"),
    ("describe the fundamental theorem of calculus", "Fundamental theorem of calculus"),
    ("explain how prime numbers are distributed", "Prime number distribution"),
    ("derive the formula for the sum of a geometric series", "Geometric series sum derivation"),
    ("explain what a Fourier transform does", "Fourier transform explained"),
    ("describe linear algebra applications in machine learning", "Linear algebra in ML"),

    # Health and Medicine
    ("explain how the immune system fights cancer", "Immune system vs cancer"),
    ("describe the difference between type 1 and type 2 diabetes", "Type 1 vs type 2 diabetes"),
    ("explain how statins reduce cholesterol", "Statin mechanism of action"),
    ("describe the stages of wound healing", "Wound healing stages"),
    ("explain how sleep affects brain health", "Sleep and brain health"),
    ("describe the role of gut bacteria in immunity", "Gut bacteria and immunity"),
    ("explain how stress affects the cardiovascular system", "Stress cardiovascular effects"),
    ("describe how antidepressants work", "Antidepressant mechanism"),
    ("explain the difference between aerobic and anaerobic exercise", "Aerobic vs anaerobic exercise"),
    ("describe how the blood-brain barrier works", "Blood-brain barrier function"),

    # Finance / Economics
    ("explain how compound interest works over time", "Compound interest explanation"),
    ("describe the difference between stocks and bonds", "Stocks vs bonds comparison"),
    ("explain what quantitative easing does to the economy", "Quantitative easing effects"),
    ("describe how to calculate net present value", "Net present value calculation"),
    ("explain the efficient market hypothesis", "Efficient market hypothesis"),
    ("describe how options pricing works", "Options pricing basics"),
    ("explain what causes inflation", "Inflation causes"),
    ("describe how central banks control interest rates", "Central bank interest rate control"),
    ("explain the difference between GDP and GNP", "GDP vs GNP differences"),
    ("describe how supply chain disruptions affect prices", "Supply chain price effects"),

    # Environment
    ("explain how ocean acidification affects marine life", "Ocean acidification effects"),
    ("describe the impact of microplastics on ecosystems", "Microplastics ecosystem impact"),
    ("explain how carbon capture technology works", "Carbon capture technology"),
    ("describe the process of soil degradation and remediation", "Soil degradation remediation"),
    ("explain how wind turbines generate electricity", "Wind turbine electricity generation"),
    ("describe the causes of deforestation and its effects", "Deforestation causes and effects"),
    ("explain how permafrost thawing affects the climate", "Permafrost thaw climate effects"),
    ("describe sustainable agriculture practices", "Sustainable agriculture practices"),
    ("explain what biodiversity loss means for ecosystems", "Biodiversity loss ecosystem effects"),
    ("describe how wastewater treatment plants work", "Wastewater treatment process"),

    # General knowledge
    ("explain how airplanes generate lift", "Airplane lift generation"),
    ("describe how the internet routes data packets", "Internet data packet routing"),
    ("explain how a refrigerator works", "Refrigerator working principle"),
    ("describe how 3D printing works", "3D printing process"),
    ("explain what causes jet lag", "Jet lag causes"),
    ("describe how touchscreens detect input", "Touchscreen detection technology"),
    ("explain how noise-canceling headphones work", "Noise-canceling headphone technology"),
    ("describe how a vaccine is developed and tested", "Vaccine development process"),
    ("explain how language models like GPT work", "GPT language model explained"),
    ("describe how blockchain consensus mechanisms work", "Blockchain consensus mechanisms"),

    # Writing and communication
    ("write a professional email declining a meeting", "Write meeting decline email"),
    ("write a resignation letter that is polite and professional", "Write professional resignation letter"),
    ("write a product description that converts", "Write converting product description"),
    ("write a LinkedIn summary that attracts recruiters", "Write LinkedIn recruiter summary"),
    ("write a cold outreach email for sales", "Write sales cold outreach email"),
    ("write a performance review for a team member", "Write team member performance review"),
    ("write a press release for a product launch", "Write product launch press release"),
    ("write a grant proposal introduction", "Write grant proposal intro"),
    ("write an abstract for a research paper", "Write research paper abstract"),
    ("write a project status update email", "Write project status email"),

    # Education
    ("explain how to study effectively for a math exam", "Effective math exam study tips"),
    ("describe active recall and spaced repetition techniques", "Active recall spaced repetition"),
    ("explain the Feynman technique for learning", "Feynman learning technique"),
    ("describe how to write a strong thesis statement", "Write strong thesis statement"),
    ("explain how to structure an argumentative essay", "Argumentative essay structure"),
    ("describe how to cite sources in APA format", "APA citation format"),
    ("explain how to solve word problems in algebra", "Solve algebra word problems"),
    ("describe effective reading strategies for dense texts", "Dense text reading strategies"),
    ("explain how to give an effective presentation", "Give effective presentation"),
    ("describe how to create a study schedule", "Create study schedule"),

    # Personal development
    ("explain how to build habits using the habit loop", "Build habits with habit loop"),
    ("describe cognitive behavioral therapy techniques for anxiety", "CBT techniques for anxiety"),
    ("explain how to develop emotional intelligence", "Develop emotional intelligence"),
    ("describe how to practice stoic philosophy daily", "Practice stoic philosophy"),
    ("explain the pomodoro technique for productivity", "Pomodoro productivity technique"),
    ("describe how to set SMART goals", "Set SMART goals"),
    ("explain how to practice active listening", "Practice active listening"),
    ("describe how to build a growth mindset", "Build growth mindset"),
    ("explain the concept of deep work and how to achieve it", "Deep work concept and practice"),
    ("describe how to recover from failure productively", "Recover from failure productively"),
    # ---- PASTE THESE INTO TOPIC_PAIRS (before the closing ]) ----

    # Advanced Python
    ("use Python's abstract base classes to enforce interfaces", "Python abstract base classes"),
    ("implement a thread pool executor in Python", "Python thread pool executor"),
    ("write a metaclass that auto-registers subclasses", "Python metaclass subclass registry"),
    ("use Python descriptors to create reusable validators", "Python descriptor validators"),
    ("build a plugin system using entry points", "Python plugin system entry points"),
    ("implement a rate limiter using a token bucket algorithm", "Python token bucket rate limiter"),
    ("use Python slots to reduce memory usage", "Python slots memory optimization"),
    ("write a custom iterator and iterable class", "Python custom iterator class"),
    ("implement copy-on-write semantics in Python", "Python copy-on-write"),
    ("use structural pattern matching in Python 3.10", "Python structural pattern matching"),
    ("implement a persistent queue using files", "Python persistent file queue"),
    ("write a simple interpreter for a tiny language", "Python simple interpreter"),
    ("use ctypes to call C code from Python", "Python ctypes C integration"),
    ("implement a publish-subscribe system in Python", "Python pub-sub system"),
    ("build a lazy evaluation system with generators", "Python lazy evaluation generators"),
    ("use Python's weakref module to avoid memory leaks", "Python weakref memory leaks"),
    ("implement a simple state machine in Python", "Python state machine"),
    ("write a decorator that retries on failure with backoff", "Python retry decorator backoff"),
    ("profile Python async code with asyncio debug mode", "Profile Python asyncio"),
    ("implement a binary protocol parser in Python", "Python binary protocol parser"),

    # Advanced JavaScript / TypeScript
    ("implement a reactive programming library from scratch", "Build reactive programming library"),
    ("write a TypeScript decorator for dependency injection", "TypeScript DI decorator"),
    ("build a custom event emitter in JavaScript", "JavaScript custom event emitter"),
    ("implement a finite state machine in TypeScript", "TypeScript finite state machine"),
    ("use JavaScript WeakMap for private class fields", "JavaScript WeakMap private fields"),
    ("build a simple compiler for a DSL in JavaScript", "JavaScript DSL compiler"),
    ("implement structural sharing for immutable data", "JavaScript structural sharing immutable"),
    ("write a virtual scrolling component from scratch", "Virtual scrolling component"),
    ("implement a custom Promise implementation", "Implement custom Promise"),
    ("build a micro-frontend architecture", "Micro-frontend architecture"),
    ("write a JavaScript memory profiler", "JavaScript memory profiler"),
    ("implement request deduplication in a fetch wrapper", "Fetch request deduplication"),
    ("build an undo/redo system with command pattern", "Undo redo command pattern"),
    ("implement a tree-shaking-friendly module system", "Tree-shaking module system"),
    ("write a streaming JSON parser in JavaScript", "Streaming JSON parser JavaScript"),

    # System Design
    ("design a URL shortener system at scale", "URL shortener system design"),
    ("design a rate limiting service for an API gateway", "API gateway rate limiter design"),
    ("design a distributed task scheduler", "Distributed task scheduler design"),
    ("design a real-time leaderboard system", "Real-time leaderboard design"),
    ("design a notification delivery system", "Notification system design"),
    ("design a search autocomplete system", "Search autocomplete system design"),
    ("design a photo sharing platform like Instagram", "Photo sharing platform design"),
    ("design a video streaming service architecture", "Video streaming architecture design"),
    ("design a ride-sharing matching system", "Ride-sharing matching system design"),
    ("design a distributed key-value store", "Distributed key-value store design"),
    ("design a content delivery network", "CDN design"),
    ("design a real-time collaborative editing system", "Collaborative editing system design"),
    ("design a recommendation engine for an e-commerce site", "E-commerce recommendation engine design"),
    ("design a webhook delivery system", "Webhook delivery system design"),
    ("design a multi-tenant SaaS architecture", "Multi-tenant SaaS architecture"),
    ("design a global chat application", "Global chat app system design"),
    ("design an event-driven microservices system", "Event-driven microservices design"),
    ("design an audit logging system", "Audit logging system design"),
    ("design a job queue with priority support", "Priority job queue design"),
    ("design a feature flag service", "Feature flag service design"),

    # Security
    ("implement CSRF protection in a web application", "Implement CSRF protection"),
    ("explain how timing attacks work and how to prevent them", "Timing attacks prevention"),
    ("implement secure password hashing with bcrypt", "Secure password hashing bcrypt"),
    ("explain how JWT token signing and verification works", "JWT token signing verification"),
    ("implement content security policy headers", "Content security policy headers"),
    ("explain how session fixation attacks work", "Session fixation attack"),
    ("implement rate limiting to prevent brute force attacks", "Rate limiting brute force prevention"),
    ("explain how man-in-the-middle attacks work", "Man-in-the-middle attack explained"),
    ("implement input sanitization to prevent XSS", "Input sanitization XSS prevention"),
    ("explain how privilege escalation attacks work", "Privilege escalation attacks"),
    ("implement secure file upload handling", "Secure file upload handling"),
    ("explain how DNS poisoning attacks work", "DNS poisoning attack"),
    ("implement secure cookie attributes", "Secure cookie configuration"),
    ("explain how subdomain takeover vulnerabilities work", "Subdomain takeover vulnerability"),
    ("implement API key rotation strategies", "API key rotation strategy"),

    # Networking
    ("explain how TCP three-way handshake works", "TCP three-way handshake"),
    ("describe what happens when you type a URL into a browser", "Browser URL request process"),
    ("explain how HTTP/2 differs from HTTP/1.1", "HTTP/2 vs HTTP/1.1"),
    ("describe how WebRTC peer-to-peer connections work", "WebRTC peer connection"),
    ("explain how DNS resolution works step by step", "DNS resolution steps"),
    ("describe how load balancers distribute traffic", "Load balancer traffic distribution"),
    ("explain the difference between TCP and UDP", "TCP vs UDP"),
    ("describe how a VPN tunnel works", "VPN tunnel explained"),
    ("explain how BGP routing works on the internet", "BGP routing explained"),
    ("describe how QUIC protocol improves on TCP", "QUIC protocol improvements"),
    ("explain how NAT works in home routers", "NAT router explained"),
    ("describe how HTTPS certificate validation works", "HTTPS certificate validation"),
    ("explain how anycast routing works for CDNs", "Anycast routing CDNs"),
    ("describe how socket programming works", "Socket programming basics"),
    ("explain how HTTP caching headers work", "HTTP caching headers"),

    # Operating Systems
    ("explain how virtual memory paging works", "Virtual memory paging"),
    ("describe how the Linux kernel schedules processes", "Linux process scheduling"),
    ("explain what system calls are and how they work", "System calls explained"),
    ("describe how file systems store data on disk", "File system data storage"),
    ("explain how inter-process communication works", "Inter-process communication"),
    ("describe what a context switch is", "Context switch explained"),
    ("explain how memory-mapped files work", "Memory-mapped files"),
    ("describe how Linux signals work", "Linux signals explained"),
    ("explain what a kernel panic is", "Kernel panic explained"),
    ("describe how copy-on-write fork works in Linux", "Linux fork copy-on-write"),
    ("explain how the inode system works in Linux", "Linux inode system"),
    ("describe how cgroups control resource usage", "Linux cgroups resource control"),
    ("explain how the OOM killer decides which process to kill", "Linux OOM killer"),
    ("describe how NUMA architecture affects performance", "NUMA architecture performance"),
    ("explain how CPU cache hierarchies work", "CPU cache hierarchy"),

    # Data Engineering
    ("design an ETL pipeline for a data warehouse", "ETL pipeline data warehouse"),
    ("explain how Apache Spark processes data in parallel", "Apache Spark parallel processing"),
    ("describe the differences between OLTP and OLAP databases", "OLTP vs OLAP databases"),
    ("explain how columnar storage formats like Parquet work", "Parquet columnar storage"),
    ("describe how data lake architectures work", "Data lake architecture"),
    ("explain how stream processing differs from batch processing", "Stream vs batch processing"),
    ("describe how Apache Flink processes streaming data", "Apache Flink streaming"),
    ("explain what a data mesh architecture is", "Data mesh architecture"),
    ("describe how to implement slowly changing dimensions", "Slowly changing dimensions"),
    ("explain how data lineage tracking works", "Data lineage tracking"),
    ("describe how to build a real-time analytics dashboard", "Real-time analytics dashboard"),
    ("explain what a lambda architecture is", "Lambda architecture explained"),
    ("describe how Airflow orchestrates data pipelines", "Airflow pipeline orchestration"),
    ("explain how data quality monitoring works", "Data quality monitoring"),
    ("describe how change data capture works", "Change data capture CDC"),

    # Advanced ML / AI
    ("explain how variational autoencoders work", "Variational autoencoder explained"),
    ("describe how GAN training works and why it's unstable", "GAN training instability"),
    ("explain how contrastive learning works for embeddings", "Contrastive learning embeddings"),
    ("describe how beam search decodes text in language models", "Beam search decoding"),
    ("explain how RLHF trains language models from feedback", "RLHF language model training"),
    ("describe how mixture of experts models work", "Mixture of experts model"),
    ("explain how sparse attention reduces transformer cost", "Sparse attention transformers"),
    ("describe how temperature and top-p sampling work", "LLM temperature top-p sampling"),
    ("explain how model distillation transfers knowledge", "Model distillation knowledge transfer"),
    ("describe how neural architecture search works", "Neural architecture search"),
    ("explain how active learning reduces labeling cost", "Active learning label efficiency"),
    ("describe how multi-task learning improves models", "Multi-task learning benefits"),
    ("explain how causal inference differs from correlation", "Causal inference vs correlation"),
    ("describe how synthetic data generation works", "Synthetic data generation"),
    ("explain how adversarial training improves robustness", "Adversarial training robustness"),
    ("describe how graph neural networks process relational data", "Graph neural networks"),
    ("explain how self-supervised learning works", "Self-supervised learning"),
    ("describe how online learning updates models in real time", "Online learning real-time updates"),
    ("explain how Bayesian optimization works for hyperparameters", "Bayesian hyperparameter optimization"),
    ("describe how conformal prediction gives coverage guarantees", "Conformal prediction guarantees"),

    # Physics
    ("explain how quantum entanglement works", "Quantum entanglement explained"),
    ("describe the standard model of particle physics", "Standard model particle physics"),
    ("explain how superconductivity works", "Superconductivity explained"),
    ("describe how lasers produce coherent light", "Laser light coherence"),
    ("explain how MRI machines use magnetic fields", "MRI machine magnetic fields"),
    ("describe what dark matter evidence exists", "Dark matter evidence"),
    ("explain how nuclear reactors control chain reactions", "Nuclear reactor chain reaction"),
    ("describe how particle accelerators work", "Particle accelerator operation"),
    ("explain what string theory proposes", "String theory explained"),
    ("describe how gravitational waves are detected", "Gravitational wave detection"),
    ("explain how semiconductors enable transistors", "Semiconductor transistors"),
    ("describe how plasma behaves differently from gas", "Plasma vs gas behavior"),
    ("explain what the Heisenberg uncertainty principle means", "Heisenberg uncertainty principle"),
    ("describe how the photoelectric effect works", "Photoelectric effect"),
    ("explain how Bose-Einstein condensates form", "Bose-Einstein condensate"),

    # Chemistry
    ("explain how catalysts speed up reactions without being consumed", "Catalyst reaction mechanism"),
    ("describe how electrochemical cells generate electricity", "Electrochemical cell electricity"),
    ("explain how polymers are synthesized", "Polymer synthesis"),
    ("describe the mechanism of acid-base reactions", "Acid-base reaction mechanism"),
    ("explain how chromatography separates compounds", "Chromatography separation"),
    ("describe how NMR spectroscopy identifies molecules", "NMR spectroscopy"),
    ("explain how enzyme kinetics work", "Enzyme kinetics"),
    ("describe what coordination chemistry involves", "Coordination chemistry basics"),
    ("explain how oxidation states are assigned", "Oxidation state assignment"),
    ("describe how thermodynamics predicts reaction spontaneity", "Thermodynamics reaction spontaneity"),

    # Biology
    ("explain how the cell cycle is regulated", "Cell cycle regulation"),
    ("describe how RNA splicing creates protein variants", "RNA splicing protein variants"),
    ("explain how epigenetic modifications affect gene expression", "Epigenetic gene expression"),
    ("describe how the nervous system develops in embryos", "Nervous system embryo development"),
    ("explain how the complement system fights pathogens", "Complement system immunity"),
    ("describe how cancer cells evade the immune system", "Cancer immune evasion"),
    ("explain how stem cells differentiate into tissues", "Stem cell differentiation"),
    ("describe how mitochondria produce ATP", "Mitochondria ATP production"),
    ("explain how protein folding determines function", "Protein folding function"),
    ("describe how viruses hijack cellular machinery", "Virus cell hijacking"),
    ("explain how natural selection drives evolution", "Natural selection evolution"),
    ("describe how the endocrine system uses hormones", "Endocrine hormone system"),
    ("explain how the synapse transmits chemical signals", "Synapse chemical signaling"),
    ("describe how CRISPR base editing works", "CRISPR base editing"),
    ("explain how antibiotic resistance spreads through populations", "Antibiotic resistance spread"),

    # Economics
    ("explain how game theory models strategic decisions", "Game theory strategic decisions"),
    ("describe how auction mechanisms work", "Auction mechanism design"),
    ("explain the prisoner's dilemma and its implications", "Prisoner's dilemma explained"),
    ("describe how public goods problems lead to market failure", "Public goods market failure"),
    ("explain how externalities are corrected by policy", "Externalities policy correction"),
    ("describe how price discrimination works", "Price discrimination economics"),
    ("explain how network effects create winner-take-all markets", "Network effects winner-take-all"),
    ("describe how behavioral economics differs from classical theory", "Behavioral vs classical economics"),
    ("explain how monetary policy affects aggregate demand", "Monetary policy aggregate demand"),
    ("describe how fiscal multipliers work during recessions", "Fiscal multiplier recessions"),
    ("explain how trade deficits affect exchange rates", "Trade deficit exchange rates"),
    ("describe how minimum wage affects employment", "Minimum wage employment effects"),
    ("explain how comparative advantage drives trade", "Comparative advantage trade"),
    ("describe how oligopolies maintain pricing power", "Oligopoly pricing power"),
    ("explain how central bank independence affects inflation", "Central bank independence inflation"),

    # Philosophy
    ("explain the problem of personal identity over time", "Personal identity problem"),
    ("describe the trolley problem and its ethical implications", "Trolley problem ethics"),
    ("explain what the Chinese room argument says about AI", "Chinese room AI argument"),
    ("describe the difference between utilitarianism and deontology", "Utilitarianism vs deontology"),
    ("explain what Plato's allegory of the cave means", "Plato's cave allegory"),
    ("describe what Kant's categorical imperative says", "Kant categorical imperative"),
    ("explain what existentialism says about human freedom", "Existentialism human freedom"),
    ("describe the hard problem of consciousness", "Hard problem of consciousness"),
    ("explain what the simulation hypothesis argues", "Simulation hypothesis"),
    ("describe what epistemological skepticism challenges", "Epistemological skepticism"),

    # Law and Policy
    ("explain how intellectual property law protects software", "Software intellectual property law"),
    ("describe how GDPR affects data processing practices", "GDPR data processing requirements"),
    ("explain how antitrust law applies to tech monopolies", "Antitrust law tech monopolies"),
    ("describe what net neutrality means for internet providers", "Net neutrality explained"),
    ("explain how patents differ from trade secrets", "Patents vs trade secrets"),
    ("describe how constitutional law limits government power", "Constitutional limits on government"),
    ("explain what liability means for AI-generated content", "AI content liability"),
    ("describe how open source licenses differ from each other", "Open source license differences"),
    ("explain how data localization laws affect cloud services", "Data localization cloud services"),
    ("describe how content moderation law works", "Content moderation law"),

    # Sociology and Psychology
    ("explain how social identity theory works", "Social identity theory"),
    ("describe what conformity experiments revealed about behavior", "Conformity experiment findings"),
    ("explain how cognitive dissonance affects decision-making", "Cognitive dissonance decisions"),
    ("describe how attachment styles affect adult relationships", "Attachment styles adult relationships"),
    ("explain what the Milgram experiments showed", "Milgram experiment findings"),
    ("describe how confirmation bias distorts reasoning", "Confirmation bias reasoning"),
    ("explain what the bystander effect is", "Bystander effect explained"),
    ("describe how implicit bias affects judgment", "Implicit bias judgment"),
    ("explain how operant conditioning shapes behavior", "Operant conditioning behavior"),
    ("describe what flow state is and how to achieve it", "Flow state achievement"),
    ("explain how social media affects adolescent mental health", "Social media teen mental health"),
    ("describe how groupthink leads to poor decisions", "Groupthink poor decisions"),
    ("explain what motivated reasoning is", "Motivated reasoning explained"),
    ("describe how trauma affects the nervous system", "Trauma nervous system effects"),
    ("explain how positive psychology differs from traditional therapy", "Positive psychology vs therapy"),

    # Climate and Energy
    ("explain how carbon pricing mechanisms work", "Carbon pricing mechanisms"),
    ("describe how smart grids manage electricity demand", "Smart grid demand management"),
    ("explain how green hydrogen is produced and used", "Green hydrogen production use"),
    ("describe how geothermal energy is harnessed", "Geothermal energy harnessing"),
    ("explain how tidal energy generation works", "Tidal energy generation"),
    ("describe how energy storage technologies compare", "Energy storage technology comparison"),
    ("explain how the social cost of carbon is calculated", "Social cost of carbon calculation"),
    ("describe how net-zero commitments are measured", "Net-zero commitment measurement"),
    ("explain how adaptation differs from mitigation in climate policy", "Climate adaptation vs mitigation"),
    ("describe how urban heat islands form and can be reduced", "Urban heat island reduction"),

    # Space and Astronomy
    ("explain how rockets achieve orbital velocity", "Rocket orbital velocity"),
    ("describe how space telescopes differ from ground telescopes", "Space vs ground telescopes"),
    ("explain how the James Webb Telescope sees the early universe", "James Webb Telescope early universe"),
    ("describe how exoplanets are detected", "Exoplanet detection methods"),
    ("explain how orbital mechanics govern satellite paths", "Orbital mechanics satellites"),
    ("describe how solar wind affects Earth's magnetosphere", "Solar wind magnetosphere effects"),
    ("explain how neutron stars differ from black holes", "Neutron stars vs black holes"),
    ("describe how SpaceX reuses rocket boosters", "SpaceX rocket reuse"),
    ("explain what the cosmic microwave background reveals", "Cosmic microwave background"),
    ("describe how dark energy drives the universe's expansion", "Dark energy universe expansion"),

    # Mathematics (advanced)
    ("explain what the Riemann hypothesis proposes", "Riemann hypothesis explained"),
    ("describe how topology studies shape properties", "Topology shape properties"),
    ("explain how group theory abstracts symmetry", "Group theory symmetry"),
    ("describe what P vs NP means in complexity theory", "P vs NP complexity"),
    ("explain how the Monte Carlo method estimates values", "Monte Carlo method"),
    ("describe how differential equations model real systems", "Differential equations real systems"),
    ("explain what information entropy measures", "Information entropy"),
    ("describe how graph theory solves network problems", "Graph theory network problems"),
    ("explain what the central limit theorem says", "Central limit theorem"),
    ("describe how Gödel's incompleteness theorems work", "Gödel incompleteness theorems"),
    ("explain what a Markov chain models", "Markov chain model"),
    ("describe how linear programming optimizes decisions", "Linear programming optimization"),
    ("explain what complex numbers represent geometrically", "Complex numbers geometry"),
    ("describe how the fast Fourier transform works", "Fast Fourier transform"),
    ("explain what a fixed point theorem says", "Fixed point theorem"),
    # ---- PASTE THESE INTO EXTRA_PAIRS (before the closing ]) ----

    # Advanced Python debugging / tooling
    ("How do I use Python's tracemalloc to find memory leaks?", "Python tracemalloc memory leaks"),
    ("Can you explain how to use pdb to debug a Python script interactively?", "Python pdb interactive debugging"),
    ("I want to understand how Python's garbage collector handles circular references", "Python circular reference garbage collection"),
    ("How do I use mypy to add type checking to my Python project?", "Python mypy type checking"),
    ("Can you explain how to write a C extension for Python?", "Python C extension writing"),
    ("I need to understand how to use multiprocessing shared memory", "Python multiprocessing shared memory"),
    ("How do I serialize Python objects with pickle safely?", "Python pickle safe serialization"),
    ("Can you explain how Python's import system finds modules?", "Python module import system"),
    ("I want to understand how to use Python's logging module properly", "Python logging module setup"),
    ("How do I measure code coverage in Python tests?", "Python test code coverage"),
    ("Can you explain what __slots__ does in Python classes?", "Python __slots__ explained"),
    ("I need to understand how to use Python's functools module", "Python functools module"),
    ("How do I implement lazy properties in Python?", "Python lazy property implementation"),
    ("Can you explain how Python's defaultdict works?", "Python defaultdict explained"),
    ("I want to know how to write Python code that is backward compatible", "Python backward compatibility"),

    # JavaScript ecosystem
    ("How do I set up ESLint and Prettier for a JavaScript project?", "Set up ESLint Prettier JavaScript"),
    ("Can you explain how Webpack bundles JavaScript modules?", "Webpack bundling explained"),
    ("I want to understand how Vite is faster than Webpack", "Vite vs Webpack speed"),
    ("How do I implement code splitting in a React application?", "React code splitting"),
    ("Can you explain what tree shaking does in a bundler?", "Tree shaking explained"),
    ("I need to understand how React's reconciliation algorithm works", "React reconciliation algorithm"),
    ("How do I prevent memory leaks in React components?", "React memory leak prevention"),
    ("Can you explain the difference between useEffect and useLayoutEffect?", "useEffect vs useLayoutEffect"),
    ("I want to understand how React context causes re-renders", "React context re-renders"),
    ("How do I implement optimistic updates in a React app?", "React optimistic updates"),
    ("Can you explain how Zustand manages state differently from Redux?", "Zustand vs Redux state"),
    ("I need to understand how Next.js server components work", "Next.js server components"),
    ("How does Next.js handle incremental static regeneration?", "Next.js incremental static regeneration"),
    ("Can you explain what React Server Components change about data fetching?", "React Server Components data fetching"),
    ("I want to understand how SolidJS achieves fine-grained reactivity", "SolidJS fine-grained reactivity"),

    # Databases (advanced)
    ("How do I implement optimistic concurrency control in PostgreSQL?", "PostgreSQL optimistic concurrency"),
    ("Can you explain what MVCC is and how PostgreSQL implements it?", "PostgreSQL MVCC explained"),
    ("I need to understand how to tune PostgreSQL for write-heavy workloads", "PostgreSQL write optimization"),
    ("How do I use EXPLAIN ANALYZE to optimize a query?", "PostgreSQL EXPLAIN ANALYZE"),
    ("Can you explain what connection pooling does for database performance?", "Database connection pooling"),
    ("I want to understand how MongoDB handles transactions", "MongoDB transactions"),
    ("How does Cassandra achieve high write throughput?", "Cassandra write throughput"),
    ("Can you explain how ClickHouse is optimized for analytics?", "ClickHouse analytics optimization"),
    ("I need to understand how vector databases store embeddings", "Vector database embeddings"),
    ("How do I choose between Redis and Memcached for caching?", "Redis vs Memcached caching"),
    ("Can you explain how DynamoDB partitioning works?", "DynamoDB partitioning"),
    ("I want to understand how to model a graph in a relational database", "Graph modeling relational database"),
    ("How do I implement audit trails in a database?", "Database audit trail implementation"),
    ("Can you explain what write-ahead logging does?", "Write-ahead logging explained"),
    ("I need to understand how database sharding splits data", "Database sharding explained"),

    # DevOps / Infrastructure
    ("How do I set up a Kubernetes ingress controller with SSL?", "Kubernetes ingress SSL setup"),
    ("Can you explain how Kubernetes handles pod autoscaling?", "Kubernetes pod autoscaling"),
    ("I want to understand how Helm charts organize Kubernetes deployments", "Helm chart Kubernetes deployment"),
    ("How do I implement GitOps with ArgoCD?", "GitOps ArgoCD implementation"),
    ("Can you explain how service meshes like Istio work?", "Istio service mesh explained"),
    ("I need to understand how to write a Dockerfile efficiently", "Efficient Dockerfile writing"),
    ("How do I reduce Docker image size?", "Reduce Docker image size"),
    ("Can you explain how multi-stage Docker builds work?", "Docker multi-stage build"),
    ("I want to understand how Terraform state management works", "Terraform state management"),
    ("How do I implement secrets management in Kubernetes?", "Kubernetes secrets management"),
    ("Can you explain how AWS IAM roles and policies work?", "AWS IAM roles policies"),
    ("I need to understand how to cost-optimize my AWS usage", "AWS cost optimization"),
    ("How do I set up cross-account AWS access?", "AWS cross-account access"),
    ("Can you explain how AWS VPC networking works?", "AWS VPC networking"),
    ("I want to understand how to implement disaster recovery in the cloud", "Cloud disaster recovery"),

    # AI / ML practical
    ("How do I handle class imbalance with SMOTE?", "Handle class imbalance SMOTE"),
    ("Can you explain how to interpret a confusion matrix?", "Confusion matrix interpretation"),
    ("I want to understand how to detect data drift in production", "Detect production data drift"),
    ("How do I implement A/B testing for ML models?", "A/B testing ML models"),
    ("Can you explain what feature stores are and why they matter?", "Feature store explained"),
    ("I need to understand how to monitor ML models in production", "ML model production monitoring"),
    ("How do I version ML experiments with MLflow?", "MLflow experiment versioning"),
    ("Can you explain how to reduce inference latency for a model?", "Reduce ML inference latency"),
    ("I want to understand how to use ONNX for model deployment", "ONNX model deployment"),
    ("How do I build a training pipeline with Kubeflow?", "Kubeflow training pipeline"),
    ("Can you explain how to use Weights & Biases for experiment tracking?", "Weights Biases experiment tracking"),
    ("I need to understand how to benchmark model inference speed", "Benchmark model inference speed"),
    ("How do I implement model ensembling effectively?", "Model ensembling techniques"),
    ("Can you explain how isotonic regression calibrates probabilities?", "Isotonic regression calibration"),
    ("I want to understand how to build a text-to-SQL system", "Text-to-SQL system building"),
    ("How do I implement entity resolution across datasets?", "Entity resolution datasets"),
    ("Can you explain how to build a knowledge graph?", "Knowledge graph construction"),
    ("I need to understand how to use LangChain for LLM applications", "LangChain LLM application"),
    ("How do I implement streaming responses from a language model?", "LLM streaming response"),
    ("Can you explain how to evaluate RAG system quality?", "RAG system quality evaluation"),

    # Green AI / Sustainability in tech
    ("How do I measure the energy consumption of a Python script?", "Measure Python energy consumption"),
    ("Can you explain what carbon-aware computing means?", "Carbon-aware computing explained"),
    ("I want to understand how to reduce the energy cost of model training", "Reduce model training energy"),
    ("How does model pruning reduce computational cost?", "Model pruning computation reduction"),
    ("Can you explain how dynamic quantization works at inference time?", "Dynamic quantization inference"),
    ("I need to understand how to route AI requests to greener data centers", "Green data center AI routing"),
    ("How do I estimate the carbon cost of a machine learning job?", "Estimate ML job carbon cost"),
    ("Can you explain what the Green Software Foundation recommends?", "Green Software Foundation practices"),
    ("I want to understand how inference batching reduces energy use", "Inference batching energy savings"),
    ("How does early exit in neural networks save computation?", "Neural network early exit"),
    ("Can you explain what carbon intensity of electricity means?", "Electricity carbon intensity"),
    ("I need to understand how time-shifting workloads reduces emissions", "Time-shift workloads emissions"),
    ("How do I implement a carbon dashboard for my application?", "Application carbon dashboard"),
    ("Can you explain how to benchmark AI energy efficiency?", "AI energy efficiency benchmark"),
    ("I want to understand how small language models compare to large ones on energy", "Small vs large LLM energy"),

    # Career and professional
    ("How do I negotiate equity in a startup offer?", "Negotiate startup equity"),
    ("Can you explain what a staff engineer does differently from a senior engineer?", "Staff vs senior engineer role"),
    ("I want to understand how to transition from engineering to product management", "Engineering to product management transition"),
    ("How do I build a portfolio as a self-taught developer?", "Self-taught developer portfolio"),
    ("Can you explain what the STAR interview method is?", "STAR interview method"),
    ("I need to understand how to prepare for a system design interview", "System design interview prep"),
    ("How do I get my first open source contribution merged?", "First open source contribution"),
    ("Can you explain how to write a strong technical blog post?", "Write technical blog post"),
    ("I want to understand how to build credibility as a new engineer", "Build new engineer credibility"),
    ("How do I handle performance improvement plans at work?", "Handle performance improvement plan"),
    ("Can you explain how to manage up effectively?", "Manage up at work"),
    ("I need to understand how to lead a project without formal authority", "Lead project without authority"),
    ("How do I give a good code review that my colleagues appreciate?", "Give good code review"),
    ("Can you explain how to write a good engineering design document?", "Write engineering design document"),
    ("I want to understand how to set career goals as a software engineer", "Software engineer career goals"),

    # Writing and content creation
    ("How do I write an op-ed that gets published?", "Write publishable op-ed"),
    ("Can you explain the inverted pyramid style for news writing?", "Inverted pyramid news writing"),
    ("I want to understand how to write a technical README that developers love", "Write great technical README"),
    ("How do I structure a case study for a business audience?", "Business case study structure"),
    ("Can you explain how to write API documentation that is easy to use?", "Write good API documentation"),
    ("I need to understand how to write a compelling crowdfunding campaign", "Write crowdfunding campaign"),
    ("How do I write a white paper for a technical audience?", "Write technical white paper"),
    ("Can you explain how to write a persuasive research proposal?", "Write persuasive research proposal"),
    ("I want to understand how to improve my scientific writing style", "Improve scientific writing"),
    ("How do I write a business requirements document?", "Write business requirements document"),
    ("Can you explain how to write for an international audience?", "Write for international audience"),
    ("I need to understand how to write effective error messages in software", "Write effective error messages"),
    ("How do I write a postmortem after an incident?", "Write incident postmortem"),
    ("Can you explain how to write a convincing product one-pager?", "Write product one-pager"),
    ("I want to understand how to write user-facing release notes", "Write user release notes"),

    # Education and learning science
    ("How do I apply spaced repetition with Anki effectively?", "Spaced repetition with Anki"),
    ("Can you explain how interleaved practice improves retention?", "Interleaved practice retention"),
    ("I want to understand how retrieval practice differs from rereading", "Retrieval practice vs rereading"),
    ("How do I create effective flashcards for complex topics?", "Create effective flashcards"),
    ("Can you explain how worked examples help beginners learn?", "Worked examples beginner learning"),
    ("I need to understand how cognitive load theory affects instructional design", "Cognitive load instructional design"),
    ("How do I write learning objectives that are measurable?", "Measurable learning objectives"),
    ("Can you explain how to use the Cornell note-taking method?", "Cornell note-taking method"),
    ("I want to understand how to prepare for oral exams", "Oral exam preparation"),
    ("How do I apply deliberate practice to learn a new skill?", "Deliberate practice skill learning"),

    # Personal finance (deeper)
    ("How do I evaluate whether to pay off debt or invest?", "Pay off debt vs invest decision"),
    ("Can you explain how to read a mutual fund prospectus?", "Read mutual fund prospectus"),
    ("I want to understand how rebalancing a portfolio works", "Portfolio rebalancing"),
    ("How do I calculate how much I need for retirement?", "Retirement savings calculation"),
    ("Can you explain what sequence of returns risk means?", "Sequence of returns risk"),
    ("I need to understand how to use a health savings account optimally", "HSA optimal use"),
    ("How do I evaluate stock options when joining a company?", "Evaluate stock options offer"),
    ("Can you explain how bond duration affects interest rate risk?", "Bond duration interest rate risk"),
    ("I want to understand how to build an emergency fund strategy", "Emergency fund strategy"),
    ("How do I reduce my tax burden through legal tax planning?", "Legal tax reduction planning"),
    ("Can you explain what a backdoor Roth IRA is?", "Backdoor Roth IRA explained"),
    ("I need to understand how estate planning works", "Estate planning basics"),
    ("How do I evaluate whether to lease or buy a car financially?", "Lease vs buy car financial"),
    ("Can you explain what umbrella insurance covers?", "Umbrella insurance coverage"),
    ("I want to understand how to think about insurance as risk management", "Insurance risk management"),

    # Health and fitness (deeper)
    ("How do I design a progressive overload strength training program?", "Progressive overload strength program"),
    ("Can you explain what VO2 max is and how to improve it?", "VO2 max improvement"),
    ("I want to understand how periodization works in athletic training", "Periodization athletic training"),
    ("How does resistance training affect bone density?", "Resistance training bone density"),
    ("Can you explain what heart rate zones mean for training?", "Heart rate zones training"),
    ("I need to understand how creatine supplementation works", "Creatine supplementation science"),
    ("How do I optimize nutrition timing around workouts?", "Nutrition timing workouts"),
    ("Can you explain how sleep deprivation affects athletic performance?", "Sleep deprivation athletic performance"),
    ("I want to understand how to safely increase running mileage", "Safe running mileage increase"),
    ("How does foam rolling help with muscle recovery?", "Foam rolling muscle recovery"),
    ("Can you explain what NEAT is and how it affects weight management?", "NEAT weight management"),
    ("I need to understand how to prevent common overuse injuries", "Prevent overuse injuries"),
    ("How do I read a nutrition label accurately?", "Read nutrition label accurately"),
    ("Can you explain the difference between hunger and appetite?", "Hunger vs appetite difference"),
    ("I want to understand how the gut microbiome affects overall health", "Gut microbiome health effects"),

    # Entrepreneurship and startups
    ("How do I validate a startup idea before building anything?", "Validate startup idea early"),
    ("Can you explain how to build an MVP effectively?", "Build effective MVP"),
    ("I want to understand how venture capital funding rounds work", "VC funding rounds explained"),
    ("How do I calculate runway and burn rate for my startup?", "Startup runway burn rate"),
    ("Can you explain how to structure a co-founder agreement?", "Co-founder agreement structure"),
    ("I need to understand how to price a SaaS product", "SaaS product pricing"),
    ("How do I find my first 10 customers for a B2B startup?", "Find first B2B customers"),
    ("Can you explain what a term sheet includes?", "Term sheet explained"),
    ("I want to understand how to build a sales funnel from scratch", "Build sales funnel"),
    ("How do I decide when to pivot my startup?", "When to pivot startup"),
    ("Can you explain how to build a moat for a software company?", "Software company competitive moat"),
    ("I need to understand how to write a fundraising pitch deck", "Write fundraising pitch deck"),
    ("How do I set up equity vesting schedules for employees?", "Employee equity vesting schedules"),
    ("Can you explain how product-led growth works?", "Product-led growth explained"),
    ("I want to understand how to build a community around a product", "Build product community"),

    # Communication and soft skills
    ("How do I structure a presentation that persuades executives?", "Persuasive executive presentation"),
    ("Can you explain the pyramid principle for business communication?", "Pyramid principle communication"),
    ("I want to understand how to write better Slack messages at work", "Write better Slack messages"),
    ("How do I run a productive one-on-one meeting?", "Run productive one-on-one"),
    ("Can you explain how to facilitate a brainstorming session?", "Facilitate brainstorming session"),
    ("I need to understand how to give a feedback that actually changes behavior", "Give behavior-changing feedback"),
    ("How do I say no to requests without damaging relationships?", "Say no professionally"),
    ("Can you explain how to communicate bad news to stakeholders?", "Communicate bad news stakeholders"),
    ("I want to understand how to build influence without authority", "Build influence without authority"),
    ("How do I prepare for a difficult conversation at work?", "Prepare difficult work conversation"),

    # Cooking / Food science
    ("Can you explain how the Maillard reaction creates flavor in cooked food?", "Maillard reaction flavor"),
    ("How does gluten develop in bread dough?", "Gluten bread dough development"),
    ("I want to understand how fermentation preserves food", "Fermentation food preservation"),
    ("Can you explain how emulsification works in cooking?", "Emulsification in cooking"),
    ("How does brining make meat juicier?", "Brining meat juiciness"),
    ("I need to understand how to balance flavors in a dish", "Balance flavors cooking"),
    ("How does temperature affect chocolate tempering?", "Chocolate tempering temperature"),
    ("Can you explain how sous vide cooking works?", "Sous vide cooking explained"),
    ("I want to understand how to make a roux and use it properly", "Roux cooking technique"),
    ("How do I build umami flavor in a dish without meat?", "Umami flavor without meat"),

    # Travel and geography
    ("How do I plan a multi-country trip on a budget?", "Budget multi-country trip planning"),
    ("Can you explain how to use travel credit card points effectively?", "Travel credit card points strategy"),
    ("I want to understand how time zones affect international travel planning", "Time zones travel planning"),
    ("How do I stay safe when traveling solo in unfamiliar countries?", "Solo travel safety"),
    ("Can you explain how to pack efficiently for a long trip?", "Efficient long trip packing"),
    ("I need to understand how travel insurance works", "Travel insurance explained"),
    ("How do I find authentic local experiences when traveling?", "Find authentic travel experiences"),
    ("Can you explain what slow travel means and its benefits?", "Slow travel benefits"),
    ("I want to understand how to navigate a new city efficiently", "Navigate new city efficiently"),
    ("How do I deal with jet lag when crossing many time zones?", "Deal with severe jet lag"),

    # Parenting and child development
    ("How do I encourage a growth mindset in my child?", "Encourage child growth mindset"),
    ("Can you explain how authoritative parenting differs from authoritarian?", "Authoritative vs authoritarian parenting"),
    ("I want to understand how screen time affects child development", "Screen time child development"),
    ("How do I help my child develop emotional regulation skills?", "Child emotional regulation skills"),
    ("Can you explain how to talk to children about difficult topics?", "Talk to children difficult topics"),
    ("I need to understand how to support a child with learning differences", "Support child learning differences"),
    ("How do I set healthy boundaries with my teenager?", "Healthy teenager boundaries"),
    ("Can you explain how play-based learning works?", "Play-based learning explained"),
    ("I want to understand how to raise financially literate children", "Raise financially literate children"),
    ("How do I build a strong reading habit in young children?", "Build child reading habit"),

    # Language learning
    ("How do I reach conversational fluency faster in a new language?", "Reach conversational fluency faster"),
    ("Can you explain how comprehensible input theory works?", "Comprehensible input theory"),
    ("I want to understand how to maintain multiple languages simultaneously", "Maintain multiple languages"),
    ("How do I overcome the intermediate plateau in language learning?", "Overcome language intermediate plateau"),
    ("Can you explain how shadowing technique improves pronunciation?", "Language shadowing pronunciation"),
    ("I need to understand how immersion environments accelerate learning", "Immersion language acceleration"),
    ("How do I learn vocabulary efficiently with context sentences?", "Learn vocabulary with context"),
    ("Can you explain how tonal languages differ from non-tonal ones?", "Tonal vs non-tonal languages"),
    ("I want to understand how grammar should be studied in language learning", "Grammar study language learning"),
    ("How do I find language exchange partners online?", "Find language exchange partners"),

    # Miscellaneous practical skills
    ("How do I negotiate a lower price when buying a car?", "Negotiate car purchase price"),
    ("Can you explain how to read a contract before signing it?", "Read contract before signing"),
    ("I want to understand how home equity loans work", "Home equity loan explained"),
    ("How do I evaluate a job offer beyond just the salary?", "Evaluate job offer fully"),
    ("Can you explain how to write an appeal letter effectively?", "Write effective appeal letter"),
    ("I need to understand how to build a good credit score", "Build good credit score"),
    ("How do I dispute an error on my credit report?", "Dispute credit report error"),
    ("Can you explain how to prepare financially for having children?", "Financial preparation for children"),
    ("I want to understand how to research a neighborhood before moving", "Research neighborhood before moving"),
    ("How do I organize important documents in case of emergency?", "Organize emergency documents"),
]


# ===========================================================================
# VARIATION ENGINE
# ===========================================================================

def make_verbose(clean_topic: str) -> str:
    """Wrap a clean topic in verbose filler language."""
    opener = random.choice(OPENERS)
    closer = random.choice(CLOSERS)
    filler = random.choice(MIDDLE_FILLERS)

    # Pick a random sentence template
    templates = [
        f"{opener}{filler}{clean_topic}{closer}?",
        f"{opener}{clean_topic}{closer}?",
        f"I have a question about {clean_topic}. {opener}explain this to me{closer}?",
        f"I'm currently working on a project and I need to understand {clean_topic}. Can you help me{closer}?",
        f"For my studies, I need to learn about {clean_topic}. {opener}explain{closer}?",
        f"I've been trying to learn about {clean_topic} for a while and {opener}clarify{closer}?",
        f"I really need your help with {clean_topic}{closer}.",
        f"My question is about {clean_topic}. {opener}give a detailed explanation{closer}?",
    ]
    return random.choice(templates)


def add_noise_words(text: str) -> str:
    """Insert a few filler words into a verbose prompt."""
    inserts = [
        ("please", 0.4), ("kindly", 0.2), ("really", 0.3),
        ("very much", 0.2), ("actually", 0.25), ("honestly", 0.15),
    ]
    words = text.split()
    for word, prob in inserts:
        if random.random() < prob and word not in text.lower():
            pos = random.randint(0, min(5, len(words)))
            words.insert(pos, word)
    return " ".join(words)


def generate_pairs_from_topics() -> list:
    """Generate verbose/clean pairs from the topic bank."""
    pairs = []
    for verbose_topic, clean_topic in TOPIC_PAIRS:
        # Generate multiple variations per topic
        for _ in range(8):
            verbose = make_verbose(verbose_topic)
            verbose = add_noise_words(verbose)
            pairs.append({"original": verbose, "optimized": clean_topic})

        # Also add a direct pair with the original verbose topic
        pairs.append({"original": verbose_topic.capitalize() + "?", "optimized": clean_topic})
    return pairs


def expand_base_pairs(base: list) -> list:
    """Add variations of the original 127 hand-crafted pairs."""
    expanded = []
    for orig, opt in base:
        # Keep the original
        expanded.append({"original": orig, "optimized": opt})
        # Add noisy variation
        for _ in range(4):
            noisy = add_noise_words(orig)
            expanded.append({"original": noisy, "optimized": opt})
        # Add a templated rephrasing
        templates = [
            f"I have a question: {orig}",
            f"Quick question - {orig.lower()}",
            f"Hey, {orig.lower()}",
            f"Hi there, {orig.lower()}",
        ]
        expanded.append({"original": random.choice(templates), "optimized": opt})
    return expanded


# ===========================================================================
# ADDITIONAL HARD-CODED DOMAIN-SPECIFIC PAIRS (500 extra unique ones)
# ===========================================================================

EXTRA_PAIRS = [
    ("Could you walk me through the process of setting up a virtual environment in Python from scratch?", "Set up Python virtual environment"),
    ("I've been trying to figure out how to use the map function in Python but I'm not quite getting it", "Use Python map function"),
    ("Can you please explain what the difference between a shallow copy and a deep copy is?", "Shallow copy vs deep copy"),
    ("I want to know how to profile memory usage in my Python application", "Profile Python memory usage"),
    ("I need help understanding why my Python script is running out of memory", "Debug Python memory issues"),
    ("Can you show me how to implement dependency injection in Python?", "Python dependency injection"),
    ("I'm struggling with understanding how to implement a graph and run BFS and DFS on it", "Implement graph BFS DFS"),
    ("What is the difference between a process and a thread?", "Process vs thread difference"),
    ("Can you explain what race conditions are and how to prevent them?", "Explain race conditions prevention"),
    ("I want to understand how garbage collection works in Python", "Python garbage collection"),
    ("How do I implement a priority queue efficiently?", "Implement priority queue"),
    ("Can you explain what monads are in functional programming?", "Explain monads functional programming"),
    ("I need to understand how to write thread-safe code", "Write thread-safe code"),
    ("What is the difference between concurrency and parallelism?", "Concurrency vs parallelism"),
    ("How do I implement event-driven programming?", "Event-driven programming"),
    ("Can you explain the SOLID principles with examples?", "SOLID principles with examples"),
    ("I want to learn how to write better unit tests", "Write better unit tests"),
    ("How do I mock external dependencies in tests?", "Mock external test dependencies"),
    ("What is test-driven development and how do I practice it?", "Test-driven development practice"),
    ("Can you explain what dependency inversion means?", "Explain dependency inversion"),
    ("How do I implement the factory pattern?", "Implement factory pattern"),
    ("What is the difference between composition and inheritance?", "Composition vs inheritance"),
    ("Can you explain what CORS is and how to fix CORS errors?", "CORS explained and fixed"),
    ("How do I implement pagination in a REST API?", "Implement REST API pagination"),
    ("What is the N+1 query problem and how do I fix it?", "Fix N+1 query problem"),
    ("Can you explain how database indexes work internally?", "Database index internals"),
    ("How do I implement optimistic locking in a database?", "Database optimistic locking"),
    ("What is eventual consistency in distributed systems?", "Eventual consistency explained"),
    ("Can you explain the CAP theorem?", "CAP theorem explained"),
    ("How do I implement a distributed cache?", "Implement distributed cache"),
    ("What is a message queue and when should I use one?", "Message queue use cases"),
    ("Can you explain how Kafka works?", "Apache Kafka explained"),
    ("How do I handle distributed transactions?", "Distributed transaction handling"),
    ("What is the saga pattern for microservices?", "Saga pattern microservices"),
    ("Can you explain how gRPC differs from REST?", "gRPC vs REST comparison"),
    ("How do I implement health checks in my service?", "Implement service health checks"),
    ("What is circuit breaker pattern?", "Circuit breaker pattern"),
    ("Can you explain blue-green deployments?", "Blue-green deployment explained"),
    ("How do I implement canary releases?", "Canary release deployment"),
    ("What is chaos engineering and why is it useful?", "Chaos engineering explained"),
    ("Can you explain how Transformer architecture works in detail?", "Transformer architecture explained"),
    ("What is the difference between BERT and GPT?", "BERT vs GPT differences"),
    ("How do I fine-tune a language model on custom data?", "Fine-tune language model custom data"),
    ("Can you explain what prompt engineering is?", "Prompt engineering explained"),
    ("How do I reduce hallucinations in language model outputs?", "Reduce LLM hallucinations"),
    ("What is retrieval augmented generation?", "Retrieval augmented generation"),
    ("Can you explain how diffusion models generate images?", "Diffusion model image generation"),
    ("How do I evaluate the quality of generated text?", "Evaluate generated text quality"),
    ("What is the difference between zero-shot and few-shot learning?", "Zero-shot vs few-shot learning"),
    ("Can you explain what embedding vectors represent?", "Embedding vectors explained"),
    ("How do I perform sentiment analysis on text?", "Text sentiment analysis"),
    ("What is named entity recognition?", "Named entity recognition explained"),
    ("Can you explain how word2vec works?", "Word2vec explained"),
    ("How do I build a text classification pipeline?", "Text classification pipeline"),
    ("What is the difference between stemming and lemmatization?", "Stemming vs lemmatization"),
    ("Can you explain TF-IDF?", "TF-IDF explained"),
    ("How do I implement semantic search?", "Implement semantic search"),
    ("What is cosine similarity used for?", "Cosine similarity use cases"),
    ("Can you explain how recommendation systems work?", "Recommendation systems explained"),
    ("How do I evaluate a recommendation system?", "Evaluate recommendation system"),
    ("I want to understand how carbon credits work and whether they actually help reduce emissions", "Carbon credits explained"),
    ("Can you explain what a circular economy is and how businesses can adopt it?", "Circular economy for business"),
    ("I need to understand the difference between climate change mitigation and adaptation", "Climate mitigation vs adaptation"),
    ("How does fast fashion contribute to environmental problems?", "Fast fashion environmental impact"),
    ("Can you explain the environmental cost of cryptocurrency mining?", "Crypto mining environmental cost"),
    ("I want to know what the Paris Agreement actually commits countries to do", "Paris Agreement commitments"),
    ("How does deforestation in the Amazon affect global climate?", "Amazon deforestation global climate"),
    ("Can you explain what scope 1, 2, and 3 emissions are?", "Scope 1 2 3 emissions explained"),
    ("I need to understand how life cycle assessment works", "Life cycle assessment explained"),
    ("How do electric vehicles compare to combustion engines in total emissions?", "EV vs combustion total emissions"),
    ("What are the differences between various meditation techniques?", "Meditation techniques compared"),
    ("Can you explain the cognitive effects of sleep deprivation?", "Sleep deprivation cognitive effects"),
    ("How does intermittent fasting affect metabolism?", "Intermittent fasting metabolism"),
    ("I want to understand how to train for a marathon safely", "Marathon training safely"),
    ("Can you explain the principles of macronutrient balance?", "Macronutrient balance principles"),
    ("How do I recover properly from intense workouts?", "Workout recovery methods"),
    ("What is the difference between saturated and unsaturated fats?", "Saturated vs unsaturated fats"),
    ("Can you explain how alcohol affects the liver long-term?", "Alcohol long-term liver effects"),
    ("I want to understand how caffeine affects the nervous system", "Caffeine nervous system effects"),
    ("How does chronic stress affect physical health?", "Chronic stress physical health effects"),
    ("Can you explain what a hedge fund actually does?", "Hedge fund explained"),
    ("I want to understand how options contracts work", "Options contracts explained"),
    ("How do index funds outperform actively managed funds?", "Index vs active fund performance"),
    ("Can you explain what dollar-cost averaging is?", "Dollar-cost averaging explained"),
    ("I need to understand how tax-loss harvesting works", "Tax-loss harvesting explained"),
    ("How do I calculate my net worth properly?", "Calculate net worth"),
    ("What is the difference between a Roth IRA and a traditional IRA?", "Roth vs traditional IRA"),
    ("Can you explain how mortgage amortization works?", "Mortgage amortization explained"),
    ("I want to know how to diversify my investment portfolio", "Diversify investment portfolio"),
    ("How does currency exchange rate fluctuation affect international trade?", "Currency exchange trade effects"),
    ("I'm trying to start a podcast and need advice on how to grow an audience from zero", "Grow podcast audience from zero"),
    ("Can you help me understand what makes a YouTube video rank highly in search?", "YouTube video SEO ranking"),
    ("I want to learn how to create effective social media ads on a small budget", "Small budget social media ads"),
    ("How do I build an email list for my business?", "Build business email list"),
    ("Can you explain what conversion rate optimization is?", "Conversion rate optimization"),
    ("I need to understand how A/B testing works", "A/B testing explained"),
    ("How do I create a content calendar for social media?", "Create social media content calendar"),
    ("What is influencer marketing and does it work?", "Influencer marketing effectiveness"),
    ("Can you explain what affiliate marketing is and how to get started?", "Affiliate marketing basics"),
    ("I want to understand how to analyze Google Analytics data", "Analyze Google Analytics data"),
    ("What is the role of empathy in good leadership?", "Empathy in leadership"),
    ("Can you explain different conflict resolution strategies?", "Conflict resolution strategies"),
    ("How do I build psychological safety in a team?", "Build team psychological safety"),
    ("I want to understand what servant leadership means", "Servant leadership explained"),
    ("Can you explain how to give constructive feedback?", "Give constructive feedback"),
    ("How do I manage underperforming team members?", "Manage underperforming employees"),
    ("What is the difference between management and leadership?", "Management vs leadership"),
    ("Can you explain what transformational leadership is?", "Transformational leadership explained"),
    ("How do I build trust with a remote team?", "Build remote team trust"),
    ("What is the Dunning-Kruger effect and how does it affect teams?", "Dunning-Kruger effect in teams"),
    ("Can you explain how to write effective meeting agendas?", "Write effective meeting agenda"),
    ("I want to understand how to run retrospectives in agile", "Run agile retrospectives"),
    ("How do I estimate work accurately for sprint planning?", "Accurate sprint estimation"),
    ("Can you explain what a product roadmap is?", "Product roadmap explained"),
    ("I need to understand how to prioritize a product backlog", "Prioritize product backlog"),
    ("How do I write good user stories?", "Write good user stories"),
    ("Can you explain what OKRs are and how to use them?", "OKRs explained and usage"),
    ("I want to understand how design thinking works", "Design thinking process"),
    ("How do I conduct effective user research?", "Conduct user research"),
    ("What is jobs-to-be-done theory?", "Jobs-to-be-done theory"),
    ("How does a compiler turn source code into machine code?", "Compiler source to machine code"),
    ("Can you explain how virtual memory works?", "Virtual memory explained"),
    ("I want to understand how a CPU executes instructions", "CPU instruction execution"),
    ("Can you explain what a buffer overflow attack is?", "Buffer overflow attack"),
    ("How does public key cryptography work?", "Public key cryptography"),
    ("I want to understand how TLS/SSL secures connections", "TLS SSL connection security"),
    ("Can you explain what SQL injection is and how to prevent it?", "SQL injection prevention"),
    ("How does a firewall work?", "Firewall operation explained"),
    ("I need to understand what a DDoS attack is", "DDoS attack explained"),
    ("Can you explain how zero-knowledge proofs work?", "Zero-knowledge proofs explained"),
    ("What is the Byzantine generals problem?", "Byzantine generals problem"),
    ("Can you explain what homomorphic encryption is?", "Homomorphic encryption explained"),
    ("How does secure multi-party computation work?", "Secure multi-party computation"),
    ("I want to understand differential privacy", "Differential privacy explained"),
    ("Can you explain how federated learning works?", "Federated learning explained"),
    ("How does model watermarking work for AI?", "AI model watermarking"),
    ("I need to understand model quantization for deployment", "Model quantization deployment"),
    ("Can you explain what knowledge distillation is?", "Knowledge distillation explained"),
    ("How do I reduce the carbon footprint of AI inference?", "Reduce AI inference carbon footprint"),
    ("What is green computing and how is it practiced?", "Green computing practices"),
    ("Can you explain energy-proportional computing?", "Energy-proportional computing"),
    ("How do data centers manage power consumption?", "Data center power management"),
    ("I want to understand what PUE means for data centers", "Data center PUE metric"),
    ("Can you explain what Scope 3 emissions are for tech companies?", "Scope 3 emissions tech companies"),
    ("How do I measure the carbon footprint of software?", "Measure software carbon footprint"),
    ("What tools exist for measuring AI energy consumption?", "AI energy measurement tools"),
    ("Can you explain what the Software Carbon Intensity specification is?", "Software Carbon Intensity spec"),
    ("How does workload scheduling reduce energy use?", "Workload scheduling energy reduction"),
]


# ===========================================================================
# EDGE CASES AND TRICKY PAIRS
# ===========================================================================

EDGE_CASE_PAIRS = [
    # Very short prompts (should stay concise)
    ("What is Python?", "What is Python?"),
    ("Define recursion", "Define recursion"),
    ("Sort list Python", "Sort list Python"),
    ("Hello", "Hello"),
    ("Hi there", "Hi there"),
    ("Thanks", "Thanks"),

    # Already optimized (model should not over-compress)
    ("Explain recursion with examples", "Explain recursion with examples"),
    ("Python list comprehensions", "Python list comprehensions"),
    ("Compare SQL vs NoSQL", "Compare SQL vs NoSQL"),
    ("Build REST API Flask", "Build REST API Flask"),
    ("Implement binary search", "Implement binary search"),

    # Mixed technical + verbose
    ("I'm really struggling and I desperately need help understanding how to implement the singleton design pattern in Python and when I should actually use it in real applications", "Implement Python singleton pattern"),
    ("Could you walk me through very carefully and in great detail the exact steps involved in setting up a complete full-stack web application from scratch using React on the front end and Node.js with Express on the back end?", "Set up React Node.js full-stack app"),
    ("I have been spending the last few days trying to understand how transformer models actually work on a technical level and I just cannot get my head around the attention mechanism no matter how many times I read about it", "Explain transformer attention mechanism"),

    # Questions with specific context clues
    ("My React component keeps re-rendering infinitely, what could be causing this?", "Fix infinite React re-render"),
    ("My Python script crashes with a RecursionError, how do I fix it?", "Fix Python RecursionError"),
    ("My SQL query returns duplicate rows, what's wrong?", "Remove SQL duplicate rows"),
    ("My Docker container exits immediately after starting, what's wrong?", "Debug Docker container exit"),
    ("My API returns 401 even though I'm sending the correct token", "Debug API 401 authentication error"),

    # Long multipart questions
    ("Can you please explain the entire history of computing from Charles Babbage all the way to modern processors, including all the major milestones along the way?", "History of computing major milestones"),
    ("I need a complete and thorough explanation of how the human immune system works, covering innate immunity, adaptive immunity, T cells, B cells, and how vaccines work", "Complete human immune system overview"),
    ("Could you walk me through the entire machine learning pipeline from data collection to model deployment, including preprocessing, feature engineering, model selection, training, evaluation, and deployment?", "Complete ML pipeline overview"),
]


# ===========================================================================
# ASSEMBLE FULL DATASET
# ===========================================================================

def build_dataset():
    print("Building dataset...")

    all_pairs = []

    # 1. Original base pairs with variations
    expanded_base = expand_base_pairs(BASE_PAIRS)
    all_pairs.extend(expanded_base)
    print(f"  Base pairs expanded: {len(expanded_base)}")

    # 2. Topic-generated pairs
    topic_pairs = generate_pairs_from_topics()
    all_pairs.extend(topic_pairs)
    print(f"  Topic pairs generated: {len(topic_pairs)}")

    # 3. Extra hand-crafted pairs with variations
    for orig, opt in EXTRA_PAIRS:
        all_pairs.append({"original": orig, "optimized": opt})
        for _ in range(3):
            noisy = add_noise_words(orig)
            all_pairs.append({"original": noisy, "optimized": opt})

    print(f"  Extra pairs added: {len(EXTRA_PAIRS) * 4}")

    # 4. Edge cases
    for orig, opt in EDGE_CASE_PAIRS:
        all_pairs.append({"original": orig, "optimized": opt})

    print(f"  Edge cases added: {len(EDGE_CASE_PAIRS)}")

    # Deduplicate by original text
    seen = set()
    unique = []
    for p in all_pairs:
        key = p["original"].strip().lower()
        if key not in seen:
            seen.add(key)
            unique.append(p)

    random.shuffle(unique)
    print(f"\nTotal unique pairs: {len(unique)}")

    # Save dataset
    output = {
        "dataset_info": {
            "name": "GreenPromptsOptimizer Large Training Dataset",
            "total_pairs": len(unique),
            "version": "2.0",
            "description": "Expanded dataset for T5 prompt optimization fine-tuning"
        },
        "data": unique
    }

    out_path = DATA_DIR / "training_dataset_10k.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # Print stats
    orig_lens = [len(p["original"].split()) for p in unique]
    opt_lens = [len(p["optimized"].split()) for p in unique]
    avg_reduction = 100 * (1 - sum(opt_lens) / sum(orig_lens))

    print(f"\nDataset saved to: {out_path}")
    print(f"Average original length: {sum(orig_lens)/len(orig_lens):.1f} words")
    print(f"Average optimized length: {sum(opt_lens)/len(opt_lens):.1f} words")
    print(f"Average token reduction: {avg_reduction:.1f}%")

    return len(unique)


if __name__ == "__main__":
    total = build_dataset()
    print(f"\nDone. {total} training pairs ready.")
