# Python file contain all functions needed for Major Advisor Recommender

# DISCLAIMER: In this project, I've used ChatGPT to help me code, teach me about the algorithms, about json files, and
# about how to use the LLMs. I did not use ChatGPT to create codes for me to copy. I wrote all the functions-
# and algorithms for the recommender along with the framework myself. I only used ChatGPT as a guider/tutor for
# learning syntaxes of new libraries and some refinement suggestions for my Major Advisor Recommender.

# Import json to load in json files
import json

# Import ollama for LLM usage for an "AI Chatbot"
from ollama import chat

# Load the majors file 
def load_majors():
    # Read the file at the file designation (Enter your own file designation)
    with open("Enter file designation here", "r") as file:

        # Load the file (stored as dictionary)
        majors = json.load(file)

    # Return the majors
    return majors

# Load the synonyms file (Not sure if still used)
def load_syn():
    # Read the file at the file designation (Enter your own file designation    )
    with open("Enter file designation here", "r") as file:

        # Load the file (stored as dictionary)
        syns = json.load(file)

    # Return the synonyms
    return syns

# Normalizes the user interests (if 2 interests has different name but similar meaning, it will be grouped into one)
# (For example, coding and programming would be grouped into coding)
def normalized_interests(user_interests):

    # Load the synonyms.json file
    synonyms = load_syn()

    # Create an empty list
    normalized_interest = []

    # For an interest in all user's interests
    for interest in user_interests:
        # If the interest is in the synonyms
        if interest in synonyms:
            # Normalize the interest
            normal_interest = synonyms[interest]

            # Add the normalized interest into the empty list
            normalized_interest.append(normal_interest)
        else:
            # If the interest is alreaedy normalized, just add into the empty list
            normalized_interest.append(interest)

    # Make sure there are no duplicates in the normalized interest using set()
    normalized_interest = list(set(normalized_interest))

    # Return the normalized interests
    return normalized_interest

# This is the main majors recommending algorithm
# This algorithm will calculate the user's match with the major in these 3 categories: interests, skills, and personality
# The result of the calculation will be displayed as a percentage.
def recommend_majors(user_interests, user_skills, user_personality, all_majors, int_ranking, skill_ranking, sal):
    # Create an empty list
    results = []

    # Loop through each majors
    for major in all_majors:

        # Initiate overall score
        overall_score = 0

        # Get the interest scores and the matched interests from interests_score()
        int_score, matched_interests = interests_score(user_interests, major, int_ranking)

        # Get the skill scores and the matched skills from skills_score()
        skill_score, matched_skills = skills_score(user_skills, major, skill_ranking)

        # Get the personality scores and the matched personality from personality_score()
        p_score, matched_p = personality_score(user_personality, major)

        # Max score for interests in that major
        maj_max_int = (sum(major["interests"].values()) * 5)

        # Max score for skills in that major
        maj_max_skill = (sum(major["skills"].values()) * 5)

        # Max score for personality in that major
        maj_max_p = (sum(major["personality"].values()) * 5)
        
        # Initialize user's max score for interest
        user_max_int = 0

        # Loop through each interest in user's selected interests, keep looping until it goes through all user's selected interest
        for interest in user_interests:

            # If the interest is in the current major's interest, then run this code line
            if interest in major["interests"]:

                # Add the user interest's max score in user_max_int
                user_max_int += major["interests"][interest] * 5
        
        # Initialize user's max score for skills
        user_max_skill = 0

        # Loop through each skill in user's selected skills, keep looping until it goes through all user's selected skills
        for skill in user_skills:

            # If the skill is in the current major's skill, then run this code line
            if skill in major["skills"]:

                # Add the user skill's max score in user_max_skill
                user_max_skill += major["skills"][skill] * 5

        # Initialize user's max score for personality
        user_max_p = 0

        # Loop through each personality in user's selected personality
        for p in user_personality:

            # If the personality is in the current major's personality, then run this code line
            if p in major["personality"]:

                # Add the user personality's max score in user_max_p
                user_max_p += major["personality"][p] * 5

        # Normalized the interest, skill, and personality score (balancing between major's max and user's max)
        # (Every score is now percentages)
        int_norm = norm_score(int_score, user_max_int, maj_max_int)
        skill_norm = norm_score(skill_score, user_max_skill, maj_max_skill)
        p_norm = norm_score(p_score, user_max_p, maj_max_p)

        # Initiate weight variable
        weight_sum = 0

        # If the user's max for interest is more than 0, then run this block of code
        if user_max_int > 0:

            # Add the interest score * weight into the overall score
            overall_score += int_norm * 0.5

            # Add the weight for interest into weight_sum
            weight_sum += 0.5

        # If the user's max for skill is more than 0, then run this block of code
        if user_max_skill > 0:

            # Add the skill score * weight into the overall score
            overall_score += skill_norm * 0.3

            # Add the weight for skill into weight_sum
            weight_sum += 0.3

        # If the user's max for personality is more than 0, then run this block of code
        if user_max_p > 0:
            
            # Add the personality score * weight into the overall score
            overall_score += p_norm * 0.2

            # Add the weight for personality into weight_sum
            weight_sum += 0.2

        # If the sum of the weights are more than 0, divide the overall score by weight_sum
        # I do this because sometimes there may be a category that had no match, and it wouldn't make sense-
        # to calculate the score by a 100% if one of the category didn't have any weight on it.
        # For example, if user had no matched skills, then we should be dividing by 70% (which would be ALL the weight) not 100%.
        if weight_sum > 0:

            # Normalize the overall_score, make sure the weights are calculated correctly
            overall_score /= weight_sum

        # If the overall score is more than 0, then append the major along with their scores and details into the empty list
        if overall_score > 0:
            results.append({"name": major["name"], "desc": major["description"], "overall_score": overall_score, "skills": major['skills'], "personality": major['personality'],
                            "int_score": (int_norm), "skill_score": (skill_norm), "p_score": (p_norm), "careers" : major['careers'], "education": major['education'], 
                            "interests": major['interests'], "matched_int": matched_interests, "matched_skills": matched_skills, "matched_p": matched_p, "difficulty": major['difficulty'],
                            "courses": major['courses'], "salary": sal})

    # Sort the list by the "overall score" of each dictionary
    results.sort(key = lambda x: x["overall_score"], reverse = True)

    # Return the results
    return results

# Calculate the user's interests score in that major
def interests_score(user_interests, major, ranking_interests):
    # Initialize score variable and an empty dictionary
    score = 0
    matched_interests = {}
        
    # Loop through each interest in user's selected interest
    for interest in user_interests:
        # If the interest matched the major's interest
        if interest in major["interests"]:
            # Then, calculate the interest score(interest's significance in the major * user's ranking for the interest)
            interest_score = (ranking_interests[interest] * major["interests"][interest]) 

            # Add the interest score in score
            score += interest_score

            # Add the matched interest in the empty dictionary along with its score
            matched_interests[interest] = interest_score

    # Return the score and the matched interests
    return score, matched_interests

# Calculate the user's skills score in that major
def skills_score(user_skills, major, ranking_skills):
    # Initialize score variable and an empty dictionary
    score = 0
    matched_skills = {}
        
    # Loop through each skill in user's selected skills
    for skill in user_skills:
        # If the skill matched the major's skill
        if skill in major["skills"]:
            # Then, calculate the skill score(skill's significance in the major * user's ranking for the skill)
            skill_score = (ranking_skills[skill] * major["skills"][skill]) 

            # Add the skill score in score
            score += skill_score

            # Add the matched skill in the empty dictionary along with its score
            matched_skills[skill] = skill_score

    # Return the score and the matched skills
    return score, matched_skills

# Calculate the user's personality score in that major
def personality_score(user_personality, major):
    # Initialize score variable and an empty dictionary
    score = 0
    matched_pers = {}

    # Loop through each personality in the user's selected personality
    for p in user_personality:
        # If the personality matched the major's personality
        if p in major["personality"]:
            # Find the personality's significance score for that major
            p_score = major["personality"][p]

            # Add the p_score to score
            score += p_score

            # Add the matched personality in the empty dictionary along with its score
            matched_pers[p] = p_score

    # Return the score and the matched personality
    return score, matched_pers

# Find the missing interests, skills, or personality of the user compared to the major's preferred interests-
# skills, and personality
def missing_attrb(user_val, maj_val):
    # Create an empty list
    missing = []

    # For each trait in major
    for i in maj_val:

        # If the user doesn't have that trait
        if i not in user_val:

            # Add the missing trait into the empty list
            missing.append(i)

    # Return the list
    return missing

# Normalize the score
def norm_score(raw_score, user_max, major_max):
    # Calculate the score using the user's selected traits as the max
    user_match = raw_score / user_max if user_max else 0

    # Calculate the score using the major traits as the max
    major_match = raw_score / major_max if major_max else 0

    # Balance between the major's max score and the user's max score
    adj_score = (user_match * 0.7) + (major_match * 0.3)

    # Return the adjusted score
    return adj_score

# Find the majors that are similar to each other
def similar_majors(major1, major2):
    # Initialize the interest, skill, and personality score
    int_score = 0
    skill_score = 0
    p_score = 0 

    # Loop through the interest of a major along with its weight
    for i, weight1 in major1["interests"].items():
        # If the interest from this major matches the interest of another major
        if i in major2["interests"]:
            # Get the weight of the interest from the other major
            weight2 = major2["interests"][i]

            # Find the minimum between 2 weights and get the interest score from it
            int_score += min(weight1, weight2)
    
    # Loop through the skill of a major along with its weight
    for s, weight1 in major1["skills"].items():
        # If the skill from this major matches the skill of another major
        if s in major2["skills"]:
            # Get the weight of the skill from the other major
            weight2 = major2["skills"][s]

            # Find the minimum between 2 weights and get the skill score from it
            skill_score += min(weight1, weight2)
    
    # Loop through the personality of a major along with its weight
    for p, weight1 in major1["personality"].items():
        # If the personality from this major matches the personality of another major
        if p in major2["personality"]:
            # Get the weight of the personality from the other major
            weight2 = major2["personality"][p]

            # Find the minimum between 2 weights and get the personality score from it
            p_score += min(weight1, weight2)

    # Get the maximum max score for interests from both majors
    max_int = max(
        sum(major1["interests"].values()),
        sum(major2["interests"].values()))

    # Get the maximum max score for skills from both majors
    max_skill = max(
        sum(major1["skills"].values()),
        sum(major2["skills"].values()))

    # Get the maximum max score for personality from both majors
    max_p = max(
        sum(major1["personality"].values()),
        sum(major2["personality"].values()))

    # Calculate the score (in percentage) of each categories
    int_norm = int_score / max_int if max_int else 0
    skill_norm = skill_score / max_skill if max_skill else 0
    p_norm = p_score / max_p if max_p else 0

    # Add each category along with multiplying them with their specific weights
    similar_score = (int_norm * 0.5) + (skill_norm * 0.3) + (p_norm * 0.2)

    # Return the similarity score
    return similar_score

# Define a function that uses Ollama LLM to explain why the major is a good match for the user
def ai_explanation(major):

    # Define the prompt
    prompt = f"""
    
    The student's best major is {major["name"]}.

    Match score (in percentage): {major["overall_score"]:.1%}

    Matched interests:
    {list(major["matched_int"].keys())}

    User selected interests:
    {list(major['interests'].keys())}

    Matched skills:
    {list(major["matched_skills"].keys())}

    User selected skills:
    {list(major['skills'].keys())}

    Matched Personality:
    {list(major["matched_p"].keys())}

    User selected Personality:
    {list(major['personality'].keys())}

    Careers:
    {[c["title"] for c in major["careers"]]}

    Difficulty:
    {major["difficulty"]}

    User selected preferred salary:
    {major["salary"]}

    You are an experienced university advisor, do not make any assumption. (no using "could", or "can", or make any guesses)

    You ONLY answer questions using the recommendation information provided.

    Do NOT invent facts.

    Do NOT make up courses, salaries, majors, or career information.

    If the information is unavailable, explicitly say:
    "I don't have enough information to answer that."

    Never recommend a major outside the recommendation list unless the user explicitly asks for alternatives.
    Use Markdown and headers.

    Also don't use % in explanation. The recommendation score is not a probability for success, but it shows how aligned
    the user is, compared to the given major.

    Write a simplified explanation (150 words max) in a friendly tone, but not like a friend to friend chat, more like a professor to a student chatting 
    Explain why:
    
    This major fits
    Explain how the student's interests, skills, and personality align.

    The Strengths
    Mention 2-3 strengths.

    The Potential Challenges
    Mention one or two realistic challenges.

    Practical Advice
    Give practical advice for succeeding.
    """

    # Get the response for the prompt
    response = chat(model = "llama3.2", messages = [{"role": "user", "content" : prompt}])

    # Return the response
    return response["message"]["content"]

# Get the AI's answer to the user's question 
def ai_answer(question, recommendations):

    # Get the user's top 3 majors that were recommended by the recommender algorithm
    top3 = recommendations[:3]

    # Define the prompt
    prompt = f"""
    You are a university advisor.

    Recommendation results:

    {json.dumps(top3, indent=2)}

    The student's best major is {recommendations[0]["name"]}.

    Match score (in percentage): {recommendations[0]["overall_score"]:.1%}

    Matched interests:
    {list(recommendations[0]["matched_int"].keys())}

    User selected interests:
    {list(recommendations[0]['interests'].keys())}

    Matched skills:
    {list(recommendations[0]["matched_skills"].keys())}

    User selected skills:
    {list(recommendations[0]['skills'].keys())}

    Matched Personality:
    {list(recommendations[0]["matched_p"].keys())}

    User selected Personality:
    {list(recommendations[0]['personality'].keys())}

    Careers:
    {[c["title"] for c in recommendations[0]["careers"]]}

    Difficulty:
    {recommendations[0]["difficulty"]}

    User selected preferred salary:
    {recommendations[0]["salary"]}

    The user asks:

    {question}

    Answer conversationally.
    Don't invent any new information not found in recommendation data.
    Don't make any guesses.
    """

    # Get the response for the prompt
    response = chat(model = "llama3.2", messages = [{"role": "user", "content" : prompt}])

    # Return the response
    return response["message"]["content"]

# Create a function for using AI to explain why the majors are similar
def similar_explanation(major1, major2):
    # Define the prompt
    prompt = f"""
    Explain why {major1} is similar to {major2} by comparing
    {major1['interests']} to {major2['interests']},
    {major1['skills']} to {major2['skills']},
    and {major1['personality']} to {major2['personality']}.

    Don't explain more than 130 words.
    Don't invent any new information.
    Don't explain by showing the dictionary, any coding syntaxes or any cryptic explanations. 
    Use words and explain like how a University Advisor would do.
    Make sure the explanation is simple and easy to understand.

    Make sure to explain: 
    Why the both majors are considered similar.
    The main skills and interests they share.
    The biggest difference between them.
    Which type of student might prefer one over the other.

    Do not list scores or percentages.
    Do not refer to them as "profiles."
    """

    # Get the response for the prompt
    response = chat(model = "llama3.2", messages = [{"role": "user", "content" : prompt}])

    # Return the response
    return response["message"]["content"]