<p align="center">
  <b>#TO BE USED IN CONTROLLED ENVIRONMENTS ONLY#<b>
</p>

<p align="center">
Symbiote is a social engineering tool designed to create a phishing page and capture webcam images. By requesting camera permission on the victim's device, this script can take pictures covertly. If you're interested in contributing to the project, we'd love to have you on board.
</p>

---

# SYMBIOTE (edición educativa modificada)

Versión mínima y estable, adaptada para ejecución en **ambientes controlados**
(por ejemplo, laboratorio de clase con participantes autorizados):

- **Landing "Veridia"** (`Server/www_f/index2.html`): página en español con
  cámara **frontal por defecto** y botón para alternar frontal ↔ trasera
  (con espejado automático). El botón aparece solo cuando la cámara arranca.
- **Capturas cada 2.5 s** + selfie final, enviadas a `post.php`.
- **Carpeta por IP** en `CapturedData/<IP>/` con `info.txt`:
  - User-Agent parseado (navegador, sistema, tipo de dispositivo).
  - **Geolocalización por IP** (ip-api.com, 1 consulta por IP, cacheada).
  - Datos de navegador: pantalla, GPU, batería, red detallada (Mbps/ms),
    orientación, almacenamiento, origen del link (referrer), DNT, cookies.
  - **GPS condicional**: solo si el permiso de ubicación ya fue concedido
    a ese dominio (`permissions.query` silencioso); de lo contrario se
    omite sin mostrar prompt.
  - `info.txt` se refresca en cada captura (conserva la fecha de primera
    captura y la geo cacheada).
- **Opción de cámara trasera original** (`Server/www_b/index2.html`).

# REQUISITOS
* Python 3
* PHP (php-cli)
* ngrok (con tu propia cuenta; lo levantás manualmente)

# INSTALACIÓN
```
sudo apt update
sudo apt install python3 php-cli -y
# ngrok: descargar de https://ngrok.com y autenticar con tu authtoken
```

# USO
```
1) python3 symbiote.py          # Enter = aceptar / Veridia / puerto 1516
2) ngrok http 1516              # en otra terminal (o antes)
3) ENTER en el monitor          # la URL pública aparece sola (auto-detección vía API local 4040)
4) X para salir
```

**Importante:**
- Ejecutar **sin sudo** (evita archivos root-owned).
- La herramienta **no gestiona ngrok**: solo detecta su URL.
- Cámara y cambio de cámara requieren HTTPS (el túnel) o localhost.
- El GPS solo se captura si la víctima ya concedió permiso a ese dominio.

# DATOS CAPTURADOS
Cada carpeta de víctima contiene las fotos (`cam*.png`) y un `info.txt`
con el detalle completo de la sesión (ver arriba). `CapturedData/ip.txt`
acumula las IPs de las víctimas detectadas.

# LICENCIA
MIT — ver `LICENSE`. Este fork mantiene la licencia del proyecto original
(hasanfirnas/symbiote) y está pensado para ejecutarse únicamente en
**ambientes controlados** con participantes autorizados y consentimiento.
