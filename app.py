import re
import sqlite3
from pathlib import Path
from flask import Flask, request, redirect, render_template_string

app = Flask(__name__)

# 🔧 CONFIGURAÇÕES BÁSICAS
WHATSAPP_NUMBER = "5511988180989"  # Número comercial GÁS USINA (DDD do país + DDD + número)
WHATSAPP_MESSAGE = "Olá! Gostaria de pedir gás da GÁS USINA."  # Mensagem automática

DB_PATH = Path("clientes.db")


def get_db():
    """Abre conexão com o banco SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Cria a tabela de clientes, se ainda não existir."""
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telefone TEXT UNIQUE NOT NULL,
            criado_em TEXT NOT NULL
        );
        """
    )
    conn.commit()
    conn.close()


# Inicializa o banco ao iniciar a aplicação
init_db()

HTML_PAGE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>GÁS USINA - Peça seu gás pelo WhatsApp</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: Arial, sans-serif; }
    body {
      background: #f5f5f5;
      color: #222;
    }
    .page {
      max-width: 900px;
      margin: 0 auto;
      padding: 20px 16px 40px;
    }
    header {
      text-align: center;
      margin-bottom: 24px;
    }
    .logo {
      font-size: 32px;
      font-weight: 800;
      color: #e65100;
      letter-spacing: 1px;
    }
    .slogan {
      font-size: 14px;
      color: #555;
      margin-top: 4px;
    }
    .main-card {
      background: #ffffff;
      border-radius: 16px;
      padding: 18px 16px 24px;
      box-shadow: 0 4px 14px rgba(0,0,0,0.08);
      margin-bottom: 20px;
    }
    .main-title {
      font-size: 18px;
      font-weight: 700;
      margin-bottom: 8px;
    }
    .main-text {
      font-size: 14px;
      color: #444;
      margin-bottom: 14px;
    }
    form {
      margin-bottom: 4px;
    }
    .field-label {
      font-size: 13px;
      margin-bottom: 4px;
      color: #444;
    }
    input[type="tel"] {
      width: 100%;
      padding: 10px 12px;
      margin-bottom: 10px;
      border-radius: 8px;
      border: 1px solid #ccc;
      font-size: 14px;
    }
    button[type="submit"] {
      width: 100%;
      padding: 11px 12px;
      border-radius: 999px;
      border: none;
      background: #25D366;
      color: #fff;
      font-size: 15px;
      font-weight: 600;
      cursor: pointer;
    }
    button[type="submit"]:hover {
      opacity: 0.96;
    }
    .msg-erro {
      font-size: 13px;
      color: #b00020;
      margin-top: 6px;
    }
    .info-extra {
      font-size: 11px;
      color: #777;
      margin-top: 6px;
    }
    .section {
      background: #ffffff;
      border-radius: 16px;
      padding: 16px 14px 18px;
      box-shadow: 0 4px 14px rgba(0,0,0,0.06);
      margin-bottom: 16px;
    }
    .section-title {
      font-size: 16px;
      font-weight: 700;
      margin-bottom: 8px;
      color: #333;
    }
    .section p {
      font-size: 14px;
      color: #444;
      margin-bottom: 6px;
      line-height: 1.4;
    }
    .badge-ref {
      display: inline-block;
      font-size: 12px;
      background: #fff3cd;
      color: #7a5a00;
      padding: 4px 8px;
      border-radius: 999px;
      margin-top: 4px;
    }
    .buttons-row {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 10px;
    }
    .btn-link {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 9px 14px;
      border-radius: 999px;
      font-size: 13px;
      text-decoration: none;
      border: 1px solid #1976d2;
      color: #1976d2;
      background: #e3f2fd;
      cursor: pointer;
    }
    .btn-link:hover {
      background: #d1e7fb;
    }
    .photos-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
      gap: 10px;
      margin-top: 10px;
    }
    .photo-card {
      border-radius: 10px;
      overflow: hidden;
      background: #eee;
      height: 120px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 12px;
      color: #555;
    }
    .photo-card img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }
    footer {
      margin-top: 16px;
      text-align: center;
      font-size: 11px;
      color: #777;
    }

    @media (min-width: 720px) {
      .main-layout {
        display: grid;
        grid-template-columns: 1.2fr 1fr;
        gap: 18px;
      }
    }
  </style>
</head>
<body>
  <div class="page">
    <header>
      <div class="logo">GÁS USINA</div>
      <div class="slogan">Seu gás rápido, seguro e perto de você.</div>
    </header>

    <div class="main-layout">
      <!-- BLOCO PRINCIPAL: PEDIDO PELO WHATSAPP -->
      <div class="main-card">
        <div class="main-title">Peça seu gás pelo WhatsApp</div>
        <p class="main-text">
          Digite seu número de WhatsApp para fazer seu pedido de gás. Nós
          registramos seu contato e você é direcionado direto para o nosso atendimento.
        </p>

        <form method="post">
          <div class="field-label">Seu WhatsApp (com DDD):</div>
          <input
            type="tel"
            name="telefone"
            placeholder="Ex: 11 98818-0989"
            value="{{ phone_value }}"
            required
          >
          <button type="submit">Continuar no WhatsApp</button>
        </form>

        {% if error_message %}
        <div class="msg-erro">{{ error_message }}</div>
        {% endif %}

        <div class="info-extra">
          Atendimento pelo WhatsApp: todos os dias, das 8h às 22h.
        </div>
      </div>

      <!-- BLOCO: COMO CHEGAR -->
      <div class="section">
        <div class="section-title">Como chegar ao depósito GÁS USINA</div>
        <p>
          <strong>Endereço:</strong><br>
          Rua Exemplo, 123 – Bairro Central<br>
          Cidade/UF – CEP 00000-000
        </p>
        <p>
          <strong>Pontos de referência:</strong><br>
          • 200m após o Supermercado Exemplo<br>
          • Ao lado do Posto de Combustível Modelo<br>
          • Fácil acesso pela Avenida Principal
        </p>
        <span class="badge-ref">Fácil estacionamento em frente ao depósito</span>

        <div class="buttons-row">
          <a
            class="btn-link"
            href="https://www.google.com/maps/search/?api=1&query=Gas+Usina,+Rua+Exemplo+123,+Cidade+UF"
            target="_blank"
            rel="noopener noreferrer"
          >
            🗺️ Abrir no Google Maps
          </a>
          <!-- Se quiser usar Waze no futuro, troque o link abaixo pela sua lat/long -->
          <a
            class="btn-link"
            href="https://waze.com/ul"
            target="_blank"
            rel="noopener noreferrer"
          >
            🚗 Ir com Waze
          </a>
        </div>

        <p class="info-extra">
          Horário de atendimento no depósito: segunda a sábado, das 8h às 18h.
        </p>
      </div>
    </div>

    <!-- BLOCO: FOTOS DO DEPÓSITO -->
    <div class="section">
      <div class="section-title">Fotos do nosso depósito</div>
      <p>
        Conheça um pouco da estrutura da GÁS USINA. Local seguro, organizado e pronto
        para atender você com rapidez.
      </p>

      <div class="photos-grid">
        <!-- Quando você tiver as fotos, salve em static/img/ e troque os src abaixo -->
        <div class="photo-card">
          <span>Foto do depósito 1</span>
          <!-- Exemplo com imagem real:
          <img src="/static/img/deposito1.jpg" alt="Depósito GÁS USINA 1">
          -->
        </div>
        <div class="photo-card">
          <span>Foto do depósito 2</span>
        </div>
        <div class="photo-card">
          <span>Foto do caminhão de entrega</span>
        </div>
        <div class="photo-card">
          <span>Foto dos botijões organizados</span>
        </div>
      </div>
    </div>

    <footer>
      GÁS USINA &middot; Pedido rápido pelo WhatsApp &middot; Depósito físico à sua disposição.
    </footer>
  </div>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    import urllib.parse

    error_message = None
    phone_value = ""

    if request.method == "POST":
        raw_phone = request.form.get("telefone", "")
        phone_value = raw_phone

        # Mantém só dígitos no telefone do cliente
        telefone_cliente = re.sub(r"\\D", "", raw_phone)

        if len(telefone_cliente) < 10:
            error_message = "Por favor, informe um número de WhatsApp válido com DDD."
        else:
            # Salva no banco (ignora se já existir)
            conn = get_db()
            conn.execute(
                "INSERT OR IGNORE INTO clientes (telefone, criado_em) VALUES (?, datetime('now'))",
                (telefone_cliente,),
            )
            conn.commit()
            conn.close()

            # Monta o link do WhatsApp e redireciona direto
            encoded_msg = urllib.parse.quote(WHATSAPP_MESSAGE)
            whatsapp_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={encoded_msg}"
            return redirect(whatsapp_url)

    # Se for GET ou se houve erro, renderiza a página normalmente
    return render_template_string(
      HTML_PAGE,
      error_message=error_message,
      phone_value=phone_value,
    )


if __name__ == "__main__":
    app.run(debug=True)
