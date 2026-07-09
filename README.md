# Major Advisor Recommender with Chatbot LLM

This project is a personal project by Payut Surapinchai. 

The goal for this project is to learn more about how to use AI, Machine Learning, how to make recommendation system, how to use Ollama, 
and be more familiar with the overall LLM framework. 

**DISCLAIMER:** In this project, I've used ChatGPT to help me code, teach me about the algorithms, about json files, and
about how to use the LLMs. I did not use ChatGPT to create codes for me to copy. I wrote all the functions-
and algorithms for the recommender along with the framework myself. I only used ChatGPT as a guider/tutor for
learning syntaxes of new libraries and some refinement suggestions for my Major Advisor Recommender.

**COMMENTS IN CODE FILES**: In the code files, you may have noticed that the comments are very detailed and pretty much explains what happens line-by-line. The reason behind this was because I wanted for people who have little background in coding or not very familiar with programming, understands what each steps does. I apologize if the code files looks messy, but to convey the reasoning behind each codes to non-technical users, I believe it was best to explain the codes line-by-line.

## Files Explanation

`majors.json` -> a json file that contains information about each majors (asked ChatGPT to create this for me)

`synonyms.json` -> a json file that contains synonyms for words, so there would be no duplicates in interests when recommending majors
                   (not sure if needed anymore because the new system doesn't require user to type, so there's very low chance that there
                   are any duplicates in interests, but I kept the file and the function anyways because it was very interesting and may be
                   needed for future LLM deployments)

`recommender.py` -> a Python file that contains all the functions that are used to run the Major Advisor Recommender along with utilizing
                    Ollama for LLM and AI purposes

`streamlit_app.py` -> a Python file that contains how the application is displayed, ran, formatted, and how the overall system works

`Application Showcase.pdf` -> a pdf file that shows how the application works

In the recommender.py for the `load_majors()` and `load_syn()` functions, make sure to put your own file designation for the program to work.

Let me know if there are any concerns or inquiries about the program.
Contact: payut.surapinchai2005@gmail.com 
