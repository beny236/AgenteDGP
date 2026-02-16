import json
import hashlib
import time
from pathlib import Path


class SimpleCache:
    """Caché simple con Time-To-Live"""
    
    def __init__(self, ttl_seconds=3600):
        self.cache = {}
        self.ttl = ttl_seconds
        self.cache_file = Path("response_cache.json")
        self._load()
    
    def _load(self):
        """Carga caché desde disco"""
        if self.cache_file.exists():
            try:
                data = json.loads(self.cache_file.read_text(encoding="utf-8"))
                now = time.time()
                self.cache = {
                    k: v for k, v in data.items()
                    if v["expires_at"] > now
                }
                if self.cache:
                    print(f"✓ Caché cargado: {len(self.cache)} entradas")
            except Exception as e:
                print(f"Advertencia: No se pudo cargar caché: {e}")
                self.cache = {}
    
    def _save(self):
        """Guarda caché a disco"""
        try:
            self.cache_file.write_text(
                json.dumps(self.cache, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        except Exception as e:
            print(f"Advertencia: No se pudo guardar caché: {e}")
    
    def _make_key(self, text):
        """Genera key única para la pregunta"""
        normalized = text.lower().strip()
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def get(self, pregunta):
        """Busca respuesta en caché"""
        key = self._make_key(pregunta)
        
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        
        # Verificar si expiró
        if entry["expires_at"] < time.time():
            del self.cache[key]
            self._save()
            return None
        
        print("✓ CACHE HIT - Respuesta encontrada (0 tokens)")
        return entry["response"]
    
    def set(self, pregunta, respuesta):
        """Guarda respuesta en caché"""
        key = self._make_key(pregunta)
        self.cache[key] = {
            "response": respuesta,
            "expires_at": time.time() + self.ttl,
            "created_at": time.time()
        }
        self._save()
    
    def clear(self):
        """Limpia todo el caché"""
        self.cache = {}
        self._save()