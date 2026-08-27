from fastapi import FastAPI, BackgroundTasks
import httpx

app = FastAPI()

class CentralArmazenagem:
    def __init__(self):
        self.pilha = []
        self.status_pesquisa = "LIVRE"
        self.limite_seguranca = 3 

    def processar_chegada_da_transportadora(self, carga):
        id_carga = carga.get('id', 'desconhecida')
        
        if self.status_pesquisa == "LIVRE":
            self.status_pesquisa = "OCUPADO"
            print(f"[BYPASS] Carga {id_carga} enviada DIRETO para a Pesquisa.")
            self.chamar_api_jogo("/pesquisa/analisar", {"id_carga": id_carga})
            return

        if len(self.pilha) >= self.limite_seguranca:
            print(f"[ALERTA] Armazém lotado. Segurando carga na doca.")
            return 
            
        self.pilha.append(carga)
        print(f"[GUARDADO] Carga {id_carga} colocada no TOPO da pilha.")
        self.chamar_api_jogo("/armazenagem/guardar", {"id_carga": id_carga})

    def desempilhar_para_pesquisa(self):
        self.status_pesquisa = "LIVRE"
        if not self.pilha:
            return

        carga_topo = self.pilha.pop()
        self.status_pesquisa = "OCUPADO"
        id_carga = carga_topo.get('id')
        
        print(f"[DESEMPILHADO] Carga {id_carga} retirada do topo e enviada à Pesquisa.")
        self.chamar_api_jogo("/pesquisa/analisar", {"id_carga": id_carga})

    def chamar_api_jogo(self, endpoint, payload):
        URL_MOTOR = "http://localhost:5000"
        try:
            httpx.post(f"{URL_MOTOR}{endpoint}", json=payload)
        except:
            pass 

armazem = CentralArmazenagem()

@app.post("/webhook/carga_entregue")
async def transporte_chegou(evento: dict, bg_tasks: BackgroundTasks):
    carga = evento.get("carga", {"id": "Desconhecida"})
    bg_tasks.add_task(armazem.processar_chegada_da_transportadora, carga)
    return {"status": "Processando armazenamento"}

@app.post("/webhook/analise_concluida")
async def laboratorio_liberado(evento: dict, bg_tasks: BackgroundTasks):
    bg_tasks.add_task(armazem.desempilhar_para_pesquisa)
    return {"status": "Alimentando laboratório"}