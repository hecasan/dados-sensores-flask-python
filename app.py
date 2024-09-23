from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)
DATABASE = 'database.db'

# Função para inicializar o banco de dados e criar a tabela se não existir
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS dados_sensores (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      sensor_id INTEGER,
                      temperatura REAL,
                      umidade REAL,
                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                      )''')
    conn.commit()
    conn.close()

# Inicializando o banco de dados na inicialização do servidor
init_db()

# Endpoint para inserir dados (POST)
@app.route('/dados-sensores', methods=['POST'])
def inserir_dados():
    dados = request.get_json()
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO dados_sensores (sensor_id, temperatura, umidade) VALUES (?, ?, ?)',
                   (dados['sensor_id'], dados['temperatura'], dados['umidade']))
    conn.commit()
    conn.close()
    return jsonify({"message": "Dados inseridos com sucesso"}), 201

# Endpoint para buscar todos os dados (GET)
@app.route('/dados-sensores', methods=['GET'])
def buscar_dados():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM dados_sensores')
    rows = cursor.fetchall()
    conn.close()
    return jsonify(rows)

# Endpoint para limpar todos os dados da tabela (DELETE)
@app.route('/limpar-dados', methods=['DELETE'])
def limpar_dados():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM dados_sensores')
    conn.commit()
    conn.close()
    return jsonify({"message": "Dados limpos com sucesso"}), 200

# Endpoint para buscar os dados em formato JSON (para uso no gráfico)
@app.route('/dados-sensores-json', methods=['GET'])
def dados_sensores_json():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT timestamp, temperatura, umidade FROM dados_sensores')
    rows = cursor.fetchall()
    conn.close()

    # Separando os dados em listas
    timestamps = [row[0] for row in rows]
    temperaturas = [row[1] for row in rows]
    umidades = [row[2] for row in rows]

    # Retornando um JSON com as listas
    return jsonify({
        "timestamp": timestamps,
        "temperatura": temperaturas,
        "umidade": umidades
    })

# Novo endpoint para buscar dados filtrados por sensor_id (GET)
@app.route('/dados-sensores/<int:sensor_id>', methods=['GET'])
def obter_dados_sensor(sensor_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Consulta para filtrar os dados pelo sensor_id
    cursor.execute('SELECT timestamp, temperatura, umidade FROM dados_sensores WHERE sensor_id = ?', (sensor_id,))
    dados = cursor.fetchall()

    # Transformando os dados em um formato adequado para JSON
    dados_formatados = {
        'timestamp': [linha[0] for linha in dados],
        'temperatura': [linha[1] for linha in dados],
        'umidade': [linha[2] for linha in dados]
    }

    conn.close()
    return jsonify(dados_formatados)

# Endpoint para exibir os gráficos
@app.route('/graficos')
def graficos():
    return render_template('graficos.html')

# Rota para a página principal
@app.route('/')
def index():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM dados_sensores')
    dados = cursor.fetchall()
    conn.close()
    return render_template('index.html', dados=dados)

# Inicia o servidor Flask
if __name__ == '__main__':
    app.run(debug=True)
