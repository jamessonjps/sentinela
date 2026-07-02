import sqlite3

def clear_old_alerts():
    print("Conectando...")
    conn = sqlite3.connect("sentinela.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM SENTINELA_FILA_ALERTAS WHERE TIPO_ALERTA NOT LIKE 'Divergência%';")
    conn.commit()
    print(f"Limpados alertas antigos. {cursor.rowcount} alertas excluídos.")
    conn.close()

if __name__ == "__main__":
    clear_old_alerts()
