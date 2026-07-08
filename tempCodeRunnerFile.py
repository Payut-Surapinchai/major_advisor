import streamlit as st
from recommender import *
from app import *
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

st.title("Major Advisor")
majors = load_majors()

all_interests = sorted(set(interest for major in majors for interest in major["interests"]))

all_skills = sorted(set(skill for major in majors for skill in major["skills"]))

all_p = sorted(set(p for major in majors for p in major["personality"]))

selected_interests = st.multiselect("Select your interests", options = all_interests)
selected_skills = st.multiselect("Select your skills", options = all_skills)
selected_p = st.multiselect("Select your personalities", options = all_p)

user_interests = normalized_interests(selected_interests)

int_ranking = {}
skill_ranking = {}

for interest in user_interests:
    int_ranking[interest] = st.slider(f"Rate your interest in {interest}", 1, 5, 3)

for skill in selected_skills:
    skill_ranking[skill] = st.slider(f"Rate your skill in {skill}", 1, 5, 3)

minimum_salary = st.slider("Minimum desired salary", 0, 200000, 100000)

if st.button("Show Recommendations", disabled=len(selected_interests) == 0 or len(selected_skills) == 0 or len(selected_p) == 0):

    recommendations = recommend_majors(user_interests, selected_skills, selected_p, majors, int_ranking, skill_ranking)

    st.subheader("Top Recommendations")

    for major in recommendations[:3]:
        with st.expander(f"**{major['name']}** ({major['overall_score']:.1%} Match)"):

            st.write(f"**Education offered:** {major['education']}")

            st.write(f"**Recommended Careers:**")

            for c in major['careers']:
                if c['salary'] >= minimum_salary:
                    st.write(f"**{c['title']}, Average salary: {c['salary']:,}**")

                    st.write(f"Why this major matched **{c['title']}:**")
                
                    sorted_int_scores = sorted(
                        major["matched_int"].items(),
                        key=lambda x: x[1],
                        reverse=True)

                    sorted_skill_scores = sorted(
                        major["matched_skills"].items(),
                        key=lambda x: x[1],
                        reverse=True)
                    
                    sorted_p_scores = sorted(
                        major["matched_p"].items(),
                        key=lambda x: x[1],
                        reverse=True)

                    st.write("**Interests Section**")
                    for interest, score in sorted_int_scores:
                        st.write(f"- {interest}: {score}")

                    st.write("**Skills Section**")
                    for skill, score in sorted_skill_scores:
                        st.write(f"- {skill}: {score}")
                    
                    st.write("**Personality Section**")
                    for p, score in sorted_p_scores:
                        st.write(f"- {p}: {score}")
                else:
                    st.write(f"Although {c['title']} matched your interests, it did not satisfy the minimum salary requirements.")

    df = pd.DataFrame([{"Major": m["name"], "Match": m["overall_score"]} for m in recommendations[:3]])

    fig = px.bar(df, x = "Major", y = "Match", title = "Top 3 Recommended Majors", hover_data={"Match": ":.2%"})

    fig.update_yaxes(title="Match Percentage", tickformat=".0%")
    
    fig.update_xaxes(title="Major")

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top 3 Comparison Rundown")

    for major in recommendations[:3]:

        col1, col2, col3 = st.columns([5, 2, 3])    
        avg_sal = sum(c["salary"] for c in major["careers"]) / len(major["careers"])

        with col1:
            st.metric("Major", f"{major['name']}")

        with col2:
            st.metric("Match %", f"{major['overall_score']:.2%}")

        with col3:
            st.metric(
                "Average Salary",
                f"${avg_sal:,.2f}")

    best_major = recommendations[0]

    st.success(
        f"Based on your interests, "
        f"{best_major['name']} appears to be your strongest match.")