import torch
import numpy as np
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity
from app.models.evaluation import EvaluationResult, EvaluationSummary
import logging
import time

logger = logging.getLogger(__name__)


class BERTService:
    def __init__(self):
        self.tokenizer = None
        self.model = None
        self._initialize_model()

    def _initialize_model(self):
        """Initialize BERT model and tokenizer."""
        try:
            logger.info("Loading BERT model...")
            self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
            self.model = BertModel.from_pretrained('bert-base-uncased')
            self.model.eval()
            logger.info("BERT model loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load BERT model: {str(e)}")
            raise

    def calculate_similarity_score(self, teacher_answer, student_answer):
        """Calculate cosine similarity between teacher's and student's answers using BERT embeddings."""
        try:
            def get_embedding(text):
                inputs = self.tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
                with torch.no_grad():
                    outputs = self.model(**inputs)
                return outputs.last_hidden_state[:, 0, :].squeeze().numpy()  # Use [CLS] token embedding

            teacher_embedding = get_embedding(teacher_answer)
            student_embedding = get_embedding(student_answer)

            # Calculate cosine similarity
            similarity = cosine_similarity([teacher_embedding], [student_embedding])[0][0]
            return float(similarity)

        except Exception as e:
            logger.error(f"Similarity calculation failed: {str(e)}")
            return 0.0

    def calculate_length_score(self, teacher_answer, student_answer):
        """Simple length comparison between teacher's and student's answers."""
        teacher_len = len(teacher_answer.split())
        student_len = len(student_answer.split())

        if teacher_len == 0:
            return 0.0

        # Allow some flexibility in length, but penalize very short answers
        length_ratio = min(student_len / teacher_len, 1.0)
        return length_ratio

    def evaluate_answers(self, teacher_answers, student_answers, total_test_marks):
        """Evaluate student answers against teacher answers."""
        start_time = time.time()

        try:
            # Create dictionaries for quick lookup
            teacher_dict = {ans['question_text'].strip(): ans['answer_text'].strip()
                            for ans in teacher_answers}
            marks_dict = {ans['question_text'].strip(): float(ans['marks_allotted'])
                          for ans in teacher_answers}
            student_dict = {q['question_id']: q['corrected_text'].strip()
                            for q in student_answers}

            # Validate questions match (simplified - assumes sequential mapping)
            if len(teacher_answers) != len(student_answers):
                logger.warning(
                    f"Question count mismatch: Teacher={len(teacher_answers)}, Student={len(student_answers)}")

            # Calculate total marks allotted
            total_marks_allotted = sum(marks_dict.values())
            if total_marks_allotted == 0:
                raise ValueError("Total marks allotted is zero")

            # Initialize results
            results = []
            total_obtained_marks = 0

            # Process each question
            for i, (teacher_ans, student_ans) in enumerate(zip(teacher_answers, student_answers)):
                question_text = teacher_ans['question_text']
                teacher_answer = teacher_ans['answer_text']
                student_answer = student_ans['corrected_text']
                marks_allotted = teacher_ans['marks_allotted']

                # Calculate scores
                similarity_score = self.calculate_similarity_score(teacher_answer, student_answer)
                length_score = self.calculate_length_score(teacher_answer, student_answer)

                # Final score for the question
                question_score = similarity_score * length_score * marks_allotted
                total_obtained_marks += question_score

                # Create result
                result = EvaluationResult(
                    question_id=student_ans['question_id'],
                    question_text=question_text,
                    student_answer=student_answer,
                    teacher_answer=teacher_answer,
                    similarity_score=round(similarity_score * 100, 2),  # Percentage
                    length_score=round(length_score, 2),
                    marks_allotted=marks_allotted,
                    question_score=round(question_score, 2)
                )
                results.append(result)

                logger.info(f"Evaluated Q{i + 1}: Similarity={result.similarity_score}%, Score={result.question_score}")

            # Normalize total obtained marks to the total test marks
            normalization_factor = total_test_marks / total_marks_allotted
            final_score = int(total_obtained_marks * normalization_factor)

            processing_time = time.time() - start_time

            return EvaluationSummary(
                results_per_question=results,
                total_obtained_marks=round(total_obtained_marks, 2),
                total_marks_allotted=total_marks_allotted,
                total_test_marks=total_test_marks,
                final_score=final_score,
                processing_time=round(processing_time, 2)
            )

        except Exception as e:
            logger.error(f"Evaluation failed: {str(e)}")
            raise