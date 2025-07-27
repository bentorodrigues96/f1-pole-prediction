import fastf1
import mysql.connector
from mysql.connector import Error
import pandas as pd
import os
import time

# Etapa 1: preparar cache do FastF1 SEM usar SQLite
print("🚦 Iniciando importação de dados FastF1...")

# Usar cache em memória ao invés de SQLite
try:
    # Tentar desabilitar cache primeiro
    fastf1.Cache.clear_cache()
    fastf1.Cache.disable_cache()
    print("✅ Cache desabilitado - usando modo sem cache")
except:
    print("⚠️ Continuando sem cache...")

# Etapa 2: conectar ao banco MySQL
def conectar_mysql(tentativa=1):
    try:
        print(f"🔌 Conectando ao MySQL (tentativa {tentativa})...")
        
        # Criar banco se não existir
        conn_temp = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Mazembe30*1234',
            connection_timeout=10
        )
        cursor_temp = conn_temp.cursor()
        cursor_temp.execute("CREATE DATABASE IF NOT EXISTS f1_data")
        cursor_temp.close()
        conn_temp.close()
        
        # Conectar ao banco específico
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Mazembe30*1234',
            database='f1_data',
            connection_timeout=10,
            autocommit=True
        )
        
        # Criar tabela
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS qualifying_results (
                id INT AUTO_INCREMENT PRIMARY KEY,
                year INT NOT NULL,
                grand_prix VARCHAR(100) NOT NULL,
                driver VARCHAR(10) NOT NULL,
                team VARCHAR(50) NOT NULL,
                position INT,
                q1_time VARCHAR(20),
                q2_time VARCHAR(20),
                q3_time VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_entry (year, grand_prix, driver)
            )
        """)
        cursor.close()
        
        print("✅ Conectado ao MySQL")
        return conn
    except Error as e:
        print(f"❌ Erro MySQL: {e}")
        if tentativa < 3:
            time.sleep(2)
            return conectar_mysql(tentativa + 1)
        return None
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return None

# Etapa 3: formatar tempo do FastF1 para string
def format_time(td):
    if pd.isna(td) or td is None:
        return None
    try:
        if hasattr(td, 'total_seconds'):
            total_seconds = td.total_seconds()
            minutes = int(total_seconds // 60)
            seconds = total_seconds % 60
            return f"{minutes}:{seconds:06.3f}"
        else:
            return str(td)
    except:
        return None

# Etapa 4: inserir os dados de qualificação
def inserir_qualifying(conn, ano, circuito, resultados):
    cursor = conn.cursor()
    sucessos = 0
    
    print(f"   → Inserindo {len(resultados)} pilotos...")
    
    for _, row in resultados.iterrows():
        try:
            # Usar INSERT IGNORE para evitar duplicatas
            cursor.execute("""
                INSERT IGNORE INTO qualifying_results (
                    year, grand_prix, driver, team, position,
                    q1_time, q2_time, q3_time
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                ano,
                circuito,
                row.get('Abbreviation', 'UNK'),
                row.get('TeamName', 'Unknown'),
                int(row.get('Position', 0)) if pd.notna(row.get('Position')) else None,
                format_time(row.get('Q1')),
                format_time(row.get('Q2')),
                format_time(row.get('Q3'))
            ))
            if cursor.rowcount > 0:
                sucessos += 1
        except Exception as e:
            print(f"      ⚠️ Erro {row.get('Abbreviation', 'UNK')}: {e}")
    
    cursor.close()
    print(f"   → ✅ {sucessos} pilotos inseridos")

# Etapa 5: função principal
def main():
    conn = conectar_mysql()
    if not conn:
        print("❌ Não foi possível conectar ao MySQL")
        return

    ano = 2025
    
    try:
        print(f"\n📅 Processando temporada {ano}...")
        
        # Teste com poucos GPs primeiro
        for round_num in range(1, 26):  # 3 primeiros GPs
            try:
                print(f"\n🏁 Round {round_num}...")
                
                # Carregar sessão sem cache
                session = fastf1.get_session(ano, round_num, 'Q')
                print(f"   → Carregando dados...")
                session.load()
                
                nome_gp = session.event.get('EventName', f'Round {round_num}')
                print(f"   → 📦 {nome_gp}")
                
                if hasattr(session, 'results') and len(session.results) > 0:
                    inserir_qualifying(conn, ano, nome_gp, session.results)
                else:
                    print(f"   → ⚠️ Sem dados de qualificação")
                
                # Pausa entre requisições
                print(f"   → Aguardando 3 segundos...")
                time.sleep(3)
                
            except Exception as e:
                print(f"   → ❌ Erro no Round {round_num}: {e}")
                continue
                
    except KeyboardInterrupt:
        print("\n⏹️ Interrompido pelo usuário")
    finally:
        conn.close()
        print("\n✅ Conexão fechada")

    print("\n🏁 Processo finalizado!")
    
    # Mostrar estatísticas
    try:
        conn = conectar_mysql()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM qualifying_results")
            total = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT grand_prix) FROM qualifying_results WHERE year = %s", (ano,))
            gps = cursor.fetchone()[0]
            print(f"📊 Total inserido: {total} registros de {gps} GPs")
            cursor.close()
            conn.close()
    except Exception as e:
        print(f"⚠️ Erro ao mostrar estatísticas: {e}")

if __name__ == "__main__":
    main()