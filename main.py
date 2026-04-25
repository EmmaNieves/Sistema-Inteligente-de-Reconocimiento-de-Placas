from database import save_plate
from camera_capture import detect_plate_from_camera, show_camera_live

if __name__ == '__main__':
    print('Sistema de Reconocimiento de Placas con YOLOv8')
    print('=' * 60)
    print('1. Capturar una placa (modo automatico)')
    print('2. Ver camara en vivo (captura manual con "c")')
    print('=' * 60)

    modo = input('Selecciona modo (1/2): ').strip()

    if modo == '2':
        print('\nIniciando camara en vivo...')
        plates = show_camera_live()

        if plates:
            print(f'\nSe capturaron {len(plates)} placa(s) durante la sesion:')
            for plate_text, frame in plates:
                is_new = save_plate(plate_text, frame)
                if is_new:
                    print(f'  PLACA NUEVA guardada  -> {plate_text}')
                else:
                    print(f'  Placa YA EXISTE       -> {plate_text}')
        else:
            print('No se capturaron placas en esta sesion.')

    else:
        while True:
            plate_text, frame = detect_plate_from_camera()

            if plate_text:
                is_new = save_plate(plate_text, frame)

                if is_new:
                    print(f'PLACA NUEVA guardada! -> {plate_text}')
                else:
                    print(f'Placa YA EXISTE en la base de datos -> {plate_text}')

                print('-' * 60)

            respuesta = input('Quieres capturar otra placa? (s/n): ').strip().lower()
            if respuesta != 's':
                print('Hasta luego!')
                break
