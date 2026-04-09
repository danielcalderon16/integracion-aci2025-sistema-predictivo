# Proyecto de Grado - Sistema Predictivo de Concreto (Arquitectura Mejorada)

Repositorio maestro que contiene la refactorización arquitectónica del proyecto de grado. Se ha migrado y optimizado de un prototipo IoT/Streamlit a una plataforma de inteligencia artificial y microservicios de nivel industrial.

## 🎯 Arquitectura de la Solución

El proyecto ha superado la dependencia de hardware físico (sensores inestables) para apoyarse en un robusto diseño teórico matemáticamente validado (normativa ACI 2025). Predice la madurez del concreto utilizando Inteligencia Artificial entrenada con ensayos reales de laboratorio. 

*   **Machine Learning (`/ml_models`):** Entrenamiento de Red Neuronal Profunda utilizando el "Concrete Compressive Strength Data Set" (UCI). Capaz de predecir curvas completas de curado.
*   **Backend & APIs (`/backend`):** Consolidado en **FastAPI** para exponer la inferencia del modelo junto a métodos ACI, todo acoplado mediante SQLAlchemy.
*   **Frontend Web (`/frontend`):** Plataforma web transaccional construida con **Next.js** y **TailwindCSS**, brindando la mejor experiencia al ingeniero calculista.
*   **DevOps & Persistencia:** Infraestructura dockerizada incluyendo base de datos **PostgreSQL**.

## 📂 Directorios Actuales
*   `docs/` -> Documento PDF detallado de la propuesta y hoja de ruta tecnológica de estas mejoras.
*   `ml_models/` -> Script actualizado para uso y entrenamiento del modelo UCI sin sensor, además de archivos legados para contexto.
*   `backend/` -> Scripts originales (`app_v3.py`) a la espera de ser desensamblados y migrados a microservicios FastAPI.

> *Este repositorio es el punto de inicio para la Fase 1, 2 y 3 del plan de implantación.*
