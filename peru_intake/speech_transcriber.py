import io
import speech_recognition as sr
from pydub import AudioSegment

class PeruSpeechTranscriber:
    """
    Motor de Transcripción de Voz Cívica adaptado al dialecto peruano ('es-PE').
    Procesa archivos de audio (.wav, .mp3, .ogg, .m4a) provenientes de grabaciones en vivo
    (st.audio_input) o notas de voz subidas (WhatsApp / st.file_uploader) y los convierte
    a texto estructurado para el Ideario y el análisis DAMA.
    """
    def __init__(self, language="es-PE"):
        self.language = language
        self.recognizer = sr.Recognizer()
        # Ajustar sensibilidad de ruido
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True

    def _convert_to_wav_bytes(self, file_bytes, filename="audio.wav"):
        """
        Normaliza cualquier formato de audio recibido (MP3/OGG/WAV) a WAV PCM de 16kHz en memoria
        compatible con speech_recognition.
        """
        try:
            # Si el archivo ya es WAV, intentamos cargarlo o normalizar con pydub
            ext = filename.split(".")[-1].lower() if "." in filename else "wav"
            
            # Cargar con pydub desde bytes
            if ext == "mp3":
                audio = AudioSegment.from_mp3(io.BytesIO(file_bytes))
            elif ext in ["ogg", "opus"]:
                audio = AudioSegment.from_ogg(io.BytesIO(file_bytes))
            elif ext == "m4a":
                audio = AudioSegment.from_file(io.BytesIO(file_bytes), format="m4a")
            else:
                audio = AudioSegment.from_file(io.BytesIO(file_bytes))
                
            # Convertir a mono 16000 Hz WAV para mejor reconocimiento
            audio = audio.set_channels(1).set_frame_rate(16000)
            wav_buffer = io.BytesIO()
            audio.export(wav_buffer, format="wav")
            wav_buffer.seek(0)
            return wav_buffer
        except Exception as e:
            # Si pydub o ffmpeg no están disponibles en el PATH, intentar usar el buffer raw si es WAV
            if "wav" in filename.lower():
                return io.BytesIO(file_bytes)
            raise RuntimeError(f"Error normalizando formato de audio: {str(e)}")

    def transcribe(self, file_bytes, filename="audio.wav"):
        """
        Ejecuta el reconocimiento de voz sobre el audio normalizado en español peruano (es-PE).
        Retorna (exito: bool, transcripcion_o_error: str).
        """
        if not file_bytes:
            return False, "⚠️ No se recibió ningún flujo de audio."

        try:
            wav_stream = self._convert_to_wav_bytes(file_bytes, filename)
            
            with sr.AudioFile(wav_stream) as source:
                # Escuchar el audio completo
                audio_data = self.recognizer.record(source)
                
                # Reconocimiento usando el motor Web Speech API para español peruano
                text = self.recognizer.recognize_google(audio_data, language=self.language)
                
                if text and len(text.strip()) > 0:
                    return True, text.strip()
                else:
                    return False, "⚠️ El audio fue procesado pero no se detectaron palabras claras."
                    
        except sr.UnknownValueError:
            return False, "⚠️ No se pudo entender claramente el audio. Por favor, asegúrate de hablar cerca del micrófono y sin mucho ruido de fondo."
        except sr.RequestError as re:
            return False, f"⚠️ Error en el servicio de transcripción de voz: {str(re)}. Por favor, verifica tu conexión a Internet o ingresa el texto manualmente."
        except Exception as ex:
            return False, f"⚠️ Error técnico al procesar el audio: {str(ex)}"
