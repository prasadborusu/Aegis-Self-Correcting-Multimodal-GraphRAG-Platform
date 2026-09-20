from fastapi import FastAPI
app = FastAPI(title='Aegis')
@app.get('/health')
def root_health(): return {'status': 'healthy'}
