import json
from sklearn.metrics import classification_report
from app.services.classification_service import classify_comment

def run_evaluations():
    print ("--- Iniciando a avaliação do modelo de classificação ---")

    with open ('golden_dataset.json', 'r', encoding='utf-8') as f:
        golden_dataset = json.load(f)

    true_labels = []
    predicted_labels = []

    print (f"Avaliando {len(golden_dataset)} amostras...")

    for item in golden_dataset:
        text = item['text']
        true_category = item['expected_category']

        classification_result = classify_comment(text)

        if classification_result and 'categoria' in classification_result:
            predicted_category = classification_result['categoria']

            true_labels.append(true_category)
            predicted_labels.append(predicted_category)
            print(f"    - Texto: '{text[:30]}...' | Real: {true_category} | Previsto: {predicted_category}")
        else:
            print(f"    - FALHA ao classificar o texto: '{text[:30]}...'")

    print("\n--- Relatório de métricas ---")

    if not true_labels:
        print("Nenhuma classificação foi bem-sucedida. Não é possível gerar o relatório.")
        return
    
    report = classification_report(true_labels, predicted_labels, zero_division=0)
    print(report)

    print("--- Avaliação Concluída ---")

if __name__ == "__main__":
    run_evaluations()