"""
Assessment generation and grading tools.
Creates quiz questions and evaluates student performance.
"""
from typing import List, Dict, Any
import random
from src.config import Config


def generate_assessment_questions(topics: str, num_questions: int = 10) -> List[Dict[str, Any]]:
    """
    Generate assessment questions based on study topics.

    Args:
        topics: Topics to generate questions about
        num_questions: Number of questions to generate

    Returns:
        List of question dictionaries
    """
    # Question templates for different Azure/Microsoft topics
    question_templates = [
        {
            "template": f"What is the primary purpose of {{topic}} in Microsoft Azure?",
            "options": [
                f"To manage {{topic}} resources efficiently",
                "To provide storage services",
                "To handle network routing",
                "To manage user authentication"
            ],
            "correct": 0,
            "difficulty": "easy"
        },
        {
            "template": f"Which Azure service is best suited for {{topic}} workloads?",
            "options": [
                "Azure Virtual Machines",
                f"Azure {{topic}} Service",
                "Azure Storage",
                "Azure Networking"
            ],
            "correct": 1,
            "difficulty": "medium"
        },
        {
            "template": f"What are the key benefits of using {{topic}} in Azure? (Select the best answer)",
            "options": [
                "Reduced costs only",
                "Improved performance only",
                f"Scalability, reliability, and managed {{topic}} capabilities",
                "None of the above"
            ],
            "correct": 2,
            "difficulty": "medium"
        },
        {
            "template": f"How does Azure {{topic}} integrate with other Azure services?",
            "options": [
                "It doesn't integrate with other services",
                f"Through Azure Resource Manager and service endpoints",
                "Only through third-party tools",
                "Manual configuration only"
            ],
            "correct": 1,
            "difficulty": "hard"
        }
    ]

    questions = []
    topic_words = topics.split()

    for i in range(num_questions):
        template = question_templates[i % len(question_templates)]
        topic_word = topic_words[i % len(topic_words)] if topic_words else "Azure"

        question = {
            "question_id": i + 1,
            "question_text": template["template"].replace("{{topic}}", topic_word),
            "options": [opt.replace("{{topic}}", topic_word) for opt in template["options"]],
            "correct_answer": template["correct"],
            "topic": topic_word,
            "difficulty": template["difficulty"]
        }
        questions.append(question)

    return questions


def grade_assessment(questions: List[Dict[str, Any]], student_answers: List[int]) -> Dict[str, Any]:
    """
    Grade student assessment and provide feedback.

    Args:
        questions: List of questions with correct answers
        student_answers: List of student's answer indices

    Returns:
        Assessment result dictionary with score, feedback, and weak areas
    """
    if len(questions) != len(student_answers):
        return {
            "score": 0.0,
            "total_questions": len(questions),
            "correct_answers": 0,
            "passed": False,
            "feedback": "Error: Number of answers doesn't match number of questions",
            "weak_areas": []
        }

    correct_count = 0
    weak_areas = []

    for i, (question, answer) in enumerate(zip(questions, student_answers)):
        if answer == question["correct_answer"]:
            correct_count += 1
        else:
            weak_areas.append(question["topic"])

    score = correct_count / len(questions)
    passed = score >= Config.PASSING_SCORE_THRESHOLD

    # Generate feedback
    if passed:
        feedback = f"Excellent work! You scored {score*100:.0f}% and demonstrated strong understanding of the material."
    else:
        feedback = f"You scored {score*100:.0f}%. Review the weak areas and try again. Focus on: {', '.join(set(weak_areas))}."

    return {
        "score": score,
        "total_questions": len(questions),
        "correct_answers": correct_count,
        "passed": passed,
        "feedback": feedback,
        "weak_areas": list(set(weak_areas))
    }
