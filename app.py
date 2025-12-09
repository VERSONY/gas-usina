from flask import Flask, render_template_string
import urllib.parse

app = Flask(__name__)

# Configuração do WhatsApp da GÁS USINA
WHATSAPP_NUMBER = "5511988180989"
WHATSAPP_MESSAGE = "Olá! Gostaria de falar com a GÁS USINA sobre pedido de gás."

HTML_PAGE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>GÁS USINA - Atendimento pelo WhatsApp</title>
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

    .layout {
      display: grid;
      gap: 18px;
    }
    @media (min-width: 768px) {
      .layout {
        grid-template-columns: 1.2fr 1fr;
      }
    }

    /* Bloco de chat */
    .chat-card {
      background: #ffffff;
      border-radius: 18px;
      padding: 18px 16px 22px;
      box-shadow: 0 4px 14px rgba(0,0,0,0.08);
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
      border: 2px solid #e0e0e0;
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
    }
    .chat-agent-status {
      font-size: 12px;
      color: #2e7d32;
    }
    .chat-body {
      background: #e3f2fd;
      border-radius: 14px;
      padding: 10px 12px;
      font-size: 13px;
      color: #333;
      margin-bottom: 14px;
    }
    .chat-body p + p {
      margin-top: 6px;
    }
    .chat-info {
      font-size: 12px;
      color: #777;
      margin-bottom: 10px;
    }
    .whatsapp-btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      text-decoration: none;
      background: #25D366;
      color: #ffffff;
      font-weight: 600;
      font-size: 15px;
      padding: 11px 16px;
      border-radius: 999px;
      box-shadow: 0 4px 12px rgba(37,211,102,0.4);
    }
    .whatsapp-btn:hover {
      opacity: 0.96;
    }

    /* Seção Como Chegar */
    .section {
      background: #ffffff;
      border-radius: 16px;
      padding: 16px 14px 18px;
      box-shadow: 0 4px 14px rgba(0,0,0,0.06);
      margin-top: 10px;
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

    /* Fotos */
    .photos-section {
      margin-top: 16px;
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
      margin-top: 18px;
      text-align: center;
      font-size: 11px;
      color: #777;
    }
  </style>
</head>
<body>
  <div class="page">
    <header>
      <div class="logo">GÁS USINA</div>
      <div class="slogan">Atendimento rápido pelo WhatsApp e depósito físico à sua disposição.</div>
    </header>

    <div class="layout">
      <!-- BLOCO: CHAT VIA WHATSAPP -->
      <div>
        <div class="chat-card">
          <div class="chat-header">
            <div class="chat-avatar">
              <img src="/static/Screenshot_18.png" alt="Logo GÁS USINA" class="chat-avatar-img">
            </div>
            <div class="chat-agent">
              <div class="chat-agent-name">Atendimento GÁS USINA</div>
              <div class="chat-agent-status">🟢 Online agora</div>
            </div>
          </div>

          <div class="chat-body">
            <p>Olá! Seja bem-vindo à GÁS USINA 👋</p>
            <p>Clique no botão abaixo para falar com a nossa equipe pelo WhatsApp e fazer seu pedido de gás sem burocracia.</p>
          </div>

          <div class="chat-info">
            • Atendimento pelo WhatsApp: todos os dias, das 8h às 22h.
          </div>

          <a
            class="whatsapp-btn"
            href="{{ whatsapp_url }}"
            target="_blank"
            rel="noopener noreferrer"
          >
            💬 Iniciar atendimento no WhatsApp
          </a>
        </div>
      </div>

      <!-- BLOCO: COMO CHEGAR -->
      <div>
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
            <a
              class="btn-link"
              href="https://waze.com/ul"
              target="_blank"
              rel="noopener noreferrer"
            >
              🚗 Ir com Waze
            </a>
          </div>

          <p class="chat-info">
            Horário de atendimento no depósito: segunda a sábado, das 8h às 18h.
          </p>
        </div>
      </div>
    </div>

    <!-- BLOCO: FOTOS DO DEPÓSITO -->
    <div class="section photos-section">
      <div class="section-title">Fotos do nosso depósito</div>
      <p>
        Veja um pouco da estrutura da GÁS USINA. Local organizado, seguro e pronto
        para atender você com rapidez.
      </p>

      <div class="photos-grid">
        <div class="photo-card">
          Foto do depósito 1<br>(depois trocamos por uma imagem real)
        </div>
        <div class="photo-card">
          Foto do depósito 2
        </div>
        <div class="photo-card">
          Caminhão de entrega
        </div>
        <div class="photo-card">
          Botijões organizados
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

@app.route("/")
def index():
    encoded_msg = urllib.parse.quote(WHATSAPP_MESSAGE)
    whatsapp_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={encoded_msg}"
    return render_template_string(HTML_PAGE, whatsapp_url=whatsapp_url)

if __name__ == "__main__":
    app.run(debug=True)
