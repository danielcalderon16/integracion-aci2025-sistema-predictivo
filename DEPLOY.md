# Guía de despliegue gratuito (Vercel + Render + Neon)

Sigue este orden exacto: primero la base de datos, luego el backend (que la
necesita), y al final el frontend (que necesita la URL del backend). Al
final hay que volver al backend una vez para terminar de conectar todo.

## 1. Base de datos — Neon (gratis, no caduca)

1. Crea una cuenta en https://neon.tech (con GitHub o correo).
2. "Create a project" → nombre: `aci2025` (o el que quieras) → región cercana
   (ej. US East).
3. Neon te da una cadena de conexión tipo:
   ```
   postgresql://usuario:contraseña@ep-xxxx.us-east-2.aws.neon.tech/aci2025?sslmode=require
   ```
4. Guárdala — la necesitas en el paso 2. Para SQLAlchemy debe empezar con
   `postgresql+psycopg2://` en vez de `postgresql://`:
   ```
   postgresql+psycopg2://usuario:contraseña@ep-xxxx.us-east-2.aws.neon.tech/aci2025?sslmode=require
   ```

## 2. Backend — Render (gratis, se duerme tras 15 min sin uso)

1. Crea una cuenta en https://render.com (con GitHub, para conectar el repo directo).
2. "New +" → "Web Service" → conecta tu repositorio
   `integracion-aci2025-sistema-predictivo`.
3. Configuración:
   - **Root Directory**: `backend`
   - **Runtime**: Docker (Render detecta el `Dockerfile` automáticamente)
   - **Instance Type**: Free
4. Variables de entorno (sección "Environment"):

   | Variable | Valor |
   |---|---|
   | `DATABASE_URL` | la cadena de conexión de Neon, con `postgresql+psycopg2://` |
   | `JWT_SECRET` | una cadena larga y aleatoria (ej. genera una en https://1password.com/password-generator, 40+ caracteres) |
   | `JWT_ALGORITHM` | `HS256` |
   | `JWT_EXPIRE_MINUTES` | `1440` |
   | `CORS_ORIGINS` | déjalo temporalmente en `http://localhost:3000` — lo actualizas en el paso 4 |

5. Dale "Create Web Service". Render construye la imagen Docker y la
   despliega (tarda unos minutos la primera vez). Al terminar te da una URL
   como `https://aci-backend-xxxx.onrender.com`.
6. Verifica que funcionó entrando a `https://tu-backend.onrender.com/docs`
   — debe mostrar la documentación interactiva de la API (Swagger).

## 3. Frontend — Vercel (gratis, sin dormirse)

1. Crea una cuenta en https://vercel.com (con GitHub).
2. "Add New..." → "Project" → importa el mismo repositorio.
3. Configuración:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Next.js (Vercel lo detecta solo)
4. Variables de entorno:

   | Variable | Valor |
   |---|---|
   | `NEXT_PUBLIC_API_URL` | la URL de Render del paso 2, ej. `https://aci-backend-xxxx.onrender.com` |
   | `BACKEND_INTERNAL_URL` | la misma URL de Render |

5. Dale "Deploy". Al terminar te da una URL como
   `https://tu-proyecto.vercel.app`.

## 4. Último paso — conectar el frontend al backend (CORS)

El backend, por seguridad, solo acepta peticiones del navegador que vengan
del frontend autorizado. Vuelve a Render:

1. Ve a tu servicio backend → "Environment".
2. Cambia `CORS_ORIGINS` por la URL real de Vercel del paso 3, ej.
   `https://tu-proyecto.vercel.app`.
3. Guarda — Render redespliega automáticamente con el valor nuevo.

## Verificación final

1. Abre tu URL de Vercel.
2. Regístrate (la primera cuenta que crees queda como administrador).
3. Calcula un diseño de mezcla y genera la predicción de IA.
4. Si el backend estaba dormido, la primera petición puede tardar ~20-30
   segundos en responder — es normal en el plan gratuito de Render, no es un
   error.

## Notas

- Cada vez que hagas `git push` a `main`, Render y Vercel vuelven a
  desplegar automáticamente (CI/CD incluido gratis).
- Las migraciones de base de datos (`alembic upgrade head`) corren solas en
  cada arranque del backend — no hay que ejecutarlas a mano en producción.
- Si cambias el dominio de Vercel más adelante, recuerda repetir el paso 4.
