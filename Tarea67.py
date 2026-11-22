"""
Clientes, Servicios y Reservas - Sin Base de Datos
"""

from abc import ABC, abstractmethod
from datetime import datetime
import logging

# ============================================================
# 1. LOGS - Archivo donde se guardan errores y eventos
# ============================================================
logging.basicConfig(
    filename="sistema.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8"
)

def log_info(mensaje):
    logging.info(mensaje)
    print(f"[INFO] {mensaje}")

def log_error(mensaje):
    logging.error(mensaje)
    print(f"[ERROR] {mensaje}")

# ============================================================
# 2. EXCEPCIONES PERSONALIZADAS
# ============================================================
class ErrorSistema(Exception):
    pass

class DatosInvalidosError(ErrorSistema):
    pass

class ParametroFaltanteError(ErrorSistema):
    pass

class OperacionNoPermitidaError(ErrorSistema):
    pass

class ServicioNoDisponibleError(ErrorSistema):
    pass

class ReservaInvalidaError(ErrorSistema):
    pass

class CalculoError(ErrorSistema):
    pass

# ============================================================
# 3. CLASE ABSTRACTA BASE
# ============================================================
class EntidadBase(ABC):
    def __init__(self, id_entidad):
        if not id_entidad:
            raise ParametroFaltanteError("El ID es obligatorio")
        self._id = id_entidad
        self._fecha_creacion = datetime.now()

    @property
    def id(self):
        return self._id

    @abstractmethod
    def describir(self):
        pass

    @abstractmethod
    def validar(self):
        pass

# ============================================================
# 4. CLIENTE - Encapsulación con @property
# ============================================================
class Cliente(EntidadBase):
    def __init__(self, id_cliente, nombre, correo, telefono, documento):
        super().__init__(id_cliente)
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono
        self.documento = documento
        self._activo = True

    # --- Encapsulación ---
    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not valor or len(valor.strip()) < 3:
            raise DatosInvalidosError("Nombre debe tener mínimo 3 letras")
        self._nombre = valor.strip().title()

    @property
    def correo(self):
        return self._correo

    @correo.setter
    def correo(self, valor):
        if not valor or "@" not in valor or "." not in valor:
            raise DatosInvalidosError(f"Correo inválido: {valor}")
        self._correo = valor.lower()

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        valor = str(valor).strip()
        if not valor.isdigit() or len(valor) < 7:
            raise DatosInvalidosError("Teléfono debe ser numérico y mínimo 7 dígitos")
        self._telefono = valor

    @property
    def documento(self):
        return self._documento

    @documento.setter
    def documento(self, valor):
        if not valor or len(str(valor)) < 5:
            raise DatosInvalidosError("Documento inválido, mínimo 5 caracteres")
        self._documento = str(valor)

    @property
    def activo(self):
        return self._activo

    def desactivar(self):
        self._activo = False

    def validar(self):
        return True

    def describir(self):
        return f"Cliente [{self.id}] {self._nombre} | {self._correo} | Tel: {self._telefono} | Activo: {self._activo}"

# ============================================================
# 5. SERVICIO ABSTRACTO
# ============================================================
class Servicio(EntidadBase, ABC):
    def __init__(self, id_servicio, nombre, precio_base):
        super().__init__(id_servicio)
        self.nombre = nombre
        if precio_base is None:
            raise ParametroFaltanteError("precio_base es obligatorio")
        if precio_base < 0:
            raise CalculoError("El precio no puede ser negativo")
        self._precio_base = float(precio_base)
        self._disponible = True

    @property
    def precio_base(self):
        return self._precio_base

    @property
    def disponible(self):
        return self._disponible

    def marcar_no_disponible(self):
        self._disponible = False

    # --- MÉTODO SOBRECARGADO ---
    # Se puede llamar de 3 formas:
    # calcular_costo(2)
    # calcular_costo(2, descuento=0.1)
    # calcular_costo(2, descuento=0.1, impuesto=0.19)
    def calcular_costo(self, duracion=1, descuento=0.0, impuesto=0.0, cantidad=1):
        try:
            if duracion <= 0:
                raise DatosInvalidosError("Duración debe ser mayor a 0")
            if not 0 <= descuento < 1:
                raise CalculoError("Descuento debe estar entre 0 y 1")
            if not 0 <= impuesto < 1:
                raise CalculoError("Impuesto debe estar entre 0 y 1")
            if cantidad <= 0:
                raise DatosInvalidosError("Cantidad debe ser mayor a 0")

            subtotal = self._calcular_subtotal(duracion, cantidad)
            total = subtotal * (1 - descuento) * (1 + impuesto)
            return round(total, 2)
        except (DatosInvalidosError, CalculoError) as e:
            # Encadenamiento de excepciones
            raise CalculoError(f"Error al calcular costo de {self.nombre}: {e}") from e

    @abstractmethod
    def _calcular_subtotal(self, duracion, cantidad):
        pass

    @abstractmethod
    def calcular_costo_base(self, duracion):
        pass

    def validar(self):
        if self._precio_base < 0:
            raise CalculoError("Precio inválido")
        return True

# ============================================================
# 6. TRES SERVICIOS - Herencia + Polimorfismo
# ============================================================
class ReservaSala(Servicio):
    def __init__(self, id_servicio, nombre, precio_base, capacidad, tiene_proyector=False):
        super().__init__(id_servicio, nombre, precio_base)
        if capacidad <= 0:
            raise DatosInvalidosError("Capacidad debe ser mayor a 0")
        self.capacidad = capacidad
        self.tiene_proyector = tiene_proyector

    def _calcular_subtotal(self, duracion, cantidad):
        extra = 20000 if self.tiene_proyector else 0
        return (self._precio_base * duracion + extra) * cantidad

    def calcular_costo_base(self, duracion):
        return self.calcular_costo(duracion)

    def describir(self):
        return f"Sala [{self.id}] {self.nombre} | Capacidad: {self.capacidad} | Proyector: {self.tiene_proyector} | ${self._precio_base}/hora | Disponible: {self._disponible}"

class AlquilerEquipo(Servicio):
    def __init__(self, id_servicio, nombre, precio_base, stock, tipo_equipo="General"):
        super().__init__(id_servicio, nombre, precio_base)
        if stock < 0:
            raise DatosInvalidosError("Stock no puede ser negativo")
        self.stock = stock
        self.tipo_equipo = tipo_equipo

    def _calcular_subtotal(self, duracion, cantidad):
        if cantidad > self.stock:
            raise ServicioNoDisponibleError(f"Solo hay {self.stock} unidades, pidió {cantidad}")
        return self._precio_base * duracion * cantidad

    def calcular_costo_base(self, duracion):
        return self.calcular_costo(duracion, cantidad=1)

    def describir(self):
        return f"Equipo [{self.id}] {self.nombre} ({self.tipo_equipo}) | Stock: {self.stock} | ${self._precio_base}/día | Disponible: {self._disponible}"

class Asesoria(Servicio):
    def __init__(self, id_servicio, nombre, precio_base, especialista, nivel="Básico"):
        super().__init__(id_servicio, nombre, precio_base)
        if not especialista or len(especialista.strip()) < 3:
            raise DatosInvalidosError("Especialista inválido")
        if nivel not in ["Básico", "Intermedio", "Avanzado"]:
            raise DatosInvalidosError("Nivel debe ser Básico, Intermedio o Avanzado")
        self.especialista = especialista
        self.nivel = nivel

    def _calcular_subtotal(self, duracion, cantidad):
        multiplicador = {"Básico": 1.0, "Intermedio": 1.3, "Avanzado": 1.6}[self.nivel]
        return self._precio_base * duracion * multiplicador * cantidad

    def calcular_costo_base(self, duracion):
        return self.calcular_costo(duracion)

    def describir(self):
        return f"Asesoría [{self.id}] {self.nombre} | Especialista: {self.especialista} | Nivel: {self.nivel} | ${self._precio_base}/hora | Disponible: {self._disponible}"

# ============================================================
# 7. RESERVA
# ============================================================
class Reserva(EntidadBase):
    def __init__(self, id_reserva, cliente, servicio, duracion, cantidad=1):
        super().__init__(id_reserva)
        if cliente is None or servicio is None:
            raise ParametroFaltanteError("Reserva necesita cliente y servicio")
        if duracion <= 0:
            raise ReservaInvalidaError("Duración debe ser mayor a 0")
        self._cliente = cliente
        self._servicio = servicio
        self._duracion = duracion
        self._cantidad = cantidad
        self._estado = "PENDIENTE"
        self._costo_total = 0

    @property
    def estado(self):
        return self._estado

    @property
    def costo_total(self):
        return self._costo_total

    def confirmar(self):
        try:
            if self._estado != "PENDIENTE":
                raise OperacionNoPermitidaError(f"No se puede confirmar en estado {self._estado}")
            if not self._servicio.disponible:
                raise ServicioNoDisponibleError(f"Servicio {self._servicio.nombre} no disponible")
            if not self._cliente.activo:
                raise OperacionNoPermitidaError("Cliente inactivo")

            self._servicio.validar()
            self._costo_total = self._servicio.calcular_costo(self._duracion, cantidad=self._cantidad)
            self._estado = "CONFIRMADA"

        except (ServicioNoDisponibleError, OperacionNoPermitidaError, DatosInvalidosError) as e:
            log_error(f"Reserva {self.id} falló: {e}")
            # Encadenamiento
            raise ReservaInvalidaError(f"No se pudo confirmar reserva {self.id}") from e
        else:
            log_info(f"Reserva {self.id} CONFIRMADA - {self._cliente.nombre} - ${self._costo_total}")
            return True
        finally:
            # Siempre se ejecuta
            logging.info(f"Intento confirmar {self.id} - Estado: {self._estado}")

    def cancelar(self):
        try:
            if self._estado == "CANCELADA":
                raise OperacionNoPermitidaError("Ya está cancelada")
            if self._estado == "COMPLETADA":
                raise OperacionNoPermitidaError("No se puede cancelar una completada")
            self._estado = "CANCELADA"
        except OperacionNoPermitidaError as e:
            log_error(str(e))
            raise
        else:
            log_info(f"Reserva {self.id} CANCELADA")
            return True
        finally:
            logging.info(f"Intento cancelar {self.id}")

    def procesar(self):
        try:
            if self._estado != "CONFIRMADA":
                raise OperacionNoPermitidaError(f"Solo se puede procesar CONFIRMADA, actual: {self._estado}")
            self._estado = "COMPLETADA"
        except OperacionNoPermitidaError as e:
            log_error(f"Error al procesar {self.id}: {e}")
            raise
        else:
            log_info(f"Reserva {self.id} COMPLETADA")
            return True

    def validar(self):
        return self._duracion > 0

    def describir(self):
        return f"Reserva [{self.id}] {self._cliente.nombre} -> {self._servicio.nombre} | Dur: {self._duracion} | Cant: {self._cantidad} | ${self._costo_total} | Estado: {self._estado}"

# ============================================================
# 8. SISTEMA PRINCIPAL - Listas, sin BD
# ============================================================
class SistemaSoftwareFJ:
    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def registrar_cliente(self, cliente):
        try:
            cliente.validar()
            if any(c.id == cliente.id for c in self.clientes):
                raise OperacionNoPermitidaError(f"Cliente {cliente.id} ya existe")
            self.clientes.append(cliente)
        except (DatosInvalidosError, OperacionNoPermitidaError) as e:
            log_error(f"Registro cliente fallido: {e}")
            raise
        else:
            log_info(f"Cliente registrado: {cliente.describir()}")
            return True
        finally:
            logging.info(f"Intento registrar cliente {cliente.id}")

    def agregar_servicio(self, servicio):
        try:
            servicio.validar()
            self.servicios.append(servicio)
        except Exception as e:
            log_error(f"Agregar servicio fallido: {e}")
            raise ServicioNoDisponibleError("No se pudo agregar servicio") from e
        else:
            log_info(f"Servicio agregado: {servicio.describir()}")
            return True

    def crear_reserva(self, id_reserva, cliente, servicio, duracion, cantidad=1):
        try:
            reserva = Reserva(id_reserva, cliente, servicio, duracion, cantidad)
            reserva.confirmar()
            self.reservas.append(reserva)
            return reserva
        except Exception as e:
            log_error(f"Crear reserva {id_reserva} fallida: {e}")
            return None  # No se cae el sistema
        finally:
            logging.info(f"Proceso crear_reserva {id_reserva} finalizado")

    def listar_todo(self):
        print("\n--- CLIENTES ---")
        for c in self.clientes:
            print(c.describir())
        print("\n--- SERVICIOS (Polimorfismo) ---")
        for s in self.servicios:
            print(s.describir())
            print(f"   Costo 2h: ${s.calcular_costo_base(2)} | Con descuento+impuesto: ${s.calcular_costo(2, descuento=0.1, impuesto=0.19)}")
        print("\n--- RESERVAS ---")
        for r in self.reservas:
            print(r.describir())

# ============================================================
# 9. SIMULACIÓN - 12 OPERACIONES
# ============================================================
def main():
    print("=" * 65)
    print(" SOFTWARE FJ - Sistema Integral")
    print("=" * 65)
    sistema = SistemaSoftwareFJ()

    # 1. Cliente válido
    print("\n[1] Cliente válido")
    try:
        c1 = Cliente("C001", "Felipe Jaramillo", "felipe@email.com", "3001234567", "1012345678")
        sistema.registrar_cliente(c1)
    except Exception as e:
        print(f"Error: {e}")

    # 2. Cliente inválido - correo
    print("\n[2] Cliente inválido - correo malo")
    try:
        c_malo = Cliente("C002", "Ana", "correo-mal", "123", "12")
        sistema.registrar_cliente(c_malo)
    except DatosInvalidosError as e:
        print(f"✓ Error controlado, sistema sigue: {e}")
    finally:
        print("Op 2 cerrada (finally)")

    # 3. Cliente válido 2
    print("\n[3] Cliente válido 2")
    try:
        c2 = Cliente("C003", "Laura Torres", "laura@fj.com", "3109876543", "1098765432")
        sistema.registrar_cliente(c2)
    except Exception as e:
        print(e)

    # 4. Sala válida
    print("\n[4] Servicio Sala")
    try:
        sala = ReservaSala("S001", "Sala Reuniones A", 50000, capacidad=12, tiene_proyector=True)
        sistema.agregar_servicio(sala)
    except Exception as e:
        print(e)

    # 5. Equipo válido
    print("\n[5] Servicio Equipo")
    try:
        equipo = AlquilerEquipo("S002", "Portátil HP", 80000, stock=5, tipo_equipo="Computo")
        sistema.agregar_servicio(equipo)
    except Exception as e:
        print(e)

    # 6. Asesoría válida
    print("\n[6] Servicio Asesoría")
    try:
        asesoria = Asesoria("S003", "Asesoría Python", 120000, especialista="Ing. Jaramillo", nivel="Avanzado")
        sistema.agregar_servicio(asesoria)
    except Exception as e:
        print(e)

    # 7. Servicio inválido - precio negativo
    print("\n[7] Servicio inválido - precio negativo")
    try:
        malo = ReservaSala("S004", "Sala Mala", -1000, capacidad=5)
        sistema.agregar_servicio(malo)
    except Exception as e:
        print(f"✓ Error controlado: {e} | Causa: {e.__cause__}")

    # 8. Reserva exitosa
    print("\n[8] Reserva exitosa")
    r1 = sistema.crear_reserva("R001", c1, sala, duracion=3)
    if r1:
        print(f"✓ {r1.describir()}")

    # 9. Reserva fallida - duración 0
    print("\n[9] Reserva fallida - duración 0")
    r2 = sistema.crear_reserva("R002", c1, sala, duracion=0)
    print(f"Resultado: {r2} (None = falló pero sistema sigue)")

    # 10. Reserva fallida - stock
    print("\n[10] Reserva fallida - stock insuficiente")
    try:
        r3 = Reserva("R003", c2, equipo, duracion=2, cantidad=10)
        r3.confirmar()
    except Exception as e:
        print(f"✓ Error controlado: {e} | Causa: {e.__cause__}")
    else:
        print("Esto solo sale si NO hubo error")
    finally:
        print("Op 10 cerrada")

    # 11. Reserva + procesar + cancelar bloqueada
    print("\n[11] Reserva Asesoría + procesar + cancelar bloqueada")
    r4 = sistema.crear_reserva("R004", c2, asesoria, duracion=2)
    if r4:
        try:
            r4.procesar()
            print(f"Procesada: {r4.describir()}")
            r4.cancelar()  # Debe fallar
        except OperacionNoPermitidaError as e:
            print(f"✓ Cancelación bloqueada: {e}")

    # 12. Sobrecarga
    print("\n[12] Sobrecarga calcular_costo()")
    try:
        print(f"Base: ${sala.calcular_costo(2)}")
        print(f"Con descuento: ${sala.calcular_costo(2, descuento=0.1)}")
        print(f"Con descuento+impuesto: ${sala.calcular_costo(2, descuento=0.1, impuesto=0.19)}")
        print(f"Con cantidad: ${equipo.calcular_costo(2, cantidad=3)}")
        print(f"Descuento inválido: {sala.calcular_costo(2, descuento=1.5)}")
    except CalculoError as e:
        print(f"✓ Cálculo inválido controlado: {e} | Causa: {e.__cause__}")

    # Resumen
    sistema.listar_todo()
    print("\n" + "=" * 65)
    print("FIN - Sistema siguió funcionando a pesar de los errores.")
    print("Revisa sistema.log")
    print("=" * 65)

if __name__ == "__main__":
    main()