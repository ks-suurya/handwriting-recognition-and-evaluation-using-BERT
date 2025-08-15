from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class QuestionAnswer:
    question_id: str
    question_text: str
    answer_text: str
    marks_allotted: float

@dataclass
class EvaluationResult:
    question_id: str
    question_text: str
    student_answer: str
    teacher_answer: str
    similarity_score: float
    length_score: float
    marks_allotted: float
    question_score: float

@dataclass
class EvaluationSummary:
    results_per_question: List[EvaluationResult]
    total_obtained_marks: float
    total_marks_allotted: float
    total_test_marks: float
    final_score: int
    processing_time: float