from flask import Flask, render_template_string, redirect, request
import urllib.parse
import sqlite3
import os

app = Flask(__name__)

# Caminho do banco de dados
DB_PATH = "dados.db"

# Configuração do WhatsApp da GÁS USINA
WHATSAPP_NUMBER = "5511988180989"
WHATSAPP_MESSAGE = "Olá! Gostaria de falar com a GÁS USINA sobre pedido de gás."


def init_db():
  """Cria o banco de dados e a tabela de pedidos se ainda não existirem."""
  conn = sqlite3.connect(DB_PATH)
  cur = conn.cursor()
  cur.execute(
    """
    CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
        ip TEXT,
        user_agent TEXT
    )
    """
  )
  conn.commit()
  conn.close()


# inicializa o banco quando o app sobe
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
      background: #f3f4f6;
      color: #111827;
    }
    .page {
      max-width: 1024px;
      margin: 0 auto;
      padding: 20px 16px 40px;
    }
    header {
      text-align: center;
      margin-bottom: 24px;
    }
    .logo {
      font-size: 30px;
      font-weight: 800;
      color: #1f2937;
      letter-spacing: 0.04em;
    }
    .slogan {
      font-size: 14px;
      color: #6b7280;
      margin-top: 4px;
    }

    .hero {
      background: linear-gradient(135deg, #2563eb, #22c55e);
      border-radius: 18px;
      padding: 14px 16px;
      color: #ecfeff;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      margin-bottom: 18px;
    }
    .hero-text-main {
      font-size: 18px;
      font-weight: 700;
    }
    .hero-text-sub {
      font-size: 13px;
      opacity: 0.95;
    }
    .hero-tag {
      font-size: 12px;
      background: rgba(15, 23, 42, 0.25);
      padding: 4px 10px;
      border-radius: 999px;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }
    .hero-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #22c55e;
      box-shadow: 0 0 0 4px rgba(34, 197, 94, 0.4);
      animation: pulse 1.4s infinite;
    }
    @keyframes pulse {
      0% { transform: scale(1); opacity: 1; }
      50% { transform: scale(1.2); opacity: 0.6; }
      100% { transform: scale(1); opacity: 1; }
    }

    .layout {
      display: grid;
      gap: 18px;
    }
    @media (min-width: 820px) {
      .layout {
        grid-template-columns: 1.2fr 1fr;
        align-items: flex-start;
      }
    }

    /* Card de chat WhatsApp */
    .chat-card {
      background: #ffffff;
      border-radius: 18px;
      padding: 18px 16px 22px;
      box-shadow: 0 8px 24px rgba(15, 23, 42, 0.09);
      margin-bottom: 16px;
    }
    .chat-header {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 14px;
    }
    .chat-avatar {
      width: 42px;
      height: 42px;
      border-radius: 50%;
      overflow: hidden;
      background: #ffffff;
      border: 2px solid #e5e7eb;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .chat-avatar-img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }
    .chat-agent {
      display: flex;
      flex-direction: column;
      gap: 2px;
    }
    .chat-agent-name {
      font-size: 14px;
      font-weight: 700;
      color: #111827;
    }
    .chat-agent-status {
      font-size: 12px;
      color: #16a34a;
      display: flex;
      align-items: center;
      gap: 4px;
    }
    .status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #16a34a;
      box-shadow: 0 0 0 4px rgba(22, 163, 74, 0.35);
      animation: pulse 1.4s infinite;
    }
    .chat-body {
      background: #e0f2fe;
      border-radius: 14px;
      padding: 10px 12px;
      font-size: 13px;
      color: #111827;
      margin-bottom: 14px;
    }
    .chat-body p + p {
      margin-top: 6px;
    }
    .chat-info {
      font-size: 12px;
      color: #6b7280;
      margin-bottom: 10px;
    }
    .chat-info strong {
      color: #111827;
    }
    .chat-info .small-note {
      display: block;
      margin-top: 4px;
      font-size: 11px;
      color: #9ca3af;
    }
    .whatsapp-btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      text-decoration: none;
      background: #22c55e;
      color: #ffffff;
      font-weight: 600;
      font-size: 15px;
      padding: 11px 16px;
      border-radius: 999px;
      box-shadow: 0 10px 26px rgba(34, 197, 94, 0.55);
    }
    .whatsapp-btn span {
      font-size: 18px;
    }
    .whatsapp-btn:hover {
      opacity: 0.96;
    }

    /* Card lateral: QR + mapa */
    .side-card {
      background: #ffffff;
      border-radius: 18px;
      padding: 16px 14px 18px;
      box-shadow: 0 8px 24px rgba(15, 23, 42, 0.07);
    }
    .side-title {
      font-size: 15px;
      font-weight: 700;
      margin-bottom: 6px;
      color: #111827;
    }
    .side-sub {
      font-size: 12px;
      color: #6b7280;
      margin-bottom: 12px;
    }
    .qr-wrapper {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 12px;
      flex-wrap: wrap;
    }
    .qr-box {
      border-radius: 12px;
      padding: 6px;
      background: #f9fafb;
      border: 1px solid #e5e7eb;
    }
    .qr-box img {
      display: block;
      width: 120px;
      height: 120px;
    }
    .qr-text {
      font-size: 12px;
      color: #4b5563;
      max-width: 220px;
    }
    .map-wrapper {
      border-radius: 12px;
      overflow: hidden;
      border: 1px solid #e5e7eb;
      background: #f3f4f6;
      margin-top: 8px;
    }
    .map-frame {
      width: 100%;
      height: 170px;
      border: 0;
    }

    /* Seção Como Chegar (coluna esquerda) */
    .section {
      background: #ffffff;
      border-radius: 18px;
      padding: 16px 14px 18px;
      box-shadow: 0 6px 20px rgba(15, 23, 42, 0.05);
    }
    .section + .section {
      margin-top: 14px;
    }
    .section-title {
      font-size: 16px;
      font-weight: 700;
      margin-bottom: 8px;
      color: #111827;
    }
    .section p {
      font-size: 14px;
      color: #374151;
      margin-bottom: 6px;
      line-height: 1.4;
    }
    .badge-ref {
      display: inline-block;
      font-size: 12px;
      background: #fef3c7;
      color: #92400e;
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
      padding: 8px 12px;
      border-radius: 999px;
      font-size: 13px;
      text-decoration: none;
      border: 1px solid #2563eb;
      color: #1d4ed8;
      background: #e0edff;
      cursor: pointer;
    }
    .btn-link:hover {
      background: #d1e3ff;
    }

    /* Fotos */
    .photos-section {
      margin-top: 18px;
    }
    .photos-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
      gap: 10px;
      margin-top: 10px;
    }
    .photo-card {
      border-radius: 12px;
      overflow: hidden;
      background: #e5e7eb;
      height: 130px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 12px;
      color: #4b5563;
      text-align: center;
      padding: 4px;
    }
    .photo-card img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }

    footer {
      margin-top: 20px;
      text-align: center;
      font-size: 11px;
      color: #9ca3af;
    }

    /* Tabela admin */
    .admin-page {
      max-width: 960px;
      margin: 0 auto;
      padding: 20px 16px 40px;
      font-family: Arial, sans-serif;
    }
    .admin-title {
      font-size: 22px;
      font-weight: 700;
      margin-bottom: 10px;
    }
    .admin-table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 10px;
      font-size: 13px;
    }
    .admin-table th,
    .admin-table td {
      border: 1px solid #d1d5db;
      padding: 6px 8px;
    }
    .admin-table th {
      background: #f3f4f6;
      text-align: left;
    }
    .admin-note {
      font-size: 12px;
      color: #6b7280;
      margin-top: 6px;
    }
  </style>
</head>
<body>
  <div class="page">
    <header>
      <div class="logo">GÁS USINA</div>
      <div class="slogan">Peça seu gás pelo WhatsApp ou venha até nosso depósito.</div>
    </header>

    <div class="hero">
      <div>
        <div class="hero-text-main">Entrega rápida de gás na sua região</div>
        <div class="hero-text-sub">Atendimento humanizado, com segurança e confiança, direto pelo WhatsApp.</div>
      </div>
      <div class="hero-tag">
        <span class="hero-dot"></span>
        <span>Aberto hoje · 09:00 às 22:00</span>
      </div>
    </div>

    <div class="layout">
      <!-- COLUNA ESQUERDA: WhatsApp + Como chegar -->
      <div>
        <div class="chat-card">
          <div class="chat-header">
            <div class="chat-avatar">
              <img src="/static/Screenshot_18.png" alt="Logo GÁS USINA" class="chat-avatar-img">
            </div>
            <div class="chat-agent">
              <div class="chat-agent-name">Atendimento GÁS USINA</div>
              <div class="chat-agent-status">
                <span class="status-dot"></span> Online agora
              </div>
            </div>
          </div>

          <div class="chat-body">
            <p>Olá! Seja bem-vindo à GÁS USINA 👋</p>
            <p>Clique no botão abaixo para falar com a nossa equipe pelo WhatsApp e fazer seu pedido de gás sem burocracia.</p>
          </div>

          <div class="chat-info">
            <strong>Horário WhatsApp:</strong> todos os dias, das <strong>09:00 às 22:00</strong>.
            <span class="small-note">
              Ao clicar, registramos data, IP e navegador apenas para controle interno de atendimento.
            </span>
          </div>

          <a class="whatsapp-btn" href="{{ pedido_url }}" target="_blank" rel="noopener noreferrer">
            <span>💬</span> <span>Iniciar atendimento no WhatsApp</span>
          </a>
        </div>

        <!-- COMO CHEGAR ABAIXO DO CHAT -->
        <div class="section">
          <div class="section-title">Como chegar ao depósito GÁS USINA</div>

          <p>
            <strong>Endereço:</strong><br>
            Estr. Hisaichi Takebayashi, 7530<br>
            Jardim Colonial – Atibaia/SP<br>
            Brasil
          </p>

          <p>
            <strong>Pontos de referência:</strong><br>
            • Próximo à região da Usina<br>
            • Localizado na Estrada Hisaichi Takebayashi<br>
            • Região bem sinalizada e de fácil localização
          </p>

          <span class="badge-ref">Fácil estacionamento em frente ao depósito</span>

          <div class="buttons-row">
            <a class="btn-link"
               href="https://www.google.com/maps/search/?api=1&query=Estrada+Hisaichi+Takebayashi,+7530,+Jardim+Colonial,+Atibaia+SP"
               target="_blank">
              🗺️ Abrir no Google Maps
            </a>
            <a class="btn-link"
               href="https://waze.com/ul?q=Estrada+Hisaichi+Takebayashi,+7530,+Jardim+Colonial,+Atibaia+SP&navigate=yes"
               target="_blank">
              🚗 Ir com Waze
            </a>
          </div>

          <p class="chat-info" style="margin-top: 10px;">
            <strong>Horário do depósito:</strong><br>
            • Segunda a sexta: 09:00 às 22:00<br>
            • Sábado e domingo: 09:00 às 15:00
          </p>
        </div>
      </div>

      <!-- COLUNA DIREITA: QR CODE + MAPA -->
      <div>
        <div class="side-card">
          <div class="side-title">Pedir pelo QR Code</div>
          <div class="side-sub">Aponte a câmera do celular para abrir o WhatsApp direto no nosso atendimento.</div>

          <div class="qr-wrapper">
            <div class="qr-box">
              <img src="{{ qr_url }}" alt="QR Code WhatsApp GÁS USINA">
            </div>
            <div class="qr-text">
              Abra a câmera do seu celular ou o app de leitura de QR Code e aponte para o código ao lado. Você será
              direcionado diretamente para o nosso WhatsApp.
            </div>
          </div>

          <div class="side-title" style="margin-top: 6px;">Nosso depósito no mapa</div>
          <div class="side-sub">Veja a localização da GÁS USINA e trace sua rota até nós.</div>

          <div class="map-wrapper">
            <iframe
              class="map-frame"
              src="https://www.google.com/maps?q=Estrada+Hisaichi+Takebayashi,+7530,+Jardim+Colonial,+Atibaia+SP&output=embed"
              loading="lazy"
              referrerpolicy="no-referrer-when-downgrade">
            </iframe>
          </div>
        </div>
      </div>
    </div>

    <!-- SEÇÃO: FOTOS (FULL WIDTH) -->
    <div class="section photos-section">
      <div class="section-title">Fotos do nosso depósito</div>
      <p>Veja um pouco da estrutura da GÁS USINA. Local organizado, seguro e pronto para atender você com rapidez.</p>

      <div class="photos-grid">
        <div class="photo-card">
          <img src="/static/deposito1.jpg" alt="Depósito Gás Usina - Fachada">
        </div>
        <div class="photo-card">
          Foto do depósito 2 (adicione como <code>deposito2.jpg</code> na pasta <code>static/</code>).
        </div>
        <div class="photo-card">
          Foto do caminhão de entrega (arquivo <code>deposito3.jpg</code>).
        </div>
        <div class="photo-card">
          Foto dos botijões organizados (arquivo <code>deposito4.jpg</code>).
        </div>
      </div>
    </div>

    <footer>
      GÁS USINA · Atendimento rápido pelo WhatsApp · Depósito físico à sua disposição.
    </footer>
  </div>
</body>
</html>
"""

ADMIN_PAGE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>Admin - Pedidos GÁS USINA</title>
</head>
<body>
  <div class="admin-page">
    <div class="admin-title">Relatório de acessos ao botão de WhatsApp</div>
    <p class="admin-note">
      Listando os últimos {{ total }} registros (data/hora, IP e navegador).
    </p>
    <table class="admin-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Data/Hora</th>
          <th>IP</th>
          <th>Navegador (User-Agent)</th>
        </tr>
      </thead>
      <tbody>
        {% for p in pedidos %}
        <tr>
          <td>{{ p.id }}</td>
          <td>{{ p.criado_em }}</td>
          <td>{{ p.ip }}</td>
          <td>{{ p.user_agent }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
    <p class="admin-note">
      URL desta página: <code>/admin/pedidos</code> — não está protegida por senha, use apenas para controle interno.
    </p>
  </div>
</body>
</html>
"""


@app.route("/")
def index():
  encoded_msg = urllib.parse.quote(WHATSAPP_MESSAGE)
  whatsapp_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={encoded_msg}"

  # Gera URL do QR Code com base no link do WhatsApp
  qr_data = urllib.parse.quote(whatsapp_url, safe="")
  qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=220x220&data={qr_data}"

  # rota interna que registra pedido antes de redirecionar
  pedido_url = "/fazer-pedido"

  return render_template_string(
    HTML_PAGE,
    whatsapp_url=whatsapp_url,
    qr_url=qr_url,
    pedido_url=pedido_url,
  )


@app.route("/fazer-pedido")
def fazer_pedido():
  """Registra o acesso ao botão e redireciona para o WhatsApp."""
  encoded_msg = urllib.parse.quote(WHATSAPP_MESSAGE)
  whatsapp_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={encoded_msg}"

  # Pega IP (considerando proxy do Render) e user-agent
  ip = request.headers.get("X-Forwarded-For", request.remote_addr)
  if ip and "," in ip:
    ip = ip.split(",")[0].strip()
  user_agent = request.headers.get("User-Agent", "")

  conn = sqlite3.connect(DB_PATH)
  cur = conn.cursor()
  cur.execute(
    "INSERT INTO pedidos (ip, user_agent) VALUES (?, ?)",
    (ip, user_agent),
  )
  conn.commit()
  conn.close()

  return redirect(whatsapp_url)


@app.route("/admin/pedidos")
def admin_pedidos():
  """Página simples para ver os últimos pedidos registrados."""
  conn = sqlite3.connect(DB_PATH)
  conn.row_factory = sqlite3.Row
  cur = conn.cursor()
  cur.execute(
    "SELECT id, criado_em, ip, user_agent FROM pedidos "
    "ORDER BY id DESC LIMIT 50"
  )
  rows = cur.fetchall()
  conn.close()

  return render_template_string(ADMIN_PAGE, pedidos=rows, total=len(rows))


if __name__ == "__main__":
  app.run(debug=True)
