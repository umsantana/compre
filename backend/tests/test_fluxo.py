H = {"X-Requested-With": "compre"}
LEAD = {"nome": "Maria Souza", "email": "maria@empresa.com", "consentimento_lgpd": True, "produto_interesse": "compras"}


def login(client, senha="senha-muito-longa-1"):
    return client.post("/api/auth/login", json={"email": "admin@teste.com", "senha": senha})


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_lead_publico_exige_consentimento_e_ignora_robo(client):
    assert client.post("/api/public/leads", json={**LEAD, "consentimento_lgpd": False}).status_code == 422
    assert client.post("/api/public/leads", json={**LEAD, "website": "http://spam"}).status_code == 201
    assert client.post("/api/public/leads", json=LEAD).status_code == 201
    login(client)
    leads = client.get("/api/leads").json()
    assert len(leads) == 1 and leads[0]["email"] == "maria@empresa.com"  # o do robô não foi gravado


def test_login_e_protecao(client):
    assert client.get("/api/clientes").status_code == 401
    assert login(client, "errada").status_code == 401
    assert login(client).status_code == 200
    assert client.get("/api/auth/me").json()["perfil"] == "super_admin"
    # sem o cabeçalho anti-CSRF, ações que alteram dados são recusadas
    assert client.post("/api/clientes", json={"nome": "X Ltda", "email": "x@x.com"}).status_code == 403


def test_bloqueio_apos_falhas(client):
    for _ in range(5):
        login(client, "errada")
    assert login(client).status_code == 429


def test_cliente_licenca_e_validacao(client):
    login(client)
    c = client.post("/api/clientes", json={"nome": "Padaria Ltda", "email": "p@p.com", "documento": "123"}, headers=H)
    assert c.status_code == 201
    assert client.post("/api/clientes", json={"nome": "Outra", "email": "o@o.com", "documento": "123"}, headers=H).status_code == 409
    prod = client.get("/api/produtos").json()[0]
    lic = client.post("/api/licencas", json={"cliente_id": c.json()["id"], "produto_id": prod["id"], "status": "ativa", "limite_usuarios": 5}, headers=H)
    assert lic.status_code == 201
    chave = lic.json()["chave"]

    v = client.get("/api/licencas/validar", headers={"X-License-Key": chave}).json()
    assert v["valida"] and v["produto"] == "compras" and v["limites"]["usuarios"] == 5
    assert client.get("/api/licencas/validar", headers={"X-License-Key": "cmp_falsa"}).status_code == 404

    client.patch(f"/api/licencas/{lic.json()['id']}/status", json={"status": "suspensa"}, headers=H)
    assert client.get("/api/licencas/validar", headers={"X-License-Key": chave}).json()["valida"] is False
    assert client.get("/api/dashboard").json()["licencas_por_status"] == {"suspensa": 1}
