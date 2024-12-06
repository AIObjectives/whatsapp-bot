# Example Usage in main.py
# Here’s how you can use the survey_mode module in your main.py:

from survey_mode.initialize_survey import initialize_event_collection

# Define event details and survey questions
event_id = "Dec3FullDynamicSurvey"
event_name = "Dec3FullDynamicSurvey"
event_location = "Global"
event_background = "A survey exploring the experiences and challenges of LBQ+ women in various sectors."
event_date = "2024-12-01"

questions = [
    "How widely do you share your LBQ identity with people, and how do you decide who to discuss it with?",
    "How widely known is your identity in your workplace? Did you tell people, or did they find out in another way?",
    "Please tell us about how you earn an income. For example: what type of work do you do: how did you find this work, is it in the formal or informal sector; what is your level of seniority, how long have you been in this position and how satisfied are you with your current work situation?",
    "What have been the biggest barriers or challenges you’ve faced in earning an income?",
    "In what ways does being a woman (or non-binary or trans) impacted your choices, opportunities, and challenges in finding work, earning an income, or advancing in your career?",
    "As an LBQ+ woman, what are the biggest challenges you face in living your life fully and safely while earning an income?",
    "How do people’s attitudes in your community or place of work about LGBQ+ people affect your ability to earn money or grow in your career?",
    "What experiences of discrimination have you had as an LBQ+ woman in your workplace or business? How did you handle it?",
    "Can you share a time when you felt supported as an LBQ+ woman at work or in business? What made the experience special?",
    "What changes would you like to see in your community or workplace to create more opportunities for LBQ+ women to succeed?",
    "What do you think LGBTQI organizations or allies could do to improve the financial well-being of LBQ+ women?",
    "What types of support do you think would be most beneficial for LBQ+ women in your community to succeed in their careers or business?",
    "How do you think your identity as an LBQ woman has influenced the decisions you have made about how to earn a living?",
    "Is there anything else you'd like to share about this topic?",
]

# Initialize Survey Mode event
initialize_event_collection(
    event_id,
    event_name,
    event_location,
    event_background,
    event_date,
    questions
)
