# Import the necessary libraries for this application, including the recommender.py that I made
import streamlit as st
from recommender import *
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Create a title in the webpage
st.title("Major Advisor")

# Load in the majors
majors = load_majors()

# Load in all the interests in the majors
all_interests = sorted(set(interest for major in majors for interest in major["interests"]))

# Load in all the skills in the majors
all_skills = sorted(set(skill for major in majors for skill in major["skills"]))

# Load in all the personality in the majors
all_p = sorted(set(p for major in majors for p in major["personality"]))

# Prompt users to select interests that they have
st.subheader("Step 1")
selected_interests = st.multiselect("Select your interests", options = all_interests)

# Prompt users to select skills that they have
st.subheader("Step 2")
selected_skills = st.multiselect("Select your skills", options = all_skills)

# Prompt users to select the personality that suits them
st.subheader("Step 3")
selected_p = st.multiselect("Select your personalities", options = all_p)

# Normalize the interests (make sure there are no duplicates)
user_interests = normalized_interests(selected_interests)

# Create empty dictionaries for storing the interest rankings and skills ranking from the user input
int_ranking = {}
skill_ranking = {}

# Prompt user to rank their selected interests from 1 to 5
for interest in user_interests:
    int_ranking[interest] = st.slider(f"Rate your interest in {interest}", 1, 5, 3)

# Prompt user to rank their selected skills from 1 to 5
for skill in selected_skills:
    skill_ranking[skill] = st.slider(f"Rate your skill in {skill}", 1, 5, 3)

# Prompt user to select their minimum desired salary
st.subheader("Step 4")
minimum_salary = st.slider("Minimum desired salary", 0, 200000, 100000)

# This if code will run when the user press "Show Recommendatios" button
# This button will also only show when the user has selected at least 1 interest, 1 skill, and 1 personality
if st.button("Show Recommendations", disabled=len(selected_interests) == 0 or len(selected_skills) == 0 or len(selected_p) == 0):

    # For this application, we will use streamlit's session state. Streamlit's session state is used for
    # the application to remember its past conversation and to remember that the user has already pressed the button.
    # Everytime a user uses the chatbot function, streamlit will rerun from the top. Without the session state,
    # streamlit will forget that the "Show Recommendations" button was pressed, which would mean the 
    # recommend_majors() function didn't run and the program would not work. The main reason we need the session state
    # is for the program to remember past conversation after the user uses the chatbot.

    # Shows that the program is analyzing using st.spinner()
    with st.spinner("Analyzing your profile..."):
        # Generate top recommendations for the user using their interests, skill, personality, and salary as indicators
        st.session_state.recommendations = recommend_majors(user_interests, selected_skills, selected_p, majors, int_ranking, skill_ranking, minimum_salary)

        # Create other empty session states for storage
        st.session_state.explanations = {}
        st.session_state.similar = {}

# If the recommendations is in session state, then run this block of code
if "recommendations" in st.session_state:

    # Rename st.session_state.recommendations to recommendations for simpler code practice
    recommendations = st.session_state.recommendations

    # Create categories for a radar chart that will be displayed
    categories = ["Interests", "Skills", "Traits"]
    
    # Create a sub header for the webpage
    st.subheader("Top Recommendations")

    # Loop through the top 3 majors that the recommend_majors() recommended
    for major in recommendations[:3]:

        # Get the user interest score, skill score, and personality score in a list (for radar chart)
        scores = [major["int_score"], major["skill_score"], major["p_score"]]

        # Duplicate the first value of the categories and the scores (for radar chart to closes the polygon)
        theta = categories + [categories[0]]
        r = scores + [scores[0]]

        # Store the major overall score in overall_score for display purposes
        overall_score = major["overall_score"]

        # If the overall score is more than 85%, then it's an excellent match
        if overall_score >= 0.85:
            confidence = "🌟 Excellent Match"

        # If the overall score is more than 70%, then it's a strong match
        elif overall_score >= 0.70:
            confidence = "🟢 Strong Match"

        # If the overall score is more than 55%, then it's a good match
        elif overall_score >= 0.55:
            confidence = "🟡 Good Match"

        # If the overall score is more than 40%, then it's a possible match
        elif overall_score >= 0.40:
            confidence = "🟠 Possible Match"

        # If the overall score is lower than 40%, then it's a weak match
        else:
            confidence = "🔴 Weak Match"

        # Use expander for each major (cleaner UI) and display the Major's name, the Match Confidence
        # the Match Score, and the Difficulty of the major
        with st.expander(f"**{major['name']}** {confidence} ({major['overall_score']:.1%} Match) Difficulty: {'⭐' * major['difficulty']}"):

            # Create columns to create a display for difficulty and what each star means in the difficulty
            col1, col2 = st.columns([5, 1])

            # Show the Major's Difficulty
            with col1:
                st.write(f"**Difficulty:** {'⭐' * major['difficulty']}")

            # Show the difficulty "stars" system's definition
            with col2:
                with st.popover("ℹ️"):
                    st.markdown("""
            ### Difficulty Scale

            ⭐ **Easy**
            - Light courseload
            - Introductory concepts

            ⭐⭐ **Moderate**
            - Regular studying
            - Some technical material

            ⭐⭐⭐ **Challenging**
            - Mix of theory, projects, and exams
            - Intermediate technical courses

            ⭐⭐⭐⭐ **Hard**
            - Heavy workload
            - Advanced technical courses

            ⭐⭐⭐⭐⭐ **Very Hard**
            - Intensive mathematics, programming, research, or technicality
            """)

            # Create Overview, Courses, Careers, and Insights tab
            overview_tab, course_tab, career_tab, insight_tab = st.tabs(["🏠 Overview", "📚 Courses", "💼 Careers", "📈 Insights"])

            # In the overview tab, show these components
            with overview_tab:

                # Show the overall score breakdown (Show Interest, Skill, and Personality score)
                st.write("**Overall Match Score % Breakdown:**")
                st.write(f"**🎯 Interest Match:** {major['int_score']:.0%}")
                st.progress(major['int_score'])
                st.write(f"**🛠️ Skill Match:** {major['skill_score']:.0%}")
                st.progress(major['skill_score'])
                st.write(f"**🧠 Personality Match:** {major['p_score']:.0%}")
                st.progress(major['p_score'])

                # If the major was never ran and never stored in session_state.explanations, then run this code
                if major["name"] not in st.session_state.explanations:

                    # Show that the program is thinking
                    with st.spinner("Generating Explanation..."):
                        # Use ai_explanation to explain why the major is a good fit and what the user would need to-
                        # work on more for a better fit to this major
                        # Use session_state so when the streamlit reruns, it's faster if the program has 
                        # explained about the major before

                        # Try if the ai_explanation works
                        try:
                            st.session_state.explanations[major["name"]] = ai_explanation(major)

                        # Display this message if ai_explanation had an error
                        except Exception:
                            st.warning("AI Explanation is unavailable. Please check and make sure Ollama is running properly.")

                # Display the AI's explanation
                st.write(st.session_state.explanations[major["name"]])

                # Show what education are offered for this major
                st.write(f"**🎓 Education offered:** {major['education']}")
                
                # Create a figure (a blank canvas for radar chart)
                fig = go.Figure()

                # Add the categories and scores detail for the radar chart
                fig.add_trace(go.Scatterpolar(r = r, theta = theta, fill = "toself", name = major['name']))

                # Configure the radar chart's template, height, background color, grid color, line color, ticks, and to show the line
                # Along with the font's and angular axis configuration.
                fig.update_layout(template="plotly_dark", height = 500, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                polar=dict(bgcolor="rgba(0,0,0,0)", radialaxis=dict(visible=True, range=[0, 1],
                                            gridcolor="white", linecolor="white", tickfont=dict(color="white"),
                                            showline=True),
                                angularaxis=dict(gridcolor="white", linecolor="white", tickfont=dict(color="white"),
                                            showline=True)), 
                                font=dict(color="white")  )

                # Show the radar_chart and configure the width for it to depend on its container
                st.plotly_chart(fig, use_container_width=True)

                # Show similar majors to the current recommended major
                st.write("**🔄 Similar Majors:**")

                # Create similar scores list
                similar_scores = []

                # For each major in all the majors
                for maj in majors:

                    # If the major's name is the same to the current recommended one, then skip
                    if major["name"] == maj["name"]:
                        continue
                    
                    # Find the similarity score between the current recommended major and the major
                    # the program is looping through
                    similar_scoring = similar_majors(major, maj)

                    # Add the major and its similarity score into a dictionary and add it into the
                    # similar_scores list
                    similar_scores.append({"name": maj["name"], "interests": maj["interests"], 
                                           "skills": maj["skills"], "personality": maj["personality"], 
                                           "score": similar_scoring})
                
                # Sort the list by the similarity score (descending values)
                similar_scores.sort(key=lambda x: x["score"], reverse=True)

                # Loop through the top 3 majors that were most similar to the current recommended major
                for i in similar_scores[:3]:

                    # Print the major's name and the similarity score
                    st.write(f"- **{i['name']} ({i['score']:.2%})**")

                    # Print out the small header for why the major is similar
                    st.write(f"**Why is {i['name']} similar to {major['name']}**")

                    # Store both major's name as the key for the dictionary in similar's session state
                    key = (major["name"], i["name"])

                    # Show that the program is thinking
                    with st.spinner("Generating Explanation..."):

                        # If the major hasn't been analyzed or explained before, then run this code
                        if key not in st.session_state.similar:
                            
                            # Try similar_explanation function
                            try:
                                # Generate the similarity explanation
                                st.session_state.similar[key] = similar_explanation(major, i)

                            # If the function fails, display this message
                            except Exception:
                                st.warning("AI Explanation is unavailable. Please check and make sure Ollama is running properly.")
                    
                    # Display the AI's explanation for similarity
                    st.write(st.session_state.similar[key])
                    
            # In the course tab, print the courses the user needs to take and the course's difficulty
            with course_tab:

                # Print header for the courses tab
                st.write("**Main courses you'd need to take:**")

                # Loop through the major's courses and show each courses' name and difficulty
                for c in major["courses"]:
                    st.write(f"- **{c['name']}**, **Course Difficulty:** {'⭐' * c['difficulty']}")

            # In the career tab, show the recommended careers for this major
            with career_tab:

                # Print out the header for the career tab
                st.write(f"**Recommended Careers:**")

                # Loop through all the careers in this recommended major
                for c in major["careers"]:

                    # If the salary for the career is more than the minimum salary desired that the user selected,
                    # then run this block of code
                    if c["salary"] >= minimum_salary:

                        # In this container, show the career's name and the salary for the career
                        # (st.container is used to show the career and salary in a "card" display format)
                        with st.container(border=True):
                            st.subheader(c["title"])
                            st.metric("Average Salary", f"${c['salary']}")
                    # Else, run this block of code if the salary for the career is less than the minimum
                    # salary desired that the user selected
                    else:
                        st.write(f"Although {c['title']} matched your interests, it did not satisfy the minimum salary requirements.")

            # In the insights tab, show the score for each categories along with what the user is missing
            # or would need to explore on for better match scores
            with insight_tab:

                # Print out header for the insight tab
                st.write(f"Why this major matched **{c['title']}:**")
            
                # Sort the user selected interest scores
                sorted_int_scores = sorted(major["matched_int"].items(), key=lambda x: x[1], reverse=True)
                
                # Find the missing attributes or what the user needs to work on using missing_attrb
                miss_int = missing_attrb(user_interests, major["interests"])

                # Sort the miss_int list so it shows the missing attribute along with their scoring
                miss_int = sorted(miss_int, key=lambda x: major["interests"][x], reverse=True)

                # Sort the user selected skills scores
                sorted_skill_scores = sorted(major["matched_skills"].items(), key=lambda x: x[1], reverse=True)
                
                # Find the missing attributes or what the user needs to work on using missing_attrb
                miss_skill = missing_attrb(selected_skills, major["skills"])

                # Sort the miss_int list so it shows the missing attribute along with their scoring
                miss_skill = sorted(miss_skill, key=lambda x: major["skills"][x], reverse=True)
                
                # Sort the user selected personality scores
                sorted_p_scores = sorted(major["matched_p"].items(), key=lambda x: x[1], reverse=True)
                
                # Find the missing attributes or what the user needs to work on using missing_attrb
                miss_p = missing_attrb(selected_p, major["personality"])

                # Sort the miss_int list so it shows the missing attribute along with their scoring
                miss_p = sorted(miss_p, key=lambda x: major["personality"][x], reverse=True)

                # Print the Interests Section
                st.write("**Interests Section**")

                # Show the user's strengths in interests
                st.write("💪 Your Strength(s)")

                # If the sorted_int_scores list isn't empty, then run this code
                if sorted_int_scores:

                    # Loop through and show the user's matched interest scoring 
                    for interest, score in sorted_int_scores:
                        st.write(f"- {interest}")
                
                # Else if the list is empty, show "None"
                else:
                    st.write("- None")

                # Print the Areas to Explore for the user
                st.write("🌱 Area(s) to Explore")

                # If the miss_int list isn't empty, then run this code
                if miss_int:

                    # Loop through the missing attribute for interest and show the attributes
                    for i in miss_int:
                        st.write(f"- {i}")

                # Else if the list is empty, show "None"
                else:
                    st.write("- None")

                # Print the Skills Section
                st.write("**Skills Section**")

                # Show the user's strength in skills
                st.write("💪 Your Strength(s)")

                # If the sorted_skill_scores list isn't empty, then run this code
                if sorted_skill_scores:

                    # Loop through and show the user's matched skill scoring 
                    for skill, score in sorted_skill_scores:
                        st.write(f"- {skill}")

                # Else if the list is empty, show "None"
                else:
                    st.write("- None")
                
                # Print the Areas to Explore for the user
                st.write("🌱 Area(s) to Explore")

                # If the miss_skill list isn't empty, then run this code
                if miss_skill:    

                    # Loop through the missing attribute for skills and show the attributes
                    for i in miss_skill:
                        st.write(f"- {i}")

                # Else if the list is empty, show "None"
                else:
                    st.write("- None")
                
                # Print the Personality Section
                st.write("**Personality Section**")

                # Show the user's strength in personality
                st.write("💪 Your Strength(s)")

                # If the sorted_p_scores list isn't empty, then run this code
                if sorted_p_scores:

                    # Loop through and show the user's matched personality scoring 
                    for p, score in sorted_p_scores:
                        st.write(f"- {p}")

                # Else if the list is empty, show "None"
                else:
                    st.write("- None")

                # Print the Areas to Explore for the user
                st.write("🌱 Area(s) to Explore")

                # If the miss_p list isn't empty, then run this code
                if miss_p:

                    # Loop through the missing attribute for personality and show the attributes
                    for i in miss_p:
                        st.write(f"- {i}")

                # Else if the list is empty, show "None"
                else:
                    st.write("- None")
        
    # Store the recommended major and overall score in a dataframe
    df = pd.DataFrame([{"Major": m["name"], "Match": m["overall_score"]} for m in recommendations[:3]])

    # Use plotly to make a bar plot comparing the match score between the 3 recommended majors 
    fig = px.bar(df, x = "Major", y = "Match", title = "Top 3 Recommended Majors", hover_data={"Match": ":.2%"})

    # Configure the y-axis label and the tick format
    fig.update_yaxes(title = "Match %", tickformat = ".0%")
    
    # Configure the x-axis label
    fig.update_xaxes(title = "Major")

    # Make a plotly barchart and configure the width for it to fit the container for displaying the bar chart
    st.plotly_chart(fig, use_container_width=True)

    # Print the sub header showing the top 3 majors comparison summary
    st.subheader("Top 3 Comparison Rundown")

    # Loop through the majors in the top 3 recommended majors from the recommend_majors()
    for major in recommendations[:3]:

        # Create 3 columns (5, 2, 3 are the size of the space for each columns)
        # Column 1 has 5 space, column 2 has 2 space, and column 3 has 3 space
        col1, col2, col3 = st.columns([5, 2, 3])    

        # Calculate the average salary for each major by summing the salary in the careers and dividing
        # by the number of careers
        avg_sal = sum(c["salary"] for c in major["careers"]) / len(major["careers"])

        # Show the major names in column 1
        with col1:
            st.metric("Major", f"{major['name']}")

        # Show the major's overall score in column 2
        with col2:
            st.metric("Match %", f"{major['overall_score']:.2%}")

        # Show the major's average salary in column 3
        with col3:
            st.metric("Average Salary", f"${avg_sal:,.2f}")

    # Get the top 1 major from the recommendations
    best_major = recommendations[0]

    # Show the best major/most recommended major for the user
    st.success(f"Based on your interests, {best_major['name']} appears to be your strongest match.")
    
    # Make a divider for this new section
    st.divider()

    # Print the AI Career Advisor Chatbot section
    st.subheader("🤖 AI Career Advisor Chatbot")
    
    # If this program hasn't run yet and has not created a session state for "msg", then run this code
    if "msg" not in st.session_state:
        st.session_state.msg = []
        
    # Loop through each message in the session state
    for message in st.session_state.msg:

        # Display the role (user or chatbot) and the message content
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Get the user's input in the chatbox
    get_input = st.chat_input("Ask me any questions!", key="ask_feedback")

    # Display the examples of what questions they can ask
    st.write("Examples:")
    st.write("• Which major has the most math?")
    st.write("• Is Data Science harder than Information Systems?")
    st.write("• What if I dislike programming?")
    st.write("• Which major fits healthcare?")

    # If the user asked a question and it's not empty, then run this block of code
    if get_input:

        # Display the user's question
        with st.chat_message("user"):
            st.markdown(get_input)

        # Display the chatbot's answer
        with st.chat_message("assistant"):

            # Show that the chatbot is thinking while waiting for ai_answer to generate the answer
            with st.spinner("Thinking..."):

                # Try the ai_answer() function
                try:
                    # Generate the chatbot's answer
                    answer = ai_answer(get_input, recommendations)

                # Display this message if there was an error
                except Exception:
                    st.warning("AI Explanation is unavailable. Please check and make sure Ollama is running properly.")

            # Display the chatbot's answer
            st.markdown(answer)

        # Append the user's message into the session_state so the program can remember what the user asked
        st.session_state.msg.append({"role": "user", "content": get_input})

        # Append the chatbot's answer into the session_state so the program can remember what the answer was
        st.session_state.msg.append({"role": "assistant", "content": answer})

# If the user pressed Start Over, then run this code
if st.button("Start Over"):

    # Clear the chatbot's messages
    st.session_state.messages = []

    # Rerun the code
    st.rerun()