from __future__ import annotations

from werkzeug.security import generate_password_hash

from app import db
from app.models.career import Career
from app.models.scholarship import Scholarship
from app.models.user import User
from app.models.conversation import Conversation, ConversationMessage


def seed() -> None:
    # Careers
    if Career.query.first() is None:
        careers = [
            {
                "title": "Software Engineer",
                "description": "Build software that solves real problems.",
                "salary_low": 65000,
                "salary_high": 120000,
                "education": "Computer Science or related",
                "required_skills": "Python, JavaScript, problem-solving, teamwork",
            },
            {
                "title": "Data Analyst",
                "description": "Turn data into insights and decisions.",
                "salary_low": 55000,
                "salary_high": 95000,
                "education": "Statistics / Data Science",
                "required_skills": "SQL, spreadsheets, communication",
            },
            {
                "title": "Cybersecurity Analyst",
                "description": "Protect systems and users from threats.",
                "salary_low": 60000,
                "salary_high": 110000,
                "education": "Information Security / Computer Science",
                "required_skills": "Networking, security basics, persistence",
            },
            {
                "title": "Healthcare Administrator",
                "description": "Improve healthcare operations and patient outcomes.",
                "salary_low": 52000,
                "salary_high": 90000,
                "education": "Public Health / Business",
                "required_skills": "Leadership, organization, communication",
            },
            {
                "title": "Mechanical Engineer",
                "description": "Design and build mechanical systems.",
                "salary_low": 70000,
                "salary_high": 130000,
                "education": "Mechanical Engineering",
                "required_skills": "Math, CAD, teamwork",
            },
            {
                "title": "UX Designer",
                "description": "Create user-friendly digital experiences.",
                "salary_low": 60000,
                "salary_high": 105000,
                "education": "Design / HCI",
                "required_skills": "Research, empathy, prototyping",
            },
            {
                "title": "Environmental Scientist",
                "description": "Study ecosystems and support sustainability.",
                "salary_low": 55000,
                "salary_high": 95000,
                "education": "Environmental Science",
                "required_skills": "Data analysis, fieldwork, writing",
            },
            {
                "title": "Marketing Specialist",
                "description": "Help brands reach the right audiences.",
                "salary_low": 50000,
                "salary_high": 90000,
                "education": "Marketing / Communications",
                "required_skills": "Writing, creativity, analytics",
            },
            {
                "title": "Nurse (RN) Track",
                "description": "Provide patient care and support.",
                "salary_low": 65000,
                "salary_high": 110000,
                "education": "Nursing program / RN",
                "required_skills": "Compassion, science, communication",
            },
            {
                "title": "Teacher / Education Specialist",
                "description": "Teach and support student learning.",
                "salary_low": 48000,
                "salary_high": 90000,
                "education": "Education degree / certification",
                "required_skills": "Communication, patience, leadership",
            },
        ]
        db.session.add_all([Career(**c) for c in careers])
        db.session.commit()

    # Scholarships
    if Scholarship.query.first() is None:
        scholarships = []
        for i in range(1, 21):
            scholarships.append(
                Scholarship(
                    name=f"Scholarship {i}: Opportunity Grant",
                    award_amount=1000 * i,
                    eligibility="Students demonstrating academic potential and community involvement.",
                    deadline=f"{2026}-0{(i%9)+1}-15",
                    tags="STEM, Leadership, Community" if i % 2 == 0 else "Arts, Leadership, Community",
                )
            )
        db.session.add_all(scholarships)
        db.session.commit()

    # Example user + conversations
    # Ensure we always create a valid user row (username is NOT NULL).
    if User.query.first() is None:
        user = User(
            username="student",
            email="student@example.com",
            password_hash=generate_password_hash("password123"),
            name="Jordan Rivera",
            grade_level="10th Grade",
            school="Riverside Middle/High",
            interests="technology, healthcare, leadership",
            career_goals="Software Engineer",
            skills="Python, teamwork, communication",
            activities="Robotics Club, Volunteer Tutoring",
            gpa=3.6,
        )
        db.session.add(user)
        db.session.flush()

        conv = Conversation(user_id=user.id, title="Welcome chat")
        db.session.add(conv)
        db.session.flush()
        db.session.add(
            ConversationMessage(
                conversation_id=conv.id,
                role="user",
                content="How do I start building a roadmap for software engineering?",
            )
        )
        db.session.add(
            ConversationMessage(
                conversation_id=conv.id,
                role="assistant",
                content="Start with one small project, join a club, and ask for feedback weekly. Then we’ll map your next steps.",
            )
        )
        db.session.commit()
