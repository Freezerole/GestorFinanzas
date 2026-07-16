"""
main.py — Punto de entrada del Sistema de Gestión Financiera.

Menú CLI que integra Gestor (lógica y balances) y Storage (persistencia JSON).
Filosofía del proyecto: código simple, sin abstracciones innecesarias,
guardado tras cada operación para no depender de un cierre limpio.
"""

from class_gestor import Gestor


MENU = """
============================================
   GESTIÓN FINANCIERA PERSONAL
============================================
 1. Añadir operación (ingreso / gasto)
 2. Ver balance actual
 3. Ver balance proyectado (a futuro)
 4. Ver todas las operaciones
 5. Filtrar / buscar operaciones
 6. Eliminar una operación
 7. Vaciar todos los datos (nuke)
 0. Guardar y salir
============================================
"""


def mostrar_balance_actual(gestor: Gestor) -> None:
    total_op, real_balance = gestor.find_true_balance()
    signo = "" if real_balance >= 0 else "-"
    print(f"\nOperaciones efectivas a día de hoy: {total_op}")
    print(f"Balance actual: {signo}{abs(real_balance):.2f}€\n")


def mostrar_balance_proyectado(gestor: Gestor) -> None:
    # find_virtual_balance(manual=True) ya pide los meses e imprime su propio resultado
    _, end_date = gestor.find_virtual_balance(manual=True)
    mostrar_desglose_movimientos(gestor, end_date)


def mostrar_desglose_movimientos(gestor, end_date, months_back: int = 2) -> None:
    breakdown = gestor.get_movement_breakdown(end_date, months_back=months_back)

    print(f"\n--- Movimientos entre {breakdown['start_date']} y {breakdown['end_date']} ---")
    print(f"Balance de partida ({breakdown['start_date']}): {breakdown['starting_balance']:.2f}€\n")

    if not breakdown["movements"]:
        print("No hay movimientos registrados en ese periodo.\n")
    else:
        for mov in breakdown["movements"]:
            signo = "+" if mov["SignedValue"] >= 0 else ""
            print(
                f"{mov['EffectiveDate']} | {mov['Concept']:<20} | "
                f"{signo}{mov['SignedValue']:.2f}€ | Balance: {mov['BalanceAfter']:.2f}€"
            )
        print()

    print(f"Balance final ({breakdown['end_date']}): {breakdown['final_balance']:.2f}€\n")


def ver_todas_las_operaciones(gestor: Gestor) -> None:
    gestor.storage.view_logs(show_columns="*", reset=True)


def filtrar_operaciones(gestor: Gestor) -> None:
    print("\nFiltra por uno o varios campos (deja vacío y pulsa Enter para omitir un campo).")
    print("Campos disponibles: Concepto, Importe, IsIncome, Destinatario, Recursivo, Usuario\n")

    criteria = {}

    concepto = input("Concepto (texto exacto): ").strip()
    if concepto:
        criteria["Concepto"] = concepto

    importe_str = input("Importe (número exacto): ").strip()
    if importe_str:
        try:
            criteria["Importe"] = float(importe_str)
        except ValueError:
            print("Importe inválido, se omite ese filtro.")

    tipo = input("¿Ingreso o gasto? (i/g, vacío para omitir): ").strip().lower()
    if tipo == "i":
        criteria["IsIncome"] = True
    elif tipo == "g":
        criteria["IsIncome"] = False

    destinatario = input("Destinatario (texto exacto): ").strip()
    if destinatario:
        criteria["Destinatario"] = destinatario

    recursivo = input("¿Recursivo? (s/n, vacío para omitir): ").strip().lower()
    if recursivo == "s":
        criteria["Recursivo"] = True
    elif recursivo == "n":
        criteria["Recursivo"] = False

    usuario = input("Usuario (texto exacto): ").strip()
    if usuario:
        criteria["Usuario"] = usuario

    if not criteria:
        print("No se indicó ningún filtro.")
        return

    gestor.storage.reset_temp_log()
    gestor.storage.filter(**criteria)


def eliminar_operacion(gestor: Gestor) -> None:
    if not gestor.storage.data["operations"]:
        print("\nTodavía no hay operaciones registradas.\n")
        return

    id_str = input("Introduce el ID de la operación a eliminar (o 'q' para cancelar): ").strip()
    if id_str.lower() == "q":
        print("Cancelado.\n")
        return

    try:
        op_id = int(id_str)
    except ValueError:
        print("ID inválido.\n")
        return

    gestor.storage.remove_log(op_id)
    gestor.storage.save()


def nuke(gestor: Gestor) -> None:
    print("\n⚠️  Esto eliminará TODAS las operaciones guardadas de forma irreversible.")
    confirm = input("Escribe ELIMINAR (en mayúsculas) para confirmar, cualquier otra cosa cancela: ").strip()
    if confirm == "ELIMINAR":
        gestor.storage.nuke()
    else:
        print("Cancelado. No se ha borrado nada.\n")


def iniciar() -> None:
    gestor = Gestor()
    gestor.storage.load()
    print("Datos cargados correctamente.")

    acciones = {
        "1": lambda: (gestor.add_operation(), gestor.storage.save()),
        "2": lambda: mostrar_balance_actual(gestor),
        "3": lambda: mostrar_balance_proyectado(gestor),
        "4": lambda: ver_todas_las_operaciones(gestor),
        "5": lambda: filtrar_operaciones(gestor),
        "6": lambda: eliminar_operacion(gestor),
        "7": lambda: nuke(gestor),
    }

    try:
        while True:
            print(MENU)
            opcion = input("Elige una opción: ").strip()

            if opcion == "0":
                gestor.storage.save()
                print("\n¡Hasta la próxima!\n")
                break

            accion = acciones.get(opcion)
            if accion:
                accion()
            else:
                print("Opción no válida. Elige un número del menú.\n")

    except KeyboardInterrupt:
        print("\n\nInterrupción detectada. Guardando antes de salir...")
        gestor.storage.save()
        print("Datos guardados. ¡Hasta la próxima!\n")


if __name__ == "__main__":
    iniciar()
