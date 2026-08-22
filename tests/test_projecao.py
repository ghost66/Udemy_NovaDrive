from datetime import date

import pytest

from src import projecao


def test_periodo_e_mes_corrente_true_quando_periodo_e_o_mes_inteiro():
    hoje = date(2026, 2, 10)
    assert projecao.periodo_e_mes_corrente(date(2026, 2, 1), date(2026, 2, 10), hoje) is True


def test_periodo_e_mes_corrente_false_quando_cruza_meses():
    hoje = date(2026, 2, 10)
    assert projecao.periodo_e_mes_corrente(date(2026, 1, 15), date(2026, 2, 10), hoje) is False


def test_periodo_e_mes_corrente_false_quando_e_mes_passado():
    hoje = date(2026, 2, 10)
    assert projecao.periodo_e_mes_corrente(date(2026, 1, 1), date(2026, 1, 31), hoje) is False


def test_calcular_projecao_run_rate(monkeypatch):
    hoje = date(2026, 2, 10)
    monkeypatch.setattr(projecao.queries, "get_faturamento_periodo", lambda inicio, fim: 100000.0)

    resultado = projecao.calcular_projecao_run_rate(hoje)

    assert resultado["dias_passados"] == 10
    assert resultado["dias_no_mes"] == 28
    assert resultado["faturamento_ate_hoje"] == 100000.0
    assert resultado["projecao_mes"] == pytest.approx(100000.0 / 10 * 28)
