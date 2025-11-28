"""
Exemplo Completo de Uso do Sistema Totem Flexmedia
Demonstra todo o fluxo: coleta → limpeza → análise → ML → visualização
"""

import sys
import os
from datetime import datetime

# Adiciona src ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_collector import DataCollector
from src.data_cleaning import DataCleaner
from src.analysis.data_analysis import DataAnalyzer
from src.ml.touch_classifier import TouchClassifier
from src.database.db_connection import DatabaseManager

def main():
    print("=" * 60)
    print("EXEMPLO COMPLETO - TOTEM FLEXMEDIA")
    print("=" * 60)
    
    # 1. COLETA DE DADOS
    print("\n[1/5] COLETANDO DADOS DOS SENSORES...")
    print("-" * 60)
    
    collector = DataCollector("TOTEM-001")
    
    # Coleta 3 sessões de exemplo
    for i in range(3):
        print(f"Coletando sessão {i+1}/3...")
        stats = collector.collect_and_store(duration_seconds=20)
        print(f"  ✓ {stats['events_stored']} eventos armazenados")
        print(f"  ✓ {stats['touch_events']} toques detectados")
    
    collector.db.close()
    print("✓ Coleta concluída!\n")
    
    # 2. LIMPEZA DE DADOS
    print("[2/5] LIMPANDO E VALIDANDO DADOS...")
    print("-" * 60)
    
    cleaner = DataCleaner()
    results = cleaner.clean_all()
    
    print(f"  ✓ {results['duplicates_removed']} duplicados removidos")
    print(f"  ✓ {results['invalid_records_fixed']} registros inválidos corrigidos")
    print(f"  ✓ {results['timestamps_standardized']} timestamps padronizados")
    
    # Relatório de qualidade
    report = cleaner.get_data_quality_report()
    print(f"\n  Relatório de Qualidade:")
    print(f"    • Total de registros: {report.get('total_records', 0)}")
    print(f"    • Score de qualidade: {report.get('quality_score', 0)}%")
    
    cleaner.db.close()
    print("✓ Limpeza concluída!\n")
    
    # 3. ANÁLISE ESTATÍSTICA
    print("[3/5] REALIZANDO ANÁLISE ESTATÍSTICA...")
    print("-" * 60)
    
    analyzer = DataAnalyzer()
    analysis_report = analyzer.generate_full_report("TOTEM-001")
    
    if 'descriptive_stats' in analysis_report:
        stats = analysis_report['descriptive_stats']
        print("  Estatísticas Descritivas:")
        
        if 'touch' in stats:
            touch_stats = stats['touch']
            print(f"    • Toques: {touch_stats.get('total_events', 0)} eventos")
            print(f"    • Taxa de ativação: {touch_stats.get('activation_rate', 0)}%")
        
        if 'ldr' in stats:
            ldr_stats = stats['ldr']
            print(f"    • LDR - Média: {ldr_stats.get('mean', 0)}")
            print(f"    • LDR - Min/Max: {ldr_stats.get('min', 0)}/{ldr_stats.get('max', 0)}")
    
    if 'engagement_metrics' in analysis_report:
        engagement = analysis_report['engagement_metrics']
        print(f"\n  Métricas de Engajamento:")
        print(f"    • Toques médios por sessão: {engagement.get('avg_touches_per_session', 0)}")
        print(f"    • Taxa de engajamento: {engagement.get('engagement_rate', 0)}%")
    
    analyzer.db.close()
    print("✓ Análise concluída!\n")
    
    # 4. MACHINE LEARNING
    print("[4/5] TREINANDO MODELO DE MACHINE LEARNING...")
    print("-" * 60)
    
    classifier = TouchClassifier()
    train_results = classifier.train()
    
    print(f"  ✓ Modelo treinado com sucesso!")
    print(f"    • Acurácia: {train_results['accuracy']:.2%}")
    print(f"    • Dados de treino: {train_results['train_size']}")
    print(f"    • Dados de teste: {train_results['test_size']}")
    
    # Testa algumas predições
    print("\n  Testando Predições:")
    test_cases = [
        {'duration': 0.5, 'session_duration': 30, 'total_touches': 2},
        {'duration': 1.5, 'session_duration': 60, 'total_touches': 5},
    ]
    
    for case in test_cases:
        pred = classifier.predict(**case)
        print(f"    • Duração {case['duration']}s → {pred['predicted_type']} "
              f"(confiança: {pred['confidence']:.1%})")
    
    # Salva modelo
    classifier.save_model('src/ml/models/touch_classifier.pkl')
    print("  ✓ Modelo salvo!")
    
    classifier.db.close()
    print("✓ ML concluído!\n")
    
    # 5. ESTATÍSTICAS FINAIS
    print("[5/5] ESTATÍSTICAS FINAIS DO BANCO...")
    print("-" * 60)
    
    db = DatabaseManager()
    stats = db.get_totem_stats("TOTEM-001")
    
    if stats:
        stat = stats[0]
        print(f"  • Total de sessões: {stat.get('total_sessions', 0)}")
        print(f"  • Total de toques: {stat.get('total_touches', 0)}")
        print(f"  • Score médio de interação: {stat.get('avg_interaction_score', 0):.2f}")
        print(f"  • Duração média de sessão: {stat.get('avg_session_duration', 0):.2f}s")
    
    db.close()
    print("✓ Estatísticas obtidas!\n")
    
    # CONCLUSÃO
    print("=" * 60)
    print("EXEMPLO CONCLUÍDO COM SUCESSO!")
    print("=" * 60)
    print("\nPróximos passos:")
    print("  1. Execute o dashboard: streamlit run src/dashboard/app.py")
    print("  2. Visualize os dados coletados")
    print("  3. Teste o modelo ML no dashboard")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Erro durante execução: {e}")
        import traceback
        traceback.print_exc()

