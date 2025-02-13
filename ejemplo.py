import pandas as pd
import json
import unidecode #libreria para eliminar las tildes
import os
from datetime import datetime
from difflib import get_close_matches
import re


class SoporteTecnicoBot:

    def __init__(self, excel_file="preguntas_respuestas.xlsx"):
        self.nombre = "Juan"
        # Inicializar la sesión actual
        self.sesion_actual = {
            "nombre_cliente": None,
            "telefono": None,
            "numero_servicio": None,
             "inicio_sesion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), # Convertir a string aquí
            "mensajes": [],
        }
        # Cargar base de conocimiento y sinónimos
        self.base_conocimiento, self.sinonimos = self._cargar_base_conocimiento(
            excel_file
        )
        # Agregar diccionario de comandos especiales
        self.comandos_especiales = {
            "1": self._mostrar_menu,
            "2": self._mostrar_opciones_hardware,
            "3": self._consultar_estado_servicio,
            "4": self._mostrar_ubicacion,
            "5": self._agendar_visita,
            "6": self._diagnostico_software,
            "7": self._contactar_humano,
        }

    def _normalizar_texto(self, texto):
        """
        Normaliza el texto removiendo acentos, convirtiendo a minúsculas
        y eliminando caracteres especiales
        """
        # Convertir a string en caso de que no lo sea
        texto = str(texto)
        # Convertir a minúsculas
        texto = texto.lower()
        # Remover acentos
        texto = unidecode.unidecode(texto)
        # Remover caracteres especiales y espacios extras
        texto = re.sub(r'[^a-z0-9\s]', '', texto)
        texto = ' '.join(texto.split())
        return texto

    def _encontrar_mejor_respuesta(self, mensaje_normalizado):
        """
        Encuentra la mejor respuesta para un mensaje dado
        """
        # Si el mensaje está directamente en la base de conocimiento
        if mensaje_normalizado in self.base_conocimiento:
            return self.base_conocimiento[mensaje_normalizado]

        # Buscar coincidencias cercanas
        posibles_coincidencias = get_close_matches(
            mensaje_normalizado,
            list(self.base_conocimiento.keys()),
            n=1,
            cutoff=0.6
        )

        if posibles_coincidencias:
            return self.base_conocimiento[posibles_coincidencias[0]]

        return None

    def _guardar_conversacion(self):
        """
        Guarda la conversación actual en un archivo JSON
        """
        # Crear directorio de conversaciones si no existe
        os.makedirs('conversaciones', exist_ok=True)
        
        # Generar nombre de archivo con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"conversaciones/conversacion_{timestamp}.json"
        
        # Guardar conversación
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            json.dump(self.sesion_actual, f, ensure_ascii=False, indent=2)

    def _cargar_base_conocimiento(self, archivo):
        """Carga la base de conocimiento y sinónimos desde Excel"""
        try:
            df = pd.read_excel(archivo)
            # Verificar columnas necesarias
            columnas_requeridas = ["Pregunta", "Respuesta", "Sinonimos"]
            columnas_faltantes = [
                col for col in columnas_requeridas if col not in df.columns
            ]

            if columnas_faltantes:
                print(
                    f"⚠️ Columnas faltantes en el Excel: {', '.join(columnas_faltantes)}"
                )
                print("ℹ️ Creando columnas faltantes con valores vacíos...")
                for col in columnas_faltantes:
                    df[col] = ""

            # Inicializar diccionarios
            conocimiento = {}
            sinonimos = {}

            # Procesar cada fila
            for _, row in df.iterrows():
                pregunta_original = str(row["Pregunta"]).strip()
                if pd.isna(pregunta_original) or not pregunta_original:
                    continue

                pregunta_normalizada = self._normalizar_texto(pregunta_original)
                respuesta = str(row["Respuesta"])

                # Agregar pregunta original al diccionario
                conocimiento[pregunta_normalizada] = respuesta

                # Procesar sinónimos si existen
                if not pd.isna(row["Sinonimos"]):
                    sin_lista = str(row["Sinonimos"]).split(",")
                    for sinonimo in sin_lista:
                        sinonimo = sinonimo.strip()
                        if sinonimo:
                            sinonimo_normalizado = self._normalizar_texto(sinonimo)
                            sinonimos[sinonimo_normalizado] = pregunta_normalizada
                            conocimiento[sinonimo_normalizado] = respuesta

            print(
                f"✅ Base de conocimiento cargada: {len(conocimiento)} preguntas y {len(sinonimos)} sinónimos"
            )
            return conocimiento, sinonimos

        except FileNotFoundError:
            print(f"⚠️ No se encontró el archivo: {archivo}")
            return {}, {}
        except Exception as e:
            print(f"⚠️ Error al cargar la base de conocimiento: {str(e)}")
            return {}, {}

    # Métodos para comandos especiales
    def _mostrar_menu(self):
        return """📋 Menú Principal:
1. Ver este menú
2. Problemas de Hardware
3. Consultar estado de servicio
4. Ver ubicación y horarios
5. Agendar visita técnica
6. Diagnóstico de Software
7. Hablar con un asesor humano"""

    def _mostrar_opciones_hardware(self):
        return "Para problemas de hardware, puedes:\n1. Traer tu equipo a nuestro centro (opción 4)\n2. Solicitar visita técnica (opción 5)"

    def _consultar_estado_servicio(self):
        if not self.sesion_actual["numero_servicio"]:
            return (
                "Por favor, proporciona tu número de servicio para consultar el estado."
            )
        return f"Consultando estado del servicio {self.sesion_actual['numero_servicio']}..."

    def _mostrar_ubicacion(self):
        return "📍 Nos encuentras en: Calle 52 # 30-15\n⏰ Horario: Lunes a Viernes de 8:00 AM a 4:00 PM"

    def _agendar_visita(self):
        return "✅ Solicitud de visita técnica registrada. Te contactaremos pronto para confirmar el horario."

    def _diagnostico_software(self):
        return "Por favor, describe los síntomas que presenta tu equipo para poder ayudarte mejor."

    def _contactar_humano(self):
        return "Te conectaremos con un asesor humano en breve. Por favor, espera un momento."

    def _solicitar_datos_cliente(self):
        """Solicita y valida los datos del cliente"""
        print("\n📝 Por favor, proporciona tus datos para brindarte mejor atención:")

        while not self.sesion_actual["nombre_cliente"]:
            nombre = input("Nombre completo: ").strip()
            if len(nombre) > 3:
                self.sesion_actual["nombre_cliente"] = nombre
            else:
                print("❌ Por favor, ingresa un nombre válido")

        while not self.sesion_actual["telefono"]:
            telefono = input("Número de teléfono: ").strip()
            if telefono.isdigit() and len(telefono) >= 7:
                self.sesion_actual["telefono"] = telefono
            else:
                print("❌ Por favor, ingresa un número de teléfono válido")

    def procesar_mensaje(self, mensaje):
        """Procesa el mensaje del usuario y genera una respuesta"""
        mensaje_normalizado = self._normalizar_texto(mensaje)

        # Registrar mensaje del usuario
        self.sesion_actual["mensajes"].append(
            {
                "usuario": mensaje,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

        # Verificar si es un comando especial
        if mensaje in self.comandos_especiales:
            respuesta = self.comandos_especiales[mensaje]()
        # Verificar comandos de salida
        elif mensaje_normalizado in ["adios", "chao"]:
            self._guardar_conversacion()
            respuesta = "👋 ¡Gracias por contactarnos! Esperamos haberte ayudado."
        else:
            # Buscar la mejor respuesta
            respuesta = self._encontrar_mejor_respuesta(mensaje_normalizado)
            if not respuesta:
                respuesta = (
                    "Lo siento, no entiendo tu consulta. ¿Podrías reformularla? "
                    "Recuerda que puedes presionar '1' para ver el menú de opciones."
                )

        # Registrar respuesta del bot
        self.sesion_actual["mensajes"].append(
            {
                "bot": respuesta,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

        return respuesta

    def iniciar(self):
        """Inicia el chatbot y maneja la interacción principal"""
        print("\n" + "=" * 50)
        print("👨‍💻 ¡Bienvenido al Soporte Técnico de Computadoras!")
        print(f"🤖 Soy {self.nombre}, tu asistente virtual.")
        print("=" * 50 + "\n")

        # Solicitar datos del cliente
        self._solicitar_datos_cliente()

        print("\n📌 Comandos disponibles:")
        print("- Presiona '1' para ver el menú de opciones")
        print("- Escribe 'Adiós' o 'chao' para salir")
        print("📝 Cuéntame tu problema (ejemplo: 'Mi computadora está lenta')\n")

        while True:
            entrada = input(f"{self.sesion_actual['nombre_cliente']}: ").strip()

            if not entrada:
                print("❌ Por favor, escribe algo...")
                continue

            respuesta = self.procesar_mensaje(entrada)
            print(f"🤖 {self.nombre}:", respuesta)

            if entrada.lower() in ["adios", "chao"]:
                break


if __name__ == "__main__":
    bot = SoporteTecnicoBot()
    bot.iniciar()
