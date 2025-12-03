# supabase_client.py
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Carrega as variáveis do .env aqui dentro
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL ou SUPABASE_ANON_KEY não configurados no .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_table_rows(tabela: str, limit: int = 100):
    """
    Busca linhas de uma tabela do Supabase.
    Retorna sempre uma lista (pode ser vazia).
    """
    response = supabase.table(tabela).select("*").limit(limit).execute()
    return response.data or []