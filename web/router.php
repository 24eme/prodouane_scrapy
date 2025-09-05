<?php
include('../bin/config.php');

const SCRAPING_FILE_NOT_FOUND = 666;

if (!isset($_SERVER['PHP_AUTH_USER']) || !$_SERVER['PHP_AUTH_USER'] || (strpos($_SERVER['REMOTE_ADDR'], '10.20') === false && strpos($_SERVER['REMOTE_ADDR'], '127.') === false && strpos($_SERVER['REMOTE_ADDR'], '::1') === false) ) {
	header('WWW-Authenticate: Basic realm="My Realm"');
	header('HTTP/1.0 401 Unauthorized');
	exit;
}
$account_name = $_SERVER['PHP_AUTH_USER'];
if (!isset($_GET['cvi'])) {
	header('HTTP/1.0 400 Bad Request');
	echo "argument cvi nécessaire\n";
	exit;
}
$cvi = $_GET['cvi'];
$cvi = preg_replace('/[^0-9A-Z]/', '', $cvi);
$dep = substr($cvi, 0, 2);

$millesime = date('Y');
if (isset($_GET['millesime'])) {
	$millesime = substr(preg_replace('/[^0-9]/', '', $_GET['millesime']), 0, 4);
}

if (!isset($_GET['type'])) {
	header('HTTP/1.0 400 Bad Request');
	echo "argument type nécessaire\n";
	exit;
}
$type = $_GET['type'];

if (!isset($_GET['action'])) {
	header('HTTP/1.0 400 Bad Request');
	echo "argument action nécessaire\n";
	exit;
}
$action = $_GET['action'];
$config_dep_to_region[$dep][] = 'default';

$page = json_encode(['error_code' => -1, 'msg' => 'no region found '.$dep]);
foreach($config_dep_to_region[$dep] as $region) {
	if ($region == $account_name) {
		continue;
	}
	if(!isset($config_instance_uri[$region])) {
		continue;
	}
	$url = $config_instance_uri[$region];
	$query = $url.'/api.php?action='.$action.'&format=json&localonly=true&type='.$type.'&cvi='.$cvi.'&millesime='.$millesime;
	error_log('router: '.$account_name.': '.$query);
	if (isset($_GET['filename'])) {
		$query .= "&filename=".$_GET['filename'];
	}
	$page = file_get_contents($query);
	$ret = json_decode($page);
	if ($ret && !isset($ret->error_code)) {
		echo $page;
		exit;
	}
}
echo $page;
