import pandas as pd
from transformers import pipeline
import random


def generate_dynamic_feedback(analysis_results: dict) -> list:
    """
    분석 결과를 바탕으로 동적인 피드백을 생성합니다.
    """
    feedback = []

    # 각 카테고리별 임계값 설정
    thresholds = {
        "aggressive": 20,
        "ignoring": 10,
        "cold": 20
    }

    # 카테고리별 피드백 메시지 포맷
    feedback_formats = {
        "aggressive": '공격적이거나 방어적인 표현(예: "{example}")의 사용 빈도가 {ratio:.0f}%로 다소 높습니다. 조금 더 부드러운 표현을 사용해보는 건 어떨까요?',
        "ignoring": '"{example}"처럼 무시하는 듯한 표현이 가끔씩 보입니다. 대신 "네 생각은 어때?"와 같이 상대방의 의견을 존중하는 표현을 사용해보세요.',
        "cold": '단답형이거나 차가운 느낌의 대화(예: "{example}")가 전체의 {ratio:.0f}%를 차지하고 있어요. "그렇구나!", "네 말이 맞아."처럼 리액션을 더해주면 대화가 훨씬 부드러워질 거예요.'
    }

    # 각 카테고리에 대해 임계값을 넘는지 확인하고 피드백 생성
    for category, threshold in thresholds.items():
        ratio = analysis_results.get(f"{category}_ratio", 0)
        if ratio > threshold:
            examples = analysis_results.get(f"{category}_examples", [])
            if examples:
                # 피드백에 사용할 예시 메시지를 랜덤으로 선택
                example_message = random.choice(examples)
                feedback.append(feedback_formats[category].format(example=example_message, ratio=ratio))

    # 생성된 피드백이 없으면 긍정적인 메시지 추가
    if not feedback:
        feedback.append("대화 분석 결과, 전반적으로 좋은 대화 습관을 가지고 계십니다! 지금처럼만 유지해주세요.")

    return feedback


def analyze_conversation(df: pd.DataFrame, user_name: str, sentiment_model, classifier):
    """
    AI 모델을 사용하여 대화 내용을 분석하고 동적 피드백을 생성합니다.
    """
    user_df = df[df["User"] == user_name]

    if user_df.empty:
        return {"error": f"'{user_name}' 사용자의 대화가 없습니다."}

    messages = user_df["Message"].dropna().tolist()
    # 메시지 샘플링 로직 추가
    if len(messages) > 500:
        messages = random.sample(messages, 500)

    # 모델 최대 길이에 맞게 메시지 자르기
    messages = [msg[:400] for msg in messages]

    if not messages:
        return {"total_messages": 0, "feedback": ["분석할 메시지가 없습니다."]}

    total_messages = len(messages)

    # 1. 기존 감성 분석 모델을 사용한 부정 비율 계산 (기존 로직 유지)
    sentiments = sentiment_model(messages)
    neg_count = sum(1 for s in sentiments if s["label"].lower().startswith("neg"))
    negative_ratio = (neg_count / total_messages) * 100 if total_messages > 0 else 0

    # 2. 제로샷 분류 모델을 사용한 세부 카테고리 분석
    candidate_labels = ["공격적인", "무시하는", "차가운", "중립적인"]

    # 카테고리별 메시지 수와 예시 저장
    category_counts = {label: 0 for label in candidate_labels}
    category_examples = {label: [] for label in candidate_labels}

    # 제로샷 분류 실행
    results = classifier(messages, candidate_labels, multi_label=False)

    for i, result in enumerate(results):
        # 가장 높은 점수를 받은 레이블을 해당 메시지의 카테고리로 지정
        top_label = result['labels'][0]
        category_counts[top_label] += 1
        # 특정 카테고리에 속하는 메시지 예시 저장
        if top_label in ["공격적인", "무시하는", "차가운"]:
            category_examples[top_label].append(messages[i])

    # 각 카테고리별 비율 계산
    analysis_results = {
        "total_messages": total_messages,
        "negative_ratio": round(negative_ratio, 2),
        "aggressive_ratio": round((category_counts.get("공격적인", 0) / total_messages) * 100,
                                  2) if total_messages > 0 else 0,
        "ignoring_ratio": round((category_counts.get("무시하는", 0) / total_messages) * 100,
                                2) if total_messages > 0 else 0,
        "cold_ratio": round((category_counts.get("차가운", 0) / total_messages) * 100, 2) if total_messages > 0 else 0,
        "aggressive_examples": category_examples.get("공격적인", []),
        "ignoring_examples": category_examples.get("무시하는", []),
        "cold_examples": category_examples.get("차가운", [])
    }

    # 3. 동적 피드백 생성
    feedback = generate_dynamic_feedback(analysis_results)
    analysis_results["feedback"] = feedback

    # 최종 결과에서 예시 메시지는 제외
    final_results = {k: v for k, v in analysis_results.items() if not k.endswith("_examples")}

    return final_results