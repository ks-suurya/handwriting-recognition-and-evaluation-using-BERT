from dataclasses import dataclass, asdict
from typing import List

@dataclass
class QuestionResult:
    question_id: str
    question_text: str
    student_answer: str
    teacher_answer: str
    similarity_score: float
    length_score: float
    marks_allotted: float
    question_score: float

    def to_dict(self):
        return asdict(self)

@dataclass
class EvaluationSummary:
    results_per_question: List[QuestionResult]
    total_obtained_marks: float
    total_marks_allotted: float
    total_test_marks: float
    final_score: int
    processing_time: float

    def to_dict(self):
        return {
            "summary": {
                "total_obtained_marks": self.total_obtained_marks,
                "total_marks_allotted": self.total_marks_allotted,
                "total_test_marks": self.total_test_marks,
                "final_score": self.final_score,
                "processing_time": self.processing_time
            },
            "results": [res.to_dict() for res in self.results_per_question]
        }
