import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from api.models import VwSentinelaCasoCompleto, SentinelaFilaAlertas, SentinelaReconciliacaoLog
from .field_rules import (
    normalize_text,
    normalize_sex,
    normalize_race,
    parse_date,
    match_names,
    jaro_winkler_score
)

logger = logging.getLogger(__name__)

class IMLComparator:
    """
    Comparador para reconciliação de dados entre CONTROLE_MORTE e o IML (SGOU).
    """

    def __init__(self):
        pass

    def compare_linked_records(self, session: Session) -> int:
        """
        Compara registros que já possuem NIC vinculado e busca divergências de PII.
        """
        logger.info("Iniciando comparação de registros vinculados do IML...")
        
        # Seleciona casos que possuem NIC ou NIC_IML preenchidos
        casos = session.query(VwSentinelaCasoCompleto).filter(
            (VwSentinelaCasoCompleto.NIC.isnot(None)) | 
            (VwSentinelaCasoCompleto.NIC_IML.isnot(None))
        ).all()
        
        logger.info(f"Localizados {len(casos)} casos com vínculo do IML para auditoria.")
        divergencias_encontradas = 0
        
        for caso in casos:
            nic = caso.NIC or caso.NIC_IML
            id_cm = caso.ID_CONTROLE_MORTE
            bo_pc = caso.BO_PC
            cad = caso.CAD
            
            # 1. Comparar NOME_VITIMA vs NOM_VITIMA_IML
            if caso.NOME_VITIMA and caso.NOM_VITIMA_IML:
                name_match, score = match_names(caso.NOME_VITIMA, caso.NOM_VITIMA_IML)
                if not name_match:
                    self._registrar_divergencia(
                        session=session,
                        id_cm=id_cm,
                        fonte="IML",
                        campo_mestra="NOME_VITIMA",
                        val_mestra=caso.NOME_VITIMA,
                        campo_fonte="NOM_VITIMA_IML",
                        val_fonte=caso.NOM_VITIMA_IML,
                        tipo="VALOR_DIFERENTE",
                        score=score,
                        tipo_alerta="Divergência de Nome da Vítima (IML)",
                        prioridade=4,
                        nic=nic, bo_pc=bo_pc, cad=cad
                    )
                    divergencias_encontradas += 1

            # 2. Comparar MAE_VITIMA vs MAE_IML
            if caso.MAE_VITIMA and caso.MAE_IML:
                m_match, score = match_names(caso.MAE_VITIMA, caso.MAE_IML, threshold=85.0)
                if not m_match:
                    self._registrar_divergencia(
                        session=session,
                        id_cm=id_cm,
                        fonte="IML",
                        campo_mestra="MAE_VITIMA",
                        val_mestra=caso.MAE_VITIMA,
                        campo_fonte="MAE_IML",
                        val_fonte=caso.MAE_IML,
                        tipo="VALOR_DIFERENTE",
                        score=score,
                        tipo_alerta="Divergência de Filiação Materna (IML)",
                        prioridade=2,
                        nic=nic, bo_pc=bo_pc, cad=cad
                    )
                    divergencias_encontradas += 1

            # 3. Comparar SEXO_VITIMA vs SEXO
            if caso.SEXO_VITIMA and caso.SEXO:
                s_mestra = normalize_sex(caso.SEXO_VITIMA)
                s_fonte = normalize_sex(caso.SEXO)
                if s_mestra and s_fonte and s_mestra != s_fonte:
                    self._registrar_divergencia(
                        session=session,
                        id_cm=id_cm,
                        fonte="IML",
                        campo_mestra="SEXO_VITIMA",
                        val_mestra=caso.SEXO_VITIMA,
                        campo_fonte="SEXO",
                        val_fonte=caso.SEXO,
                        tipo="VALOR_DIFERENTE",
                        score=0.0,
                        tipo_alerta="Divergência de Sexo (IML)",
                        prioridade=4,
                        nic=nic, bo_pc=bo_pc, cad=cad
                    )
                    divergencias_encontradas += 1

            # 4. Comparar COR_RACA_VITIMA vs ETNIA
            if caso.COR_RACA_VITIMA and caso.ETNIA:
                r_mestra = normalize_race(caso.COR_RACA_VITIMA)
                r_fonte = normalize_race(caso.ETNIA)
                if r_mestra and r_fonte and r_mestra != r_fonte:
                    self._registrar_divergencia(
                        session=session,
                        id_cm=id_cm,
                        fonte="IML",
                        campo_mestra="COR_RACA_VITIMA",
                        val_mestra=caso.COR_RACA_VITIMA,
                        campo_fonte="ETNIA",
                        val_fonte=caso.ETNIA,
                        tipo="VALOR_DIFERENTE",
                        score=0.0,
                        tipo_alerta="Divergência de Cor/Raça (IML)",
                        prioridade=2,
                        nic=nic, bo_pc=bo_pc, cad=cad
                    )
                    divergencias_encontradas += 1

            # 5. Comparar NASC_VITIMA vs NASCIMENTO
            if caso.NASC_VITIMA and caso.NASCIMENTO:
                dt_mestra = parse_date(caso.NASC_VITIMA)
                dt_fonte = parse_date(caso.NASCIMENTO)
                if dt_mestra and dt_fonte:
                    # Permite diferença de 1 ano pois o IML às vezes trunca o ano de nascimento
                    if abs(dt_mestra.year - dt_fonte.year) > 1:
                        self._registrar_divergencia(
                            session=session,
                            id_cm=id_cm,
                            fonte="IML",
                            campo_mestra="NASC_VITIMA",
                            val_mestra=caso.NASC_VITIMA,
                            campo_fonte="NASCIMENTO",
                            val_fonte=caso.NASCIMENTO,
                            tipo="VALOR_DIFERENTE",
                            score=0.0,
                            tipo_alerta="Divergência de Data de Nascimento (IML)",
                            prioridade=2,
                            nic=nic, bo_pc=bo_pc, cad=cad
                        )
                        divergencias_encontradas += 1

            # 6. Comparar STATUS (Necrópsia) vs STATUS_IML
            if caso.STATUS_IML and caso.STATUS:
                # Se na Controle Morte diz que a necrópsia está CONCLUIDA mas no IML está PENDENTE (ou vice-versa)
                # Nota: Controle de Morte costuma ter status do caso, mas no seeder temos STATUS_NECROPSIA mapeado.
                # Vamos comparar com STATUS_IML.
                pass

        session.commit()
        logger.info(f"Comparação de vinculados concluída. {divergencias_encontradas} divergências detectadas.")
        return divergencias_encontradas

    def detect_evolution_attempts(self, session: Session) -> int:
        """
        Procura por novas entradas no IML que possam ser evoluções de tentativas registradas na Mestra.
        Compara data do fato com data de óbito ou entrada no IML com uma janela estendida de até 540 dias.
        Aplica mitigações de performance:
        1. Limite temporal de 18 meses (540 dias) para monitoramento de tentativas ativas.
        2. Pre-filtering rápido por primeira letra de nome antes do cálculo Jaro-Winkler.
        3. Integração com a tabela de notificações do IML.
        """
        logger.info("Iniciando detecção de evolução de tentativas para óbito no IML...")
        
        # Obter data limite de 18 meses (540 dias) para monitoramento
        limite_monitoramento = datetime.now() - timedelta(days=540)
        
        # 1. Obter tentativas ativas da Mestra
        todas_tentativas = session.query(VwSentinelaCasoCompleto).filter(
            VwSentinelaCasoCompleto.SUBJETIVIDADE.ilike("%TENTATIVA%"),
            VwSentinelaCasoCompleto.NIC.is_(None),
            VwSentinelaCasoCompleto.NIC_IML.is_(None)
        ).all()
        
        # Filtrar tentativas ativas nos últimos 18 meses
        tentativas = []
        for t in todas_tentativas:
            dt_tent = parse_date(t.DATA_HORA_FATO)
            if dt_tent and dt_tent >= limite_monitoramento:
                tentativas.append(t)
                
        if not tentativas:
            logger.info("Nenhuma tentativa ativa recente (nos últimos 18 meses) localizada na Controle Morte.")
            return 0
            
        logger.info(f"Localizadas {len(tentativas)} tentativas ativas recentes para análise.")
        
        # 2. Obter todas as entradas do IML
        corpos_iml = session.query(VwSentinelaCasoCompleto).filter(
            VwSentinelaCasoCompleto.NIC_IML.isnot(None)
        ).all()
        
        # Registrar notificações para novas entradas do IML
        # Buscaremos se existem novos corpos cadastrados
        from api.models import SentinelaNotificacaoIML
        
        evolucao_alertas = 0
        
        for tent in tentativas:
            dt_tent = parse_date(tent.DATA_HORA_FATO)
            if not dt_tent:
                continue
                
            for corpo in corpos_iml:
                if tent.ID_CONTROLE_MORTE == corpo.ID_CONTROLE_MORTE:
                    continue
                    
                dt_corpo = parse_date(corpo.DATA_HORA_FATO) or parse_date(corpo.IML_ENTRADA)
                if not dt_corpo:
                    continue
                    
                # Diferença de dias (janela estendida de 540 dias pós-tentativa)
                delta_days = (dt_corpo - dt_tent).days
                if delta_days < 0 or delta_days > 540:
                    continue
                    
                # Mitigação 2: Pre-filtering por primeira letra
                if tent.NOME_VITIMA and corpo.NOM_VITIMA_IML:
                    n1 = normalize_text(tent.NOME_VITIMA)
                    n2 = normalize_text(corpo.NOM_VITIMA_IML)
                    if n1 and n2 and n1[0] != n2[0]:
                        continue  # Letras iniciais diferentes, descarta rapidamente
                
                # 3. Match por BO_PC ou Nome da Vítima
                bo_match = (tent.BO_PC and corpo.BO_PC and tent.BO_PC == corpo.BO_PC)
                
                name_match = False
                score = 0.0
                if tent.NOME_VITIMA and corpo.NOM_VITIMA_IML:
                    name_match, score = match_names(tent.NOME_VITIMA, corpo.NOM_VITIMA_IML)
                
                if bo_match or name_match:
                    logger.warning(f"Suspeita detectada: Tentativa ID {tent.ID_CONTROLE_MORTE} pode ter evoluído para óbito. Corpo NIC {corpo.NIC_IML} (Match Score: {score}%)")
                    
                    self._registrar_divergencia(
                        session=session,
                        id_cm=tent.ID_CONTROLE_MORTE,
                        fonte="IML",
                        campo_mestra="SUBJETIVIDADE",
                        val_mestra="TENTATIVA",
                        campo_fonte="NIC_IML",
                        val_fonte=corpo.NIC_IML,
                        tipo="CORRELACAO_PROBABILISTICA",
                        score=max(score, 100.0 if bo_match else 0.0),
                        tipo_alerta="Suspeita de Evolução de Tentativa para Óbito (IML)",
                        prioridade=3,
                        nic=corpo.NIC_IML,
                        bo_pc=tent.BO_PC or corpo.BO_PC,
                        cad=tent.CAD or corpo.CAD
                    )
                    
                    # Cria notificação na tabela de notificações do IML
                    # Apenas se não existir uma notificação similar
                    notif_existente = session.query(SentinelaNotificacaoIML).filter_by(
                        NIC=corpo.NIC_IML,
                        TIPO_MENSAGEM="Nova evolução identificada"
                    ).first()
                    
                    if not notif_existente:
                        nome_vit = corpo.NOM_VITIMA_IML or tent.NOME_VITIMA
                        nova_notif = SentinelaNotificacaoIML(
                            NIC=corpo.NIC_IML,
                            NOME_VITIMA=nome_vit,
                            STATUS_IML=corpo.STATUS_IML if hasattr(corpo, 'STATUS_IML') else "Entrada",
                            TIPO_MENSAGEM="Nova evolução identificada",
                            LIDO=0
                        )
                        session.add(nova_notif)
                        
                    evolucao_alertas += 1
                    
        session.commit()
        logger.info(f"Varredura de evolução concluída. {evolucao_alertas} suspeitas de óbito geradas.")
        return evolucao_alertas

    def _registrar_divergencia(self, session: Session, id_cm: int, fonte: str,
                              campo_mestra: str, val_mestra: str, campo_fonte: str,
                              val_fonte: str, tipo: str, score: float, tipo_alerta: str,
                              prioridade: int, nic: str = None, bo_pc: str = None,
                              cad: str = None):
        """
        Salva o log de divergência e insere um alerta correspondente na fila de alertas.
        Previne alertas duplicados na fila.
        """
        # Verifica se já existe um alerta idêntico na fila para este caso
        alerta_existente = session.query(SentinelaFilaAlertas).filter_by(
            ID_CONTROLE_MORTE=id_cm,
            TIPO_ALERTA=tipo_alerta
        ).first()
        
        if not alerta_existente:
            novo_alerta = SentinelaFilaAlertas(
                ID_CONTROLE_MORTE=id_cm,
                NIC=nic,
                BO_PC=bo_pc,
                CAD=cad,
                STATUS="Novo",
                PRIORIDADE=prioridade,
                TIPO_ALERTA=tipo_alerta
            )
            session.add(novo_alerta)
            
        # Verifica se já existe esse registro de log ativo
        log_existente = session.query(SentinelaReconciliacaoLog).filter_by(
            ID_CONTROLE_MORTE=id_cm,
            FONTE=fonte,
            CAMPO_MESTRA=campo_mestra,
            STATUS="Pendente"
        ).first()
        
        if not log_existente:
            novo_log = SentinelaReconciliacaoLog(
                ID_CONTROLE_MORTE=id_cm,
                FONTE=fonte,
                CAMPO_MESTRA=campo_mestra,
                VALOR_MESTRA=str(val_mestra) if val_mestra else None,
                CAMPO_FONTE=campo_fonte,
                VALOR_FONTE=str(val_fonte) if val_fonte else None,
                TIPO_DIVERGENCIA=tipo,
                SCORE_SIMILARIDADE=score,
                STATUS="Pendente"
            )
            session.add(novo_log)
