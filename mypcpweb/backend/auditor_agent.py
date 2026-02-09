"""Agente auditor inicial para integridade do PCP Shadow."""

from dataclasses import dataclass
from typing import List

from services.pcp_service import PCPService


@dataclass
class AuditorAlert:
    tipo: str
    mensagem: str
    detalhes: dict


class AuditorAgent:
    def __init__(self, pcp_service: PCPService):
        self.pcp_service = pcp_service

    def run(self) -> List[AuditorAlert]:
        alerts: List[AuditorAlert] = []
        alerts.extend(self._ops_encerradas_sem_consumo())
        return alerts

    def _ops_encerradas_sem_consumo(self) -> List[AuditorAlert]:
        """OPs encerradas sem consumo registrado em SD3."""
        results = self.pcp_service.get_ops_encerradas_sem_consumo() or []
        alerts = []
        for row in results:
            alerts.append(
                AuditorAlert(
                    tipo="OP_SEM_CONSUMO",
                    mensagem=(
                        f"OP {row['NumeroOP']} encerrada sem consumo de MP."
                    ),
                    detalhes=row,
                )
            )
        return alerts
