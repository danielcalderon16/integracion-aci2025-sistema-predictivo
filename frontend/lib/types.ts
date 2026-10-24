export type Rol = "estudiante" | "profesor";

export interface Usuario {
  id: number;
  username: string;
  email: string;
  nombre_completo: string;
  codigo: string;
  rol: Rol;
  is_admin: boolean;
}

export interface DisenoMezclaInput {
  tipo_construccion: string;
  condiciones_agresivas: string;
  resistencia_kgcm2: number;
  densidad_cemento: number;
  tipo_cemento: string;
  tamano_nominal_in: number;
  masa_unitaria_grueso: number;
  densidad_aparente_grueso: number;
  absorcion_grueso: number;
  humedad_grueso: number;
  modulo_finura: number;
  masa_unitaria_fino: number;
  densidad_aparente_fino: number;
  absorcion_fino: number;
  humedad_fino: number;
  asentamiento_in: number;
  contenido_aire: number;
  altura_cilindro: number;
  diametro_cilindro: number;
  num_cilindros: number;
  porcentaje_lodo: number;
}

export interface Prediccion {
  id: number;
  edad_dias: number;
  escoria: number;
  cenizas: number;
  superplastificante: number;
  resistencia_predicha_mpa: number;
  extrapolado: boolean;
}

export interface DisenoMezcla extends DisenoMezclaInput {
  id: number;
  folio: string;
  created_at: string;
  tamano_nominal_mm: number;
  resistencia_teorica_kgcm2: number;
  resistencia_teorica_mpa: number;
  resistencia_teorica_psi: number;
  volumen_unitario_agua: number;
  relacion_agua_cemento: number;
  contenido_agregado_grueso: number;
  factor_cemento: number;
  peso_agregado_grueso: number;
  peso_agregado_fino: number;
  peso_real_grueso: number;
  peso_real_fino: number;
  agua_mezclado: number;
  cemento_cant: number;
  lodo_cant: number;
  arena_cant: number;
  grava_cant: number;
  agua_cant: number;
  predicciones: Prediccion[];
  usuario_id: number;
  autor_username: string | null;
  autor_nombre: string | null;
}
