<?php
// Secure CORS proxy for GSRTC ticket fetching (ModSecurity-Safe)
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, POST, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type");

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

$url = '';
if (!empty($_POST['b64'])) {
    $url = base64_decode(trim($_POST['b64']));
} elseif (!empty($_GET['b64'])) {
    $url = base64_decode(trim($_GET['b64']));
} elseif (!empty($_POST['url'])) {
    $url = trim($_POST['url']);
} elseif (!empty($_GET['url'])) {
    $url = trim($_GET['url']);
}

$url = trim($url);

if (empty($url) || strpos($url, 'gsrtc.in') === false) {
    http_response_code(400);
    echo "Invalid URL. Only gsrtc.in URLs are allowed.";
    exit;
}

if (!preg_match('#^https?://#i', $url)) {
    $url = 'https://' . $url;
}

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($ch, CURLOPT_TIMEOUT, 30);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 0);
curl_setopt($ch, CURLOPT_USERAGENT, "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36");
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language: en-US,en;q=0.9',
    'Cache-Control: no-cache',
    'Pragma: no-cache'
]);

$response = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$error = curl_error($ch);
curl_close($ch);

if ($response === false || $http_code >= 400) {
    http_response_code(502);
    echo "Failed to fetch ticket from GSRTC. HTTP: " . htmlspecialchars($http_code . " " . $error);
    exit;
}

header("Content-Type: text/html; charset=UTF-8");
echo $response;
