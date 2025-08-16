import time
from transformers import BertTokenizer, BertModel
import torch
from sklearn.metrics.pairwise import cosine_similarity
from app.schemas import EvaluationSummary, QuestionResult  # Import dataclasses from schemas


class BERTService:
    def __init__(self):
        self.tokenizer = None
        self.model = None

    def _load_model(self):
        if self.tokenizer is None or self.model is None:
            self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
            self.model = BertModel.from_pretrained('bert-base-uncased')
            self.model.eval()

    def _get_embedding(self, text):
        inputs = self.tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state[:, 0, :].squeeze().numpy()

    def _calculate_similarity(self, teacher_answer, student_answer):
        teacher_embedding = self._get_embedding(teacher_answer)
        student_embedding = self._get_embedding(student_answer)
        similarity = cosine_similarity([teacher_embedding], [student_embedding])[0][0]
        return similarity

    def _calculate_length_score(self, teacher_answer, student_answer):
        teacher_len = len(teacher_answer.split())
        student_len = len(student_answer.split())
        if teacher_len == 0:
            return 0
        length_ratio = min(student_len / teacher_len, 1.0)
        return length_ratio

    def evaluate_answers(self, teacher_answers, student_answers, total_test_marks):
        self._load_model()
        start_time = time.time()

        student_answers_dict = {item['question_id']: item['corrected_text'] for item in student_answers}

        results_per_question = []
        total_obtained_marks = 0
        total_marks_allotted = sum(qa['marks_allotted'] for qa in teacher_answers)

        for teacher_qa in teacher_answers:
            question_id = teacher_qa['question_id']
            student_answer_text = student_answers_dict.get(question_id, "")
            teacher_answer_text = teacher_qa['answer_text']
            marks_allotted = teacher_qa['marks_allotted']

            similarity_score = self._calculate_similarity(teacher_answer_text, student_answer_text)
            length_score = self._calculate_length_score(teacher_answer_text, student_answer_text)

            question_score = similarity_score * length_score * marks_allotted
            total_obtained_marks += question_score

            results_per_question.append(
                QuestionResult(
                    question_id=question_id,
                    question_text=teacher_qa.get('question_text', ''),
                    student_answer=student_answer_text,
                    teacher_answer=teacher_answer_text,
                    similarity_score=round(similarity_score * 100, 2),
                    length_score=round(length_score, 2),
                    marks_allotted=marks_allotted,
                    question_score=round(question_score, 2)
                )
            )

        # Normalize score
        normalization_factor = total_test_marks / total_marks_allotted if total_marks_allotted > 0 else 0
        final_score = round(total_obtained_marks * normalization_factor)

        processing_time = round(time.time() - start_time, 2)

        return EvaluationSummary(
            results_per_question=results_per_question,
            total_obtained_marks=round(total_obtained_marks, 2),
            total_marks_allotted=total_marks_allotted,
            total_test_marks=total_test_marks,
            final_score=final_score,
            processing_time=processing_time
        )
