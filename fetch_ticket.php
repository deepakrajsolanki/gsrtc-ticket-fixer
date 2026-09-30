<?php
// GSRTC Ticket Data Fetcher (IPv4 Enforced + ModSecurity Safe)
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, POST, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With");

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

$input = file_get_contents('php://input');
$json = json_decode($input, true);

$url = '';
if (!empty($json['url'])) {
    $url = trim($json['url']);
} elseif (!empty($json['b64'])) {
    $url = base64_decode(trim($json['b64']));
} elseif (!empty($_POST['url'])) {
    $url = trim($_POST['url']);
} elseif (!empty($_POST['b64'])) {
    $url = base64_decode(trim($_POST['b64']));
} elseif (!empty($_GET['b64'])) {
    $url = base64_decode(trim($_GET['b64']));
} elseif (!empty($_GET['url'])) {
    $url = trim($_GET['url']);
}

$url = trim($url);

if (empty($url) || strpos($url, 'gsrtc.in') === false) {
    http_response_code(400);
    header("Content-Type: application/json");
    echo json_encode(["error" => "Invalid URL. Please provide a valid gsrtc.in link."]);
    exit;
}

if (!preg_match('#^https?://#i', $url)) {
    $url = 'https://' . $url;
}

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
// CRITICAL: Force IPv4 because gsrtc.in advertises a dead NAT64 IPv6 prefix (64:ff9b::)
curl_setopt($ch, CURLOPT_IPRESOLVE, CURL_IPRESOLVE_V4);
curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 8);
curl_setopt($ch, CURLOPT_TIMEOUT, 15);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 0);
curl_setopt($ch, CURLOPT_ENCODING, "");
curl_setopt($ch, CURLOPT_USERAGENT, "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36");
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language: en-US,en;q=0.9',
    'Upgrade-Insecure-Requests: 1'
]);

$response = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$error = curl_error($ch);
curl_close($ch);

if ($response === false || $http_code >= 400 || strlen($response) < 100) {
    http_response_code(502);
    header("Content-Type: application/json");
    echo json_encode(["error" => "Could not reach GSRTC. " . ($error ?: "HTTP " . $http_code)]);
    exit;
}

header("Content-Type: text/html; charset=UTF-8");
echo $response;
