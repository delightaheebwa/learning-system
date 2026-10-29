<!-- source: https://www.promptingguide.ai/techniques/cot | type: html | hash: f0654d351769306557ad3b8055151dac0bc82a23e81a58b37c151e806f0b4d6b | fetched: 2026-10-28T00:00:00Z -->

🚀 Learn to build apps with Claude Code! Use PROMPTING for 20% off Enroll now →
Prompt Engineering Guide 🎓 Courses
About About
GitHub (opens in a new tab) Discord (opens in a new tab) ✨ Services
- Prompt Engineering
- Introduction - LLM Settings
- Basics of Prompting
- Prompt Elements
- General Tips for Designing Prompts
- Examples of Prompts
- Prompting Techniques - Zero-shot Prompting
- Few-shot Prompting
- Chain-of-Thought Prompting
- Meta Prompting
- Self-Consistency
- Generate Knowledge Prompting
- Prompt Chaining
- Tree of Thoughts
- Retrieval Augmented Generation
- Automatic Reasoning and Tool-use
- Automatic Prompt Engineer
- Active-Prompt
- Directional Stimulus Prompting
- Program-Aided Language Models
- ReAct
- Reflexion
- Multimodal CoT
- Graph Prompting
- AI Agents - Introduction to Agents
- Agent Components
- AI Workflows vs AI Agents
- Context Engineering for AI Agents
- Context Engineering Deep Dive
- Function Calling
- Deep Agents
- Guides - Optimizing Prompts
- OpenAI Deep Research
- Reasoning LLMs
- 4o Image Generation
- Context Engineering Guide
- Applications - Fine-tuning GPT-4o
- Function Calling
- Context Caching with LLMs
- Generating Data
- Generating Synthetic Dataset for RAG
- Tackling Generated Datasets Diversity
- Generating Code
- Graduate Job Classification Case Study
- Prompt Function
- Prompt Hub - Classification - Sentiment Classification
- Few-Shot Sentiment Classification
- Coding - Generate Code Snippet
- Generate MySQL Query
- Draw TiKZ Diagram
- Creativity - Rhymes
- Infinite Primes
- Interdisciplinary
- Inventing New Words
- Evaluation - Evaluate Plato's Dialogue
- Information Extraction - Extract Model Names
- Image Generation - Draw a Person Using Alphabet
- Mathematics - Evaluating Composite Functions
- Adding Odd Numbers
- Question Answering - Closed Domain Question Answering
- Open Domain Question Answering
- Science Question Answering
- Reasoning - Indirect Reasoning
- Physical Reasoning
- Text Summarization - Explain A Concept
- Truthfulness - Hallucination Identification
- Adversarial Prompting - Prompt Injection
- Prompt Leaking
- Jailbreaking
- Models - ChatGPT
- Claude 3
- Code Llama
- Flan
- Gemini
- Gemini Advanced
- Gemini 1.5 Pro
- Gemma
- GPT-4
- Grok-1
- Kimi K2.5
- LLaMA
- Llama 3
- Mistral 7B
- Mistral Large
- Mixtral
- Mixtral 8x22B
- OLMo
- Phi-2
- Sora
- LLM Collection
- Risks & Misuses - Adversarial Prompting
- Factuality
- Biases
- LLM Research Findings - LLM Agents
- RAG for LLMs
- LLM Reasoning
- RAG Faithfulness
- LLM In-Context Recall
- RAG Reduces Hallucination
- Synthetic Data
- ThoughtSculpt
- Infini-Attention
- LM-Guided CoT
- Trustworthiness in LLMs
- LLM Tokenization
- What is Groq?
- Papers
- Tools
- Notebooks
- Datasets
- Additional Readings
- Services
English Light
On This Page
- Chain-of-Thought (CoT) Prompting
- Zero-shot COT Prompting
- Automatic Chain-of-Thought (Auto-CoT)
Question? Give us feedback → (opens in a new tab) Edit this page
Prompting Techniques
Chain-of-Thought Prompting
Copy page
Chain-of-Thought Prompting
Chain-of-Thought (CoT) Prompting
Image Source: Wei et al. (2022) (opens in a new tab)
Introduced in Wei et al. (2022) (opens in a new tab) , chain-of-thought (CoT) prompting enables complex reasoning capabilities through intermediate reasoning steps. You can combine it with few-shot prompting to get better results on more complex tasks that require reasoning before responding.
Prompt:
The odd numbers in this group add up to an even number: 4, 8, 9, 15, 12, 2, 1.
A: Adding all the odd numbers (9, 15, 1) gives 25. The answer is False.
The odd numbers in this group add up to an even number: 17, 10, 19, 4, 8, 12, 24.
A: Adding all the odd numbers (17, 19) gives 36. The answer is True.
The odd numbers in this group add up to an even number: 16, 11, 14, 4, 8, 13, 24.
A: Adding all the odd numbers (11, 13) gives 24. The answer is True.
The odd numbers in this group add up to an even number: 17, 9, 10, 12, 13, 4, 2.
A: Adding all the odd numbers (17, 9, 13) gives 39. The answer is False.
The odd numbers in this group add up to an even number: 15, 32, 5, 13, 82, 7, 1.
A:
Output:
Adding all the odd numbers (15, 5, 13, 7, 1) gives 41. The answer is False.
Wow! We can see a perfect result when we provided the reasoning step. In fact, we can solve this task by providing even fewer examples, i.e., just one example seems enough:
Prompt:
The odd numbers in this group add up to an even number: 4, 8, 9, 15, 12, 2, 1.
A: Adding all the odd numbers (9, 15, 1) gives 25. The answer is False.
The odd numbers in this group add up to an even number: 15, 32, 5, 13, 82, 7, 1.
A:
Output:
Adding all the odd numbers (15, 5, 13, 7, 1) gives 41. The answer is False.
Keep in mind that the authors claim that this is an emergent ability that arises with sufficiently large language models.
Zero-shot COT Prompting
Image Source: Kojima et al. (2022) (opens in a new tab)
One recent idea that came out more recently is the idea of zero-shot CoT (opens in a new tab) (Kojima et al. 2022) that essentially involves adding "Let's think step by step" to the original prompt. Let's try a simple problem and see how the model performs:
Prompt:
I went to the market and bought 10 apples. I gave 2 apples to the neighbor and 2 to the repairman. I then went and bought 5 more apples and ate 1. How many apples did I remain with?
Output:
11 apples
The answer is incorrect! Now Let's try with the special prompt.
Prompt:
I went to the market and bought 10 apples. I gave 2 apples to the neighbor and 2 to the repairman. I then went and bought 5 more apples and ate 1. How many apples did I remain with?
Let's think step by step.
Output:
First, you started with 10 apples.
You gave away 2 apples to the neighbor and 2 to the repairman, so you had 6 apples left.
Then you bought 5 more apples, so now you had 11 apples.
Finally, you ate 1 apple, so you would remain with 10 apples.
It's impressive that this simple prompt is effective at this task. This is particularly useful where you don't have too many examples to use in the prompt.
Automatic Chain-of-Thought (Auto-CoT)
When applying chain-of-thought prompting with demonstrations, the process involves hand-crafting effective and diverse examples. This manual effort could lead to suboptimal solutions. Zhang et al. (2022) (opens in a new tab) propose an approach to eliminate manual efforts by leveraging LLMs with "Let's think step by step" prompt to generate reasoning chains for demonstrations one by one. This automatic process can still end up with mistakes in generated chains. To mitigate the effects of the mistakes, the diversity of demonstrations matter. This work proposes Auto-CoT, which samples questions with diversity and generates reasoning chains to construct the demonstrations.
Auto-CoT consists of two main stages:
- Stage 1): question clustering : partition questions of a given dataset into a few clusters
- Stage 2): demonstration sampling : select a representative question from each cluster and generate its reasoning chain using Zero-Shot-CoT with simple heuristics
The simple heuristics could be length of questions (e.g., 60 tokens) and number of steps in rationale (e.g., 5 reasoning steps). This encourages the model to use simple and accurate demonstrations.
The process is illustrated below:
Image Source: Zhang et al. (2022) (opens in a new tab)
Code for Auto-CoT is available here (opens in a new tab) .
Related Learning
Course
Prompt Engineering for LLMs
Master chain-of-thought prompting, zero-shot CoT, and advanced reasoning techniques for complex problem solving.
Beginner
2 hours
Course
Building Effective AI Agents
Learn to build effective AI agents. Covers function calling, tool integration, and debugging agentic systems.
Intermediate
5 hours
Explore All Courses
Discover our full catalog of AI and prompt engineering courses. From beginners to advanced practitioners. Use code PROMPTING20 for 20% off!
Browse Academy
Few-shot Prompting Meta Prompting
English Light
Copyright © 2026 DAIR.AI