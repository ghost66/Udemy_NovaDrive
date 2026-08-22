import calendar
from datetime import date
from typing import Optional

from . import queries


def periodo_e_mes_corrente(data_inicio: date, data_fim: date, hoje: Optional[date] = None) -> bool:
    hoje = hoje or date.today()
    return (
        (data_inicio.year, data_inicio.month) == (hoje.year, hoje.month)
        and (data_fim.year, data_fim.month) == (hoje.year, hoje.month)
    )


def calcular_projecao_run_rate(hoje: Optional[date] = None) -> dict:
    hoje = hoje or date.today()
    primeiro_dia_mes = hoje.replace(day=1)
    dias_passados = hoje.day
    dias_no_mes = calendar.monthrange(hoje.year, hoje.month)[1]

    faturamento_ate_hoje = queries.get_faturamento_periodo(primeiro_dia_mes, hoje)
    projecao_mes = (faturamento_ate_hoje / dias_passados) * dias_no_mes

    return {
        "faturamento_ate_hoje": faturamento_ate_hoje,
        "projecao_mes": projecao_mes,
        "dias_passados": dias_passados,
        "dias_no_mes": dias_no_mes,
    }
