interface PydanticError {
  type: string;
  loc: (string | number)[];
  msg: string;
  ctx?: Record<string, unknown>;
}

const ETIQUETAS: Record<string, string> = {
  tipo_construccion: "Tipo de construcción",
  condiciones_agresivas: "Condiciones agresivas",
  resistencia_kgcm2: "Resistencia requerida f'c",
  densidad_cemento: "Densidad del cemento",
  tipo_cemento: "Tipo de cemento",
  tamano_nominal_in: "Tamaño máx. nominal",
  masa_unitaria_grueso: "Masa unitaria del agregado grueso",
  densidad_aparente_grueso: "Densidad aparente del agregado grueso",
  absorcion_grueso: "Absorción del agregado grueso",
  humedad_grueso: "Humedad del agregado grueso",
  modulo_finura: "Módulo de finura",
  masa_unitaria_fino: "Masa unitaria del agregado fino",
  densidad_aparente_fino: "Densidad aparente del agregado fino",
  absorcion_fino: "Absorción del agregado fino",
  humedad_fino: "Humedad del agregado fino",
  asentamiento_in: "Asentamiento",
  contenido_aire: "Contenido de aire",
  altura_cilindro: "Altura del cilindro",
  diametro_cilindro: "Diámetro del cilindro",
  num_cilindros: "Número de cilindros",
  porcentaje_lodo: "Porcentaje de lodo",
  diseno_id: "Diseño",
  edades_dias: "Edades de curado",
  escoria: "Escoria",
  cenizas: "Cenizas",
  superplastificante: "Superplastificante",
  username: "Usuario",
  email: "Correo",
  password: "Contraseña",
};

function etiquetaDe(loc: (string | number)[]): string {
  const campo = loc[loc.length - 1];
  return ETIQUETAS[String(campo)] ?? String(campo);
}

function traducirError(err: PydanticError): string {
  const etiqueta = etiquetaDe(err.loc);
  switch (err.type) {
    case "greater_than":
      return `${etiqueta}: debe ser mayor que ${err.ctx?.gt}`;
    case "greater_than_equal":
      return `${etiqueta}: debe ser mayor o igual a ${err.ctx?.ge}`;
    case "less_than_equal":
      return `${etiqueta}: debe ser menor o igual a ${err.ctx?.le}`;
    case "less_than":
      return `${etiqueta}: debe ser menor que ${err.ctx?.lt}`;
    case "missing":
      return `${etiqueta}: este campo es obligatorio`;
    case "string_too_short":
      return `${etiqueta}: es demasiado corto`;
    case "value_error":
    case "string_type":
      return `${etiqueta}: valor inválido`;
    default:
      return `${etiqueta}: ${err.msg}`;
  }
}

/** Convierte el `detail` de un error de FastAPI (string o lista de errores de validación) en un mensaje legible. */
export function formatApiError(detail: unknown, fallback: string): string {
  if (!detail) return fallback;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    try {
      const mensajes = detail.map((e) => traducirError(e as PydanticError));
      return mensajes.length ? mensajes.join("\n") : fallback;
    } catch {
      return fallback;
    }
  }
  return fallback;
}
