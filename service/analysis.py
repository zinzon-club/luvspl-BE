import pandas as pd
from transformers import pipeline
import random
from typing import Dict, List

# --- 설정 (Configuration) ---

CATEGORY_MAP: Dict[str, str] = {
    "공격적인": "aggressive",
    "무시하는": "ignoring",
    "차가운": "cold",
    "중립적인": "neutral",
}

PRIMARY_ANALYSIS_CATEGORIES: List[str] = ["aggressive", "ignoring", "cold"]

FEEDBACK_CONFIG = {
    "aggressive": [
        {
            "threshold": 30,
            "format": '공격적인 표현(예: "{example}")의 사용 빈도가 {ratio:.0f}%로 매우 높습니다. 이는 상대방에게 상처를 줄 수 있으니, 의식적으로 줄여보는 노력이 필요해 보입니다.',
        },
        {
            "threshold": 15,
            "format": '공격적이거나 방어적인 표현(예: "{example}")의 사용 빈도가 {ratio:.0f}%로 다소 높습니다. 조금 더 부드러운 표현을 사용해보는 건 어떨까요?',
        },
    ],
    "ignoring": [
        {
            "threshold": 20,
            "format": '"{example}"와 같이 상대방의 말을 무시하는 듯한 표현이 {ratio:.0f}%로 자주 보입니다. 상대방의 의견을 경청하고 존중하는 태도가 필요해 보입니다.',
        },
        {
            "threshold": 10,
            "format": '"{example}"처럼 무시하는 듯한 표현이 가끔씩 보입니다. 대신 "네 생각은 어때?"와 같이 상대방의 의견을 존중하는 표현을 사용해보세요.',
        },
    ],
    "cold": [
        {
            "threshold": 40,
            "format": '단답형이거나 차가운 느낌의 대화(예: "{example}")가 전체의 {ratio:.0f}%로 매우 높은 비중을 차지하고 있습니다. 대화에 좀 더 감정을 표현하고 리액션을 더해주면 관계 개선에 큰 도움이 될 거예요.',
        },
        {
            "threshold": 20,
            "format": '단답형이거나 차가운 느낌의 대화(예: "{example}")가 전체의 {ratio:.0f}%를 차지하고 있어요. "그렇구나!", "네 말이 맞아."처럼 리액션을 더해주면 대화가 훨씬 부드러워질 거예요.',
        },
    ],
    "positive": [
        {
            "threshold": 10,
            "condition": "less_than",
            "format": '긍정적인 표현의 비율이 {ratio:.0f}%로 낮은 편입니다. "고마워", "좋은 생각이야" 와 같이 긍정적인 표현을 더 자주 사용해보세요.',
        }
    ],
    "neutral": [
        {
            "threshold": 80,
            "condition": "greater_than",
            "format": "대화의 {ratio:.0f}%가 중립적인 내용으로 이루어져 있습니다. 때로는 감정을 표현하거나 유머를 더해 대화를 더 풍부하게 만들어보는 것은 어떨까요?",
        }
    ],
}
DEFAULT_FEEDBACK = "대화 분석 결과, 전반적으로 좋은 대화 습관을 가지고 계십니다! 지금처럼만 유지해주세요."


def generate_dynamic_feedback(analysis_results: dict) -> list:
    """
    분석 결과를 바탕으로 동적인 피드백을 생성합니다.
    """
    feedback = []
    feedback_added_for_category = set()

    for category, configs in FEEDBACK_CONFIG.items():
        sorted_configs = sorted(configs, key=lambda x: x["threshold"], reverse=True)

        for config in sorted_configs:
            if category in feedback_added_for_category:
                continue

            ratio = analysis_results.get(f"{category}_ratio", 0)
            condition = config.get("condition", "greater_than")

            should_add_feedback = False
            if condition == "greater_than" and ratio > config["threshold"]:
                should_add_feedback = True
            elif condition == "less_than" and ratio < config["threshold"]:
                should_add_feedback = True

            if should_add_feedback:
                format_kwargs = {"ratio": ratio}
                if "{example}" in config["format"]:
                    examples_with_scores = analysis_results.get(
                        f"{category}_examples", []
                    )
                    if not examples_with_scores:
                        continue
                    best_example_message = max(
                        examples_with_scores, key=lambda x: x[1]
                    )[0]
                    format_kwargs["example"] = best_example_message

                feedback.append(config["format"].format(**format_kwargs))
                feedback_added_for_category.add(category)

    if not feedback:
        feedback.append(DEFAULT_FEEDBACK)

    return feedback


def analyze_conversation(df: pd.DataFrame, user_name: str, sentiment_model, classifier):
    """
    AI 모델을 사용하여 대화 내용을 분석하고 동적 피드백을 생성합니다.
    """
    user_df = df[df["User"] == user_name]

    if user_df.empty:
        return {"error": f"'{user_name}' 사용자의 대화가 없습니다."}

    messages = user_df["Message"].dropna().tolist()
    messages = [msg for msg in messages if msg != "이모티콘"]
    if len(messages) > 500:
        messages = random.sample(messages, 500)

    messages = [msg[:400] for msg in messages]

    if not messages:
        return {"total_messages": 0, "feedback": ["분석할 메시지가 없습니다."]}

    total_messages = len(messages)

    sentiments = sentiment_model(messages)
    neg_count = sum(
        1 for s in sentiments if "부정" in s["label"] or "neg" in s["label"].lower()
    )
    pos_count = sum(
        1 for s in sentiments if "긍정" in s["label"] or "pos" in s["label"].lower()
    )
    negative_ratio = (neg_count / total_messages) * 100 if total_messages > 0 else 0
    positive_ratio = (pos_count / total_messages) * 100 if total_messages > 0 else 0

    candidate_labels = list(CATEGORY_MAP.keys())
    category_counts = {label: 0 for label in candidate_labels}
    category_examples: Dict[str, List[tuple[str, float]]] = {
        label: [] for label in candidate_labels
    }

    results = classifier(
        messages,
        candidate_labels,
        multi_label=False,
        hypothesis_template="이 문장의 내용은 {}이다.",
    )

    for i, result in enumerate(results):
        top_label = result["labels"][0]
        top_score = result["scores"][0]
        category_counts[top_label] += 1
        if CATEGORY_MAP.get(top_label) in PRIMARY_ANALYSIS_CATEGORIES:
            category_examples[top_label].append((messages[i], top_score))

    analysis_results = {
        "total_messages": total_messages,
        "negative_ratio": round(negative_ratio, 2),
        "positive_ratio": round(positive_ratio, 2),
    }

    for kor_label, eng_label in CATEGORY_MAP.items():
        ratio = (
            round((category_counts.get(kor_label, 0) / total_messages) * 100, 2)
            if total_messages > 0
            else 0
        )
        analysis_results[f"{eng_label}_ratio"] = ratio
        if eng_label in PRIMARY_ANALYSIS_CATEGORIES:
            analysis_results[f"{eng_label}_examples"] = category_examples.get(
                kor_label, []
            )

    feedback = generate_dynamic_feedback(analysis_results)
    analysis_results["feedback"] = feedback

    final_results = {
        k: v for k, v in analysis_results.items() if not k.endswith("_examples")
    }

    return final_results
