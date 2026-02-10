"""
Script para executar consultas TOP 10 nas tabelas Protheus e inspecionar estrutura/dados.
Ajuda a: (1) ver por que B1_DESC vem vazio (B1_FILIAL, nomes de coluna);
         (2) validar campos de pedido/NF/entrega para lógica da Carteira.

Uso (na pasta mypcpweb):
  python -m backend.run_explore
  python -m backend.run_explore --file saida.txt
"""
import argparse
import sys
from pathlib import Path

# Garante que a pasta mypcpweb e backend estão no path
# (connection.py usa "from config import AppConfig", que resolve para backend/config quando backend está no path)
_mypcpweb = Path(__file__).resolve().parent.parent
_backend = _mypcpweb / "backend"
for _p in (_backend, _mypcpweb):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from config import AppConfig
from database.connection import get_db_connection
from database.explore_queries import get_all_explore_queries


def run(cnxn, empresa: str = "010", output_file: str | None = None):
    out = open(output_file, "w", encoding="utf-8") if output_file else sys.stdout
    try:
        cursor = cnxn.cursor()
        for name, sql in get_all_explore_queries(empresa):
            print(f"\n{'='*60}\nTOP 10: {name}\n{'='*60}", file=out)
            try:
                cursor.execute(sql)
                cols = [c[0] for c in cursor.description]
                print("Colunas:", cols, file=out)
                rows = cursor.fetchall()
                for i, row in enumerate(rows, 1):
                    print(dict(zip(cols, row)), file=out)
            except Exception as e:
                print(f"Erro: {e}", file=out)
        if output_file:
            out.close()
            print(f"Resultados gravados em: {output_file}", file=sys.stdout)
    finally:
        if output_file and out != sys.stdout:
            out.close()


def main():
    parser = argparse.ArgumentParser(description="Explorar tabelas Protheus (TOP 10)")
    parser.add_argument("--file", "-f", help="Gravar saída em arquivo")
    parser.add_argument("--empresa", default="010", help="Código empresa (ex: 010)")
    args = parser.parse_args()
    config = AppConfig.from_env()
    if not config.db_server or not config.db_name:
        print("Configure DB_SERVER e DB_NAME (ou DB_DATABASE) no .env")
        sys.exit(1)
    cnxn = get_db_connection(config)
    run(cnxn, empresa=config.empresa or args.empresa, output_file=args.file)
    cnxn.close()


if __name__ == "__main__":
    main()
